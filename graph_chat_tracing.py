"""Opt-in, metadata-only OpenTelemetry for the Anthropic/Neo4j chat."""
from contextlib import contextmanager
import json
import logging
import os
from pathlib import Path
import tempfile
import threading

from grounding import RejectionReason


LOGGER = logging.getLogger(__name__)
PRICE_DATE = "2026-11-06"
TRACE_ENV = "BIOPROCESS_GRAPH_CHAT_TRACE"
PRICES = {"claude-sonnet-4-6": (3, 15, 0.30, 3.75, 6)}
TOKEN_FIELDS = (
    "input_tokens", "output_tokens", "cache_read_input_tokens",
    "cache_creation_input_tokens",
)
SPAN_NAMES = {"graph_chat.request", "anthropic.messages.create", "neo4j.search"}
STOP_REASONS = frozenset({
    "end_turn", "max_tokens", "stop_sequence", "tool_use", "pause_turn",
    "refusal", "model_context_window_exceeded",
})
REJECTION_REASONS = frozenset(reason.value for reason in RejectionReason)
OUTCOMES = {"answer", "refuse", "error", "matched", "no_match"}


def _warn(message):
    try:
        LOGGER.warning(message)
    except Exception:
        pass


def _count(value):
    return type(value) is int and 0 <= value <= 2**53 - 1


def usage_metadata(response, model):
    usage = getattr(response, "usage", None)
    values = {field: getattr(usage, field, None) for field in TOKEN_FIELDS}
    metadata = {f"usage.{field}": value for field, value in values.items() if _count(value)}
    reason = getattr(response, "stop_reason", None)
    if type(reason) is str and reason in STOP_REASONS:
        metadata["gen_ai.response.stop_reason"] = reason
    if model not in PRICES or not all(_count(values[f]) for f in TOKEN_FIELDS[:2]):
        return metadata
    cache_read, cache_write = (0 if values[f] is None else values[f] for f in TOKEN_FIELDS[2:])
    if not _count(cache_read) or not _count(cache_write):
        return metadata
    cache = getattr(usage, "cache_creation", None)
    five = getattr(cache, "ephemeral_5m_input_tokens", None)
    hour = getattr(cache, "ephemeral_1h_input_tokens", None)
    if not cache_write:
        five = hour = 0
    elif not (_count(five) and _count(hour) and five + hour == cache_write):
        return metadata
    geo = getattr(usage, "inference_geo", None)
    if geo not in (None, "global", "us"):
        return metadata
    if geo is not None:
        metadata["usage.inference_geo"] = geo
    multiplier = 1.1 if geo == "us" else 1
    rates = PRICES[model]
    counts = (values["input_tokens"], values["output_tokens"], cache_read, five, hour)
    metadata["cost.estimated_usd"] = round(sum(n * rate for n, rate in zip(counts, rates)) * multiplier / 1e6, 12)
    metadata["cost.pricing_date"] = PRICE_DATE
    return metadata


def _permitted(key, value):
    if key == "grounding.rejection_reason":
        return type(value) is str and value in REJECTION_REASONS
    if key == "gen_ai.response.stop_reason":
        return type(value) is str and value in STOP_REASONS
    if key == "usage.inference_geo":
        return type(value) is str and value in ("global", "us")
    if key.startswith("usage."):
        return key[6:] in TOKEN_FIELDS and _count(value)
    if key == "gen_ai.request.model":
        return type(value) is str and value in PRICES
    if key == "outcome":
        return type(value) is str and value in OUTCOMES
    if key == "cost.pricing_date":
        return value == PRICE_DATE
    if key == "cost.estimated_usd":
        return type(value) is float and 0 <= value < float("inf")
    return False


class _Span:
    def __init__(self, raw=None):
        self.raw = raw

    def attributes(self, **values):
        if self.raw is not None:
            try:
                for key, value in values.items():
                    if _permitted(key, value):
                        self.raw.set_attribute(key, value)
            except Exception:
                pass

    def failed(self):
        if self.raw is not None:
            try:
                from opentelemetry.trace import Status, StatusCode
                self.raw.set_status(Status(StatusCode.ERROR))
            except Exception:
                pass


@contextmanager
def span(tracer, name, parent=None):
    raw = None
    if tracer is not None and name in SPAN_NAMES:
        try:
            from opentelemetry.context import Context
            from opentelemetry.trace import SpanKind, set_span_in_context
            context = Context()
            if parent is not None and parent.raw is not None:
                context = set_span_in_context(parent.raw, context)
            raw = tracer.start_span(name, context=context,
                                    kind=SpanKind.INTERNAL if parent is None else SpanKind.CLIENT)
        except Exception:
            pass
    observed = _Span(raw)
    try:
        yield observed
    except BaseException:
        observed.failed()
        raise
    finally:
        if raw is not None:
            try:
                raw.end()
            except Exception:
                pass


class _FileExporter:
    def __init__(self, stream):
        self.stream = stream
        self.failed = False

    def export(self, spans):
        from opentelemetry.sdk.trace.export import SpanExportResult
        try:
            for item in spans:
                if item.name not in SPAN_NAMES:
                    continue
                row = {
                    "schema": "graph-chat-trace/v1", "name": item.name,
                    "trace_id": f"{item.context.trace_id:032x}",
                    "span_id": f"{item.context.span_id:016x}",
                    "parent_span_id": f"{item.parent.span_id:016x}" if item.parent else None,
                    "start_time_unix_nano": item.start_time,
                    "duration_ms": (item.end_time - item.start_time) / 1e6,
                    "status": item.status.status_code.name,
                    "attributes": {k: v for k, v in item.attributes.items() if _permitted(k, v)},
                }
                self.stream.write(json.dumps(row, allow_nan=False) + "\n")
            self.stream.flush()
            return SpanExportResult.SUCCESS
        except Exception:
            if not self.failed:
                self.failed = True
                _warn("Graph chat trace export failed; chat remains enabled")
            return SpanExportResult.FAILURE

    def shutdown(self):
        try:
            self.stream.close()
        except Exception:
            pass


def _provider(stream):
    from opentelemetry.metrics import NoOpMeterProvider
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import SpanLimits, TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.trace.sampling import ALWAYS_ON

    meter = NoOpMeterProvider()
    provider = TracerProvider(
        resource=Resource({"service.name": "bioprocess-graph-chat"}), sampler=ALWAYS_ON,
        shutdown_on_exit=False, meter_provider=meter, span_limits=SpanLimits(
            max_attributes=12, max_events=0, max_links=0, max_attribute_length=64),
    )
    provider.add_span_processor(BatchSpanProcessor(
        _FileExporter(stream), max_queue_size=256, max_export_batch_size=32,
        schedule_delay_millis=500, meter_provider=meter,
    ))
    return provider


def _shutdown(provider):
    def close():
        try:
            provider.shutdown()
        except Exception:
            pass
    try:
        worker = threading.Thread(target=close, daemon=True)
        worker.start()
        worker.join(1)
    except Exception:
        pass


def _initialize():
    import atexit
    stream = provider = None
    try:
        folder = Path(__file__).resolve().parent / "tmp" / "graph-chat-traces"
        folder.mkdir(parents=True, exist_ok=True)
        stream = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=folder,
            prefix="graph-chat-", suffix=".jsonl", delete=False,
        )
        provider = _provider(stream)
        tracer = provider.get_tracer("bioprocess.graph_chat", "1")
        atexit.register(_shutdown, provider)
        return tracer
    except Exception:
        if provider is not None:
            _shutdown(provider)
        elif stream is not None:
            _FileExporter(stream).shutdown()
        _warn("Graph chat tracing unavailable; chat remains enabled")
        return None


class _LocalTracer:
    def __init__(self):
        self.tracer = None
        self._start_lock = threading.Lock()
        self._started = False

    def _initialize_in_background(self):
        self.tracer = _initialize()

    def get(self):
        if not self._started and self._start_lock.acquire(blocking=False):
            try:
                if not self._started:
                    self._started = True
                    threading.Thread(target=self._initialize_in_background, daemon=True).start()
            except Exception:
                _warn("Graph chat trace startup failed; chat remains enabled")
            finally:
                self._start_lock.release()
        # Never wait for SDK initialization or file I/O. Capture a whole trace
        # or none of it, even if the worker becomes ready during the request.
        return self.tracer


_local = _LocalTracer()


def local_tracer():
    return _local.get() if os.environ.get(TRACE_ENV) == "1" else None
