"""Optional, local-only manual OTel instrumentation; no global provider or payload capture."""
from contextlib import contextmanager
from contextvars import ContextVar
import http.client
import ipaddress
import json
import logging
from pathlib import Path
import re
import threading
from urllib.parse import urlsplit

LOGGER = logging.getLogger(__name__)
RESOURCE = {"service.name": "bioprocess-registry-ui-v02",
            "bioprocess.trace_schema": "registry-ui/v1"}
SOURCE_ROUTE = "/reviewed/v1/releases/{release_id}/sources/{source_id}"
SOURCE_PATTERN = r"/reviewed/v1/releases/[A-Za-z0-9._-]+/sources/[A-Za-z0-9._-]+"
OUTCOMES = {"supported", "partial", "needs_clarification", "abstained", "quarantined",
            "unavailable", "excluded", "available", "invalid_request", "unknown"}
ERRORS = {"operation_failed", "registry_unavailable", "http_server_error"}


def warn(message):
    try:
        LOGGER.warning(message)
    except Exception:
        pass


def route(path):
    if path in ("/", "/api/reviewed/v1/evaluate"):
        return path
    return SOURCE_ROUTE if re.fullmatch(SOURCE_PATTERN, path) else "unmatched"


def permitted(name, value):
    """A closed metadata vocabulary; never stringify arbitrary input."""
    if name == "http.request.method":
        return value in ("GET", "POST")
    if name == "http.route":
        return value in ("/", "/api/reviewed/v1/evaluate", SOURCE_ROUTE, "unmatched")
    if name == "http.response.status_code":
        return type(value) is int and 100 <= value <= 599
    if name == "bioprocess.outcome":
        return type(value) is str and value in OUTCOMES
    if name == "error.type":
        return type(value) is str and value in ERRORS
    if name in ("bioprocess.release_id", "bioprocess.source_id"):
        return type(value) is str and re.fullmatch(r"[A-Za-z0-9._-]{1,128}", value) is not None
    if name in ("bioprocess.item_count", "bioprocess.citation_count"):
        return type(value) is int and 0 <= value <= 128
    return False


class Span:
    def __init__(self, raw=None, failed=None):
        self.raw = raw
        self.failed = failed or (lambda phase: None)

    def attributes(self, values):
        if self.raw is None:
            return
        for name, value in values.items():
            try:
                if permitted(name, value):
                    self.raw.set_attribute(name, value)
            except Exception:
                self.failed("attributes")

    def error(self, category):
        self.attributes({"error.type": category})
        try:
            if self.raw is not None:
                from opentelemetry.trace import Status, StatusCode
                self.raw.set_status(Status(StatusCode.ERROR))  # No exception text/stack.
        except Exception:
            self.failed("status")

    def trace_id(self):
        if self.raw is None:
            return None
        try:
            context = self.raw.get_span_context()
            return f"{context.trace_id:032x}" if context.is_valid else None
        except Exception:
            self.failed("context")
            return None

    def end(self):
        try:
            if self.raw is not None:
                self.raw.end()
        except Exception:
            self.failed("end")


class Tracing:
    def __init__(self, tracer=None, provider=None):
        self.tracer = tracer
        self.provider = provider
        self._current = ContextVar("registry_local_trace", default=None)
        self.export_failures = 0
        self.sdk_failures = {}
        self._health_lock = threading.Lock()

    def sdk_failed(self, phase):
        # Closed vocabulary: never include SDK messages or request content.
        if phase not in {"start", "attributes", "status", "context", "end"}:
            return
        with self._health_lock:
            self.sdk_failures[phase] = self.sdk_failures.get(phase, 0) + 1
            first = self.sdk_failures[phase] == 1
        if first:
            warn("Local trace SDK failure (" + phase + "); answers remain enabled")

    def export_failed(self):
        with self._health_lock:
            self.export_failures += 1
            first = self.export_failures == 1
        if first:
            warn("Local trace export failed; answers remain enabled")

    @contextmanager
    def span(self, name, *, root=False, attributes=None):
        raw = None
        if self.tracer is not None:
            try:
                from opentelemetry.context import Context
                from opentelemetry.trace import SpanKind, set_span_in_context
                parent = self._current.get()
                context = Context()
                if not root and parent is not None and parent.raw is not None:
                    context = set_span_in_context(parent.raw, context)
                # Do not extract incoming traceparent/baggage or use ambient context.
                raw = self.tracer.start_span(
                    name, context=context,
                    kind=SpanKind.SERVER if root else SpanKind.INTERNAL)
            except Exception:
                self.sdk_failed("start")
        span = Span(raw, self.sdk_failed)
        span.attributes(attributes or {})
        token = self._current.set(span)
        try:
            yield span
        except BaseException:
            span.error("operation_failed")
            raise  # Telemetry must not swallow or retry a business operation.
        finally:
            self._current.reset(token)
            span.end()

    def current(self):
        return self._current.get() or Span()

    def flush(self, timeout_ms=1000):
        try:
            return self.provider.force_flush(timeout_millis=timeout_ms) if self.provider else True
        except Exception:
            return False

    def close(self, timeout=1):
        """Bound cleanup too: a stalled exporter must not hang server shutdown."""
        if self.provider is None:
            return
        done = threading.Event()
        def shutdown():
            try:
                self.provider.shutdown()
            except Exception:
                pass
            finally:
                done.set()
        threading.Thread(target=shutdown, daemon=True).start()
        done.wait(timeout)


def metadata(result, *, source=False):
    status = result.get("status", "unknown")
    if result.get("kind") == "reviewed_serving_validation_error/v1":
        status = "invalid_request"
    values = {"bioprocess.outcome": status, "bioprocess.release_id": result.get("release_id")}
    if source:
        passage = result.get("passage")
        if isinstance(passage, dict):
            values["bioprocess.source_id"] = passage.get("source_id")
    else:
        values["bioprocess.item_count"] = len(result.get("items", []))
        values["bioprocess.citation_count"] = len(result.get("citation_refs", []))
    return values


class ObservedRegistry:
    """Pass-through only. Retain baseline authority/source error handling."""
    def __init__(self, registry, tracing):
        self.registry = registry
        self.tracing = tracing

    def __getattr__(self, name):
        return getattr(self.registry, name)

    def _call(self, operation, args, kwargs):
        parent = self.tracing.current()
        with self.tracing.span("registry." + operation) as span:
            result = getattr(self.registry, operation)(*args, **kwargs)
            try:
                values = metadata(result, source=operation == "source")
                span.attributes(values)
                parent.attributes(values)
                if result.get("status") == "unavailable":
                    span.error("registry_unavailable")
                    parent.error("registry_unavailable")
            except Exception:
                pass  # Metadata extraction cannot replace a successful response.
            return result

    def evaluate(self, *args, **kwargs):
        return self._call("evaluate", args, kwargs)

    def source(self, *args, **kwargs):
        return self._call("source", args, kwargs)


class JsonLinesExporter:
    """New file only; neither overwrite nor append to existing application data."""
    def __init__(self, filename):
        self.stream = Path(filename).open("x", encoding="utf-8", newline="\n")

    def export(self, spans):
        from opentelemetry.sdk.trace.export import SpanExportResult
        for span in spans:
            data = {"schema": "registry-trace/v1", "name": span.name,
                    "trace_id": f"{span.context.trace_id:032x}",
                    "span_id": f"{span.context.span_id:016x}",
                    "parent_span_id": f"{span.parent.span_id:016x}" if span.parent else None,
                    "kind": span.kind.name, "start_time_unix_nano": span.start_time,
                    "end_time_unix_nano": span.end_time,
                    "duration_ms": (span.end_time - span.start_time) / 1_000_000,
                    "status": span.status.status_code.name, "resource": RESOURCE,
                    "attributes": {k: v for k, v in span.attributes.items() if permitted(k, v)}}
            self.stream.write(json.dumps(data, ensure_ascii=False) + "\n")
        self.stream.flush()
        return SpanExportResult.SUCCESS

    def shutdown(self):
        self.stream.close()


class LocalOTLPExporter:
    """Standard OTLP protobuf, one bounded attempt; literal loopback only."""
    def __init__(self, endpoint):
        url = urlsplit(endpoint)
        if (url.scheme != "http" or url.username or url.password or url.query or url.fragment
                or url.path != "/v1/traces" or not ipaddress.ip_address(url.hostname).is_loopback):
            raise ValueError("Use a literal loopback OTLP/HTTP endpoint ending in /v1/traces")
        self.host, self.port = url.hostname, url.port or 80
        if url.port is not None and not 1 <= url.port <= 65535:
            raise ValueError("Invalid local collector port")

    def export(self, spans):
        from opentelemetry.exporter.otlp.proto.common.trace_encoder import encode_spans
        from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceResponse
        from opentelemetry.sdk.trace.export import SpanExportResult
        payload = encode_spans(spans).SerializeToString()
        # http.client ignores proxy/header env vars and does not follow redirects.
        connection = http.client.HTTPConnection(self.host, self.port, timeout=1)
        try:
            connection.request("POST", "/v1/traces", payload,
                               {"Content-Type": "application/x-protobuf"})
            response = connection.getresponse()
            if response.status != 200:
                return SpanExportResult.FAILURE
            body = response.read(65537)
            if len(body) > 65536:
                return SpanExportResult.FAILURE
            decoded = ExportTraceServiceResponse.FromString(body)
            return (SpanExportResult.FAILURE if decoded.partial_success.rejected_spans
                    else SpanExportResult.SUCCESS)
        finally:
            connection.close()

    def shutdown(self):
        pass


class SafeExporter:
    def __init__(self, exporter, tracing):
        self.exporter = exporter
        self.tracing = tracing

    def export(self, spans):
        from opentelemetry.sdk.trace.export import SpanExportResult
        try:
            result = self.exporter.export(spans)
        except Exception:
            result = SpanExportResult.FAILURE
        if result != SpanExportResult.SUCCESS:
            self.tracing.export_failed()
        return result

    def shutdown(self):
        try:
            self.exporter.shutdown()
        except Exception:
            pass


def close_partial(resource, timeout=1):
    """Clean up an unregistered sink without blocking application startup."""
    done = threading.Event()
    def shutdown():
        try:
            resource.shutdown()
        except Exception:
            pass
        finally:
            done.set()
    threading.Thread(target=shutdown, daemon=True).start()
    done.wait(timeout)


def configure(*, trace_file=None, otlp_endpoint=None, protected_root=None, exporters=()):
    """No SDK imports when disabled; no auto configuration or global provider."""
    tracing = Tracing()
    if trace_file is None and otlp_endpoint is None and not exporters:
        return tracing
    try:
        from opentelemetry.metrics import NoOpMeterProvider
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider, SpanLimits
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.trace.sampling import ALWAYS_ON
        provider = TracerProvider(
            resource=Resource(RESOURCE), sampler=ALWAYS_ON, shutdown_on_exit=False,
            meter_provider=NoOpMeterProvider(),
            span_limits=SpanLimits(max_attributes=16, max_events=0, max_links=0,
                                   max_attribute_length=128))
        tracing.provider = provider
        factories = [lambda e=e: e for e in exporters]
        if trace_file is not None:
            def file_sink():
                path = Path(trace_file).resolve()
                if protected_root is not None and path.is_relative_to(Path(protected_root).resolve()):
                    raise ValueError("Trace files must be outside the authority directory")
                return JsonLinesExporter(path)
            factories.append(file_sink)
        if otlp_endpoint is not None:
            factories.append(lambda: LocalOTLPExporter(otlp_endpoint))
        sinks = 0
        for factory in factories:
            exporter = processor = None
            try:
                exporter = SafeExporter(factory(), tracing)
                processor = BatchSpanProcessor(
                    exporter, max_queue_size=256, max_export_batch_size=32,
                    schedule_delay_millis=1000, export_timeout_millis=1000,
                    meter_provider=NoOpMeterProvider())
                provider.add_span_processor(processor)
                sinks += 1
            except Exception:
                if processor is not None or exporter is not None:
                    close_partial(processor if processor is not None else exporter)
                warn("A local trace sink is unavailable; answers remain enabled")
        if not sinks:
            tracing.close()
            return Tracing()
        tracing.tracer = provider.get_tracer("bioprocess.registry_ui", "1")
    except Exception:
        warn("Local tracing unavailable; answers remain enabled")
        tracing.close()
        return Tracing()
    return tracing
