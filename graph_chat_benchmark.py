"""Run the reviewed graph chat benchmark against an explicitly supplied client."""
from decimal import Decimal
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
FIRST_RUN_RESERVE_USD = Decimal("0.399168")
RETRY_MAX_OUTPUT = 1536


def run_targeted_retry(client, *, output_dir=None, simulated=False):
    """Repeat G01 and G02 twice against the remainder of the original ceiling."""
    return run_benchmark(client, output_dir=output_dir, simulated=simulated,
                         case_ids=("G01", "G02"), max_output=RETRY_MAX_OUTPUT,
                         prior_reserved_usd=FIRST_RUN_RESERVE_USD)


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
                  max_calls=GraphChatBudget.MAX_CALLS):
    """Use one budget and one initialized local trace exporter for the selected passes."""
    if type(passes) is not int or not 1 <= passes <= 2:
        raise ValueError("Invalid benchmark pass count")
    reviewed = dict(reviewed_questions())
    if not case_ids or len(set(case_ids)) != len(case_ids) or any(c not in reviewed for c in case_ids):
        raise ValueError("Invalid reviewed case selection")
    questions = [(case, reviewed[case]) for case in case_ids]
    budget = GraphChatBudget(client, max_output=max_output, prior_reserved_usd=prior_reserved_usd,
                            max_calls=max_calls)
    worst_case = passes * len(questions) * budget.max_calls * budget.call_reserve_usd
    if prior_reserved_usd + worst_case > budget.CEILING_USD:
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
        "ceiling_usd": str(budget.CEILING_USD), "reserved_usd": str(budget.reserved_usd),
        "max_output_tokens": budget.max_output, "max_calls_per_case": budget.max_calls, "prior_reserved_usd": str(prior_reserved_usd),
        "planned_maximum_usd": str(worst_case),
        "unreserved_usd": str(budget.CEILING_USD - prior_reserved_usd - budget.reserved_usd),
        "trace_flush_ok": flushed, "trace_file": trace_file.name, "results": results,
    }
    with report_file.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
    return report_file, report
