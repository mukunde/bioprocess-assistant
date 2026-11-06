"""Opt-in spend guard for the sequential graph chat benchmark."""
from decimal import Decimal


class BenchmarkLimitError(RuntimeError):
    """A benchmark constraint could not be enforced."""


class GraphChatBudget:
    MODEL = "claude-sonnet-4-6"
    MAX_SUBMISSIONS = 8
    MAX_CALLS = 3
    MAX_INPUT = 5000
    MAX_ESTIMATED_INPUT = 4500
    MAX_OUTPUT = 512
    CEILING_USD = Decimal("1.00")
    def __init__(self, client, *, max_output=MAX_OUTPUT, prior_reserved_usd=Decimal("0"),
                 max_calls=MAX_CALLS):
        if type(max_output) is not int or not 1 <= max_output <= 2048:
            raise ValueError("Invalid benchmark output limit")
        if not prior_reserved_usd.is_finite() or not 0 <= prior_reserved_usd <= self.CEILING_USD:
            raise ValueError("Invalid prior reserve")
        if type(max_calls) is not int or not 1 <= max_calls <= self.MAX_CALLS:
            raise ValueError("Invalid model call limit")
        self.max_calls = max_calls
        self.max_output = max_output
        self.call_reserve_usd = (
            (3 * self.MAX_INPUT + 15 * max_output) * Decimal("1.10") / 1_000_000
        )
        self.prior_reserved_usd = prior_reserved_usd
        self.messages = client.with_options(max_retries=0).messages
        self.submissions = 0
        self.reserved_usd = Decimal("0")
        self.stopped = False

    def start_submission(self):
        if self.stopped or self.submissions >= self.MAX_SUBMISSIONS:
            raise BenchmarkLimitError("benchmark submission limit or stop")
        self.submissions += 1
        return _Submission(self)


class _Submission:
    def __init__(self, budget):
        self.budget = budget
        self.calls = 0

    def prepare(self, *, model, system, tools, messages):
        budget = self.budget
        if budget.stopped or self.calls >= budget.max_calls:
            raise BenchmarkLimitError("benchmark model call limit or stop")
        if model != budget.MODEL:
            budget.stopped = True
            raise BenchmarkLimitError("unpriced benchmark model")
        committed = budget.prior_reserved_usd + budget.reserved_usd
        if committed + budget.call_reserve_usd > budget.CEILING_USD:
            budget.stopped = True
            raise BenchmarkLimitError("benchmark spend ceiling")
        payload = dict(model=model, system=system, tools=tools, messages=messages)
        try:
            count = budget.messages.count_tokens(**payload).input_tokens
        except Exception as exc:
            budget.stopped = True
            raise BenchmarkLimitError("input token preflight unavailable") from exc
        if type(count) is not int or not 0 < count <= budget.MAX_ESTIMATED_INPUT:
            budget.stopped = True
            raise BenchmarkLimitError("input token preflight exceeds limit or is invalid")
        self.calls += 1
        budget.reserved_usd += budget.call_reserve_usd
        return payload

    def send(self, payload):
        budget = self.budget
        try:
            response = budget.messages.create(**payload, max_tokens=budget.max_output)
        except Exception:
            budget.stopped = True
            raise
        usage = getattr(response, "usage", None)
        for field, maximum in (("input_tokens", budget.MAX_INPUT),
                               ("output_tokens", budget.max_output)):
            value = getattr(usage, field, None)
            if type(value) is not int or not 0 <= value <= maximum:
                budget.stopped = True
                raise BenchmarkLimitError("reported usage exceeds limit or is unavailable")
        if (getattr(usage, "cache_creation_input_tokens", None) not in (None, 0)
                or getattr(usage, "cache_read_input_tokens", None) not in (None, 0)
                or getattr(usage, "inference_geo", None) not in (None, "global", "us")
                or getattr(usage, "speed", None) not in (None, "standard")
                or getattr(usage, "service_tier", None) not in (None, "standard")):
            budget.stopped = True
            raise BenchmarkLimitError("unexpected billing attributes")
        return response
