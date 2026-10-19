"""Versioned claim staging contract; independent of the legacy Docling Graph template.

Candidates cannot approve themselves. These models are not publication records.
"""
from decimal import Decimal, InvalidOperation
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

VERSION = "0.2"


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Entity(Strict):
    id: str = Field(min_length=1)
    kind: Literal["Symptom", "Cause", "Action", "Product", "ProcessStep"]
    name: str = Field(min_length=1)
    product_kind: Literal["prepacked_column", "chromatography_medium", "magnetic_beads", "unknown"] | None
    evidence_refs: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def product_type(self):
        if (self.kind == "Product") != (self.product_kind is not None):
            raise ValueError("product_kind is required only for Product entities")
        return self


def decimals(values):
    try:
        parsed = [Decimal(v) for v in values]
    except InvalidOperation as exc:
        raise ValueError("Numbers must be decimal strings") from exc
    if not all(v.is_finite() for v in parsed):
        raise ValueError("Non-finite quantities are forbidden")
    return parsed


class Condition(Strict):
    field: str = Field(min_length=1)
    role: Literal["applicability", "trigger"]
    operator: Literal["equals", "not_equals", "lt", "lte", "gt", "gte", "between", "not_between", "source_text"]
    value_kind: Literal["text", "categorical", "decimal"]
    values: list[str] = Field(min_length=1)
    unit: str | None
    source_text: str = Field(min_length=1)
    evidence_refs: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def typed_comparison(self):
        if self.operator == "source_text":
            if self.value_kind != "text" or len(self.values) != 1 or self.unit is not None:
                raise ValueError("source_text is a single unresolved text condition")
            return self
        size = 2 if self.operator in ("between", "not_between") else 1
        if len(self.values) != size:
            raise ValueError("Wrong condition operand count")
        if self.value_kind == "decimal":
            nums = decimals(self.values)
            if not self.unit:
                raise ValueError("Numeric conditions need an explicit unit, including pH or dimensionless")
            if size == 2 and nums[0] > nums[1]:
                raise ValueError("Reversed interval")
        elif self.value_kind != "categorical" or self.operator not in ("equals", "not_equals") or self.unit is not None:
            raise ValueError("Prose must use source_text; exact comparisons require categorical codes")
        elif not all(re.fullmatch(r'[A-Za-z][A-Za-z0-9_.:-]*', v) for v in self.values):
            raise ValueError("Categorical codes cannot contain a sentence or numeric range")
        return self


class ConditionGroup(Strict):
    # Disjunction of groups; conjunction within one group. [] means no condition.
    all_of: list[Condition] = Field(min_length=1)


class Purpose(Strict):
    text: str = Field(min_length=1)
    evidence_refs: list[str] = Field(min_length=1)


class Denominator(Strict):
    value: str
    unit: str = Field(min_length=1)

    @model_validator(mode="after")
    def positive(self):
        if decimals([self.value])[0] <= 0:
            raise ValueError("Denominator must be positive")
        return self


class Quantity(Strict):
    comparator: Literal["eq", "range", "gte", "lte", "gt", "lt", "approx"]
    values: list[str] = Field(min_length=1)
    unit: str = Field(min_length=1)
    denominator: Denominator | None
    material: str | None
    evidence_refs: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def numeric_shape(self):
        nums = decimals(self.values)
        if len(nums) != (2 if self.comparator == "range" else 1):
            raise ValueError("Wrong quantity operand count")
        if len(nums) == 2 and nums[0] > nums[1]:
            raise ValueError("Reversed quantity interval")
        return self


class Parameter(Strict):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    value_text: str = Field(min_length=1)
    quantities: list[Quantity]
    evidence_refs: list[str] = Field(min_length=1)


class Scope(Strict):
    product_ids: list[str]
    process_step_ids: list[str]
    status: Literal["resolved", "unresolved"]
    evidence_refs: list[str] = Field(min_length=1)


class SourceIssue(Strict):
    id: str = Field(min_length=1)
    kind: Literal["source_conflict", "unclear_quantity", "unclear_scope", "unclear_condition", "missing_source", "other"]
    description: str = Field(min_length=1)
    evidence_refs: list[str] = Field(min_length=1)
    affected_claim_ids: list[str]


class Claim(Strict):
    id: str = Field(min_length=1)
    subject_id: str
    predicate: Literal["MAY_CAUSE", "RECOMMENDED_FOR", "CAN_REMOVE", "PREVENTS_BUILDUP_OF", "PROCEDURE", "DESCRIPTIVE"]
    object_id: str | None
    statement: str = Field(min_length=1)
    force: Literal["possible", "recommended", "required", "prohibited", "descriptive", "unspecified"]
    source_role: Literal["protocol", "troubleshooting", "precaution", "figure_example", "general_description"]
    symptom_context: Literal["observed_trigger", "potential_risk", "not_applicable"]
    scope: Scope
    condition_groups: list[ConditionGroup]
    purposes: list[Purpose]
    parameters: list[Parameter]
    parameter_logic: Literal["all", "any", "and_or", "sequence", "not_applicable"]
    evidence_refs: list[str] = Field(min_length=1)
    disposition: Literal["review_required", "quarantine"]
    issue_ids: list[str]


class ClaimExtraction(Strict):
    schema_version: Literal["0.2"]
    entities: list[Entity]
    claims: list[Claim]
    source_issues: list[SourceIssue]


def evaluate_conditions(groups: list[ConditionGroup], context: dict) -> bool | None:
    """Evaluate already source-validated DNF; this pure helper has no corpus.

    No NLP, unit conversion, human approval or application authorization.
    """
    def evaluate(c):
        if c.operator == "source_text" or c.field not in context:
            return None
        supplied = context[c.field]
        if not isinstance(supplied, dict) or supplied.get("unit") != c.unit:
            return None
        actual = supplied.get("value")
        try:
            if c.value_kind == "decimal":
                if not isinstance(actual, str):
                    return None
                actual = decimals([actual])[0]
                values = decimals(c.values)
            else:
                if not isinstance(actual, str):
                    return None
                values = c.values
            if c.operator == "equals": return actual == values[0]
            if c.operator == "not_equals": return actual != values[0]
            if c.operator == "lt": return actual < values[0]
            if c.operator == "lte": return actual <= values[0]
            if c.operator == "gt": return actual > values[0]
            if c.operator == "gte": return actual >= values[0]
            within = values[0] <= actual <= values[1]
            return within if c.operator == "between" else not within
        except (ValueError, TypeError, InvalidOperation):
            return None
    if not groups:
        return True
    results = []
    for group in groups:
        leaves = [evaluate(c) for c in group.all_of]
        results.append(False if False in leaves else None if None in leaves else True)
    return True if True in results else None if None in results else False
