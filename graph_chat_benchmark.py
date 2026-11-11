"""Run the reviewed graph chat benchmark against an explicitly supplied client."""
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from agent import run_agent
from graph_chat_budget import BenchmarkLimitError, GraphChatBudget
from graph_chat_tracing import _provider

ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "docs" / "GRAPH-CHAT-MEASUREMENT.md"
CASE_IDS = ("G01", "G02", "G03", "G04")
HELD_OUT_REVIEW = ROOT / "docs" / "GRAPH-CHAT-HELD-OUT-REVIEW.md"
HELD_OUT_CASE_IDS = tuple(f"H{i:02}" for i in range(1, 9))
HELD_OUT_PAYLOAD_SHA256 = "4bd9ffc410f696900718a26d63c820a8b4ee1c4932d95ffcdcb9d3a11683d0a9"
HELD_OUT_SEED_SHA256 = "9d95f426fb92cc718712bca99694c886201a32c124838f4a2351bf75b942d6ed"
FIRST_RUN_RESERVE_USD = Decimal("0.399168")
RETRY_MAX_OUTPUT = 1536
STRUCTURED_REPLAY_CEILING_USD = Decimal("1.01")
PRESSURE_PROTOCOL = ROOT / "docs" / "validation" / "GRAPH-CHAT-PRESSURE-VALIDATION.md"
PRESSURE_CEILING_USD = Decimal("0.76")
PRESSURE_PROTOCOL_SHA256 = "00874796f6b43fbf6250a5f979dfdbde4a3ee44297f993b93650745550955a9c"
G02_PROMPT_SHA256 = "f1a94eea650918e0f918da22e54535b6b9b775b867911354f00672963393d2f9"


def run_targeted_retry(client, *, output_dir=None, simulated=False):
    """Repeat G01 and G02 twice against the remainder of the original ceiling."""
    return run_benchmark(client, output_dir=output_dir, simulated=simulated,
                         case_ids=("G01", "G02"), max_output=RETRY_MAX_OUTPUT,
                         prior_reserved_usd=FIRST_RUN_RESERVE_USD)


def run_structured_replay(client, *, output_dir=None, simulated=False):
    """Run both G01–G04 passes under the separate structured-output budget."""
    return run_benchmark(client, output_dir=output_dir, simulated=simulated,
                         max_output=RETRY_MAX_OUTPUT, ceiling_usd=STRUCTURED_REPLAY_CEILING_USD)


def run_held_out(client, *, output_dir=None, simulated=False):
    """Run one pass of the frozen H01–H08 set with a fresh USD 1.01 budget."""
    return _run_questions(
        client, _held_out_questions(), output_dir=output_dir, simulated=simulated,
        passes=1, max_output=1536, max_calls=3, ceiling_usd=STRUCTURED_REPLAY_CEILING_USD,
        prior_reserved_usd=Decimal("0"),
    )


def run_pressure_validation(client, *, output_dir=None, simulated=False):
    """Run the six reviewed pressure cases once under their separate ceiling."""
    questions = _pressure_questions()
    return _run_questions(
        client, questions, output_dir=output_dir, simulated=simulated,
        passes=1, max_output=RETRY_MAX_OUTPUT, max_calls=3,
        ceiling_usd=PRESSURE_CEILING_USD, prior_reserved_usd=Decimal("0"),
    )


def _pressure_questions():
    protocol = PRESSURE_PROTOCOL.read_text(encoding="utf-8-sig")
    _, start, tail = protocol.partition("## Proposed targeted run\n")
    body, end, _ = tail.partition("\n## Proposed budget\n")
    if not start or not end or sha256(body.encode("utf-8")).hexdigest() != PRESSURE_PROTOCOL_SHA256:
        raise ValueError("Pressure protocol does not match its approved digest")

    h08 = dict(_held_out_questions())["H08"]
    g02 = dict(reviewed_questions())["G02"]
    if sha256(g02.encode("utf-8")).hexdigest() != G02_PROMPT_SHA256:
        raise ValueError("G02 prompt does not match its approved digest")
    variants = []
    for line in body.splitlines():
        if line.startswith("| P"):
            _, case, question, *_ = line.split("|")
            variants.append((case.strip(), question.strip()))
    if tuple(case for case, _ in variants) != ("P01", "P02", "P03", "P04"):
        raise ValueError("Pressure protocol must contain P01–P04 in order")
    return [("H08", h08), ("G02", g02), *variants]


def _held_out_questions():
    review = HELD_OUT_REVIEW.read_text(encoding="utf-8")
    start = "## Questions and expected results\n"
    end = "\n## Review decision and freeze\n"
    _, marker, rest = review.partition(start)
    body, boundary, _ = rest.partition(end)
    payload = (marker + body).rstrip() + "\n"
    if not marker or not boundary or sha256(payload.encode("utf-8")).hexdigest() != HELD_OUT_PAYLOAD_SHA256:
        raise ValueError("Frozen H01–H08 payload does not match its approved digest")
    seed = (ROOT / "graph" / "seed.cypher").read_bytes().replace(b"\r\n", b"\n")
    if sha256(seed).hexdigest() != HELD_OUT_SEED_SHA256:
        raise ValueError("Graph seed does not match the H01–H08 freeze")
    questions = []
    for line in body.splitlines():
        if line.startswith("| H") and line.split("|")[1].strip() in HELD_OUT_CASE_IDS:
            _, case, _, question, *_ = line.split("|")
            questions.append((case.strip(), question.strip()))
    if tuple(case for case, _ in questions) != HELD_OUT_CASE_IDS or not all(q for _, q in questions):
        raise ValueError("The frozen review must contain H01–H08 in order")
    return questions


def reviewed_questions():
    questions = []
    for line in PROTOCOL.read_text(encoding="utf-8").splitlines():
        if line.startswith("| G"):
            _, case, question, *_ = line.split("|")
            if case.strip() in CASE_IDS:
                questions.append((case.strip(), question.strip()))
    if tuple(case for case, _ in questions) != CASE_IDS or not all(q for _, q in questions):
        raise ValueError("The protocol must contain G01–G04 in order")
    return questions


def run_benchmark(client, *, output_dir=None, simulated=False, case_ids=CASE_IDS,
                  max_output=GraphChatBudget.MAX_OUTPUT, prior_reserved_usd=Decimal("0"), passes=2,
                  max_calls=GraphChatBudget.MAX_CALLS, ceiling_usd=GraphChatBudget.CEILING_USD):
    """Use one budget and one initialized local trace exporter for the selected passes."""
    if type(passes) is not int or not 1 <= passes <= 2:
        raise ValueError("Invalid benchmark pass count")
    reviewed = dict(reviewed_questions())
    if not case_ids or len(set(case_ids)) != len(case_ids) or any(c not in reviewed for c in case_ids):
        raise ValueError("Invalid reviewed case selection")
    questions = [(case, reviewed[case]) for case in case_ids]
    return _run_questions(
        client, questions, output_dir=output_dir, simulated=simulated, passes=passes,
        max_output=max_output, max_calls=max_calls, ceiling_usd=ceiling_usd,
        prior_reserved_usd=prior_reserved_usd,
    )


def _run_questions(client, questions, *, output_dir, simulated, passes, max_output,
                   max_calls, ceiling_usd, prior_reserved_usd):
    budget = GraphChatBudget(client, max_output=max_output, prior_reserved_usd=prior_reserved_usd,
                            max_calls=max_calls, ceiling_usd=ceiling_usd)
    worst_case = passes * len(questions) * budget.max_calls * budget.call_reserve_usd
    if prior_reserved_usd + worst_case > budget.ceiling_usd:
        raise BenchmarkLimitError("planned benchmark exceeds cumulative spend ceiling")
    output_dir = Path(output_dir) if output_dir is not None else ROOT / "tmp" / "graph-chat-traces"
    output_dir.mkdir(parents=True, exist_ok=True)
    mode = "simulated" if simulated else "live"
    run_id = f"{mode}-{uuid4().hex}"
    trace_file = output_dir / f"graph-chat-{run_id}.jsonl"
    report_file = output_dir / f"benchmark-{run_id}.json"
    results = []
    halt = None
    with trace_file.open("x", encoding="utf-8") as stream:
        provider = _provider(stream)
        try:
            tracer = provider.get_tracer("graph-chat-benchmark")
            for attempt in range(1, passes + 1):
                for case, question in questions:
                    metadata = {}
                    before = budget.reserved_usd
                    started = perf_counter()
                    outcome, answer = "error", None
                    try:
                        answer, _, _ = run_agent(question, answer_metadata=metadata,
                                                 benchmark_budget=budget,
                                                 benchmark_tracer=tracer)
                        outcome = metadata["status"]
                    except BenchmarkLimitError:
                        outcome = "budget_abort"
                    except Exception:
                        outcome = "service_error"
                    results.append({
                        "case": case, "pass": attempt, "outcome": outcome,
                        "trace_id": metadata.get("trace_id"), "answer": answer,
                        "elapsed_ms": round((perf_counter() - started) * 1000, 3),
                        "reserved_usd": str(budget.reserved_usd - before),
                    })
                    if budget.stopped:
                        halt = outcome
                        break
                if halt is not None:
                    break
            flushed = provider.force_flush(timeout_millis=3000)
        finally:
            provider.shutdown()

    traces = {}
    for line in trace_file.read_text(encoding="utf-8").splitlines():
        try:
            span = json.loads(line)
        except json.JSONDecodeError:
            continue
        if span["name"] == "graph_chat.request":
            traces[span["trace_id"]] = span
    for result in results:
        result["trace_exported"] = result["trace_id"] in traces
        result["trace_url"] = (
            f"http://127.0.0.1:8765/?trace={result['trace_id']}"
            if result["trace_exported"] and output_dir.resolve() == (ROOT / "tmp" / "graph-chat-traces").resolve()
            else None
        )
    report = {
        "mode": mode, "run_id": run_id, "halt": halt,
        "ceiling_usd": str(budget.ceiling_usd), "reserved_usd": str(budget.reserved_usd),
        "max_output_tokens": budget.max_output, "max_calls_per_case": budget.max_calls, "prior_reserved_usd": str(prior_reserved_usd),
        "planned_maximum_usd": str(worst_case),
        "unreserved_usd": str(budget.ceiling_usd - prior_reserved_usd - budget.reserved_usd),
        "trace_flush_ok": flushed, "trace_file": trace_file.name, "results": results,
    }
    with report_file.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
    return report_file, report
