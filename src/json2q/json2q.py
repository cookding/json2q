from typing import Any, TypedDict, TypeVar

T = TypeVar("T")

AND = "AND"
OR = "OR"


class LogicalOperatorProperty(TypedDict):
    join_type: str
    is_negated: bool


LOGICAL_OP_PROPERTIES: dict[str, LogicalOperatorProperty] = {
    "$and": {
        "join_type": AND,
        "is_negated": False,
    },
    "$or": {
        "join_type": OR,
        "is_negated": False,
    },
    "$not": {
        "join_type": AND,
        "is_negated": True,
    },
}


class FieldOperatorProperty(TypedDict):
    suffix: str


FIELD_OP_PROPERTIES: dict[str, FieldOperatorProperty] = {
    "$eq": {
        "suffix": "",
    },
    "$ne": {
        "suffix": "__not",
    },
    "$lt": {
        "suffix": "__lt",
    },
    "$lte": {
        "suffix": "__lte",
    },
    "$gt": {
        "suffix": "__gt",
    },
    "$gte": {
        "suffix": "__gte",
    },
    "$in": {
        "suffix": "__in",
    },
    "$contains": {
        "suffix": "__contains",
    },
    "$startsWith": {
        "suffix": "__startswith",
    },
    "$endsWith": {
        "suffix": "__endswith",
    },
}


class JSON2Q:
    @classmethod
    def _logical_filter_to_q(
        cls, logical_op: str, conditions: list[dict[str, Any]], Q: type[T]
    ) -> T:
        expressions = [cls.to_q(condition, Q) for condition in conditions]
        q = Q(*expressions, join_type=LOGICAL_OP_PROPERTIES[logical_op]["join_type"])  # type: ignore[call-arg]
        if LOGICAL_OP_PROPERTIES[logical_op]["is_negated"]:
            return ~q  # type: ignore[operator,no-any-return]
        else:
            return q

    @classmethod
    def _field_filter_to_q(
        cls, field: str, conditions: dict[str, Any], Q: type[T]
    ) -> T:
        q_kwargs = {}
        for op, value in conditions.items():
            if op in FIELD_OP_PROPERTIES:
                q_kwargs[f"{field}{FIELD_OP_PROPERTIES[op]['suffix']}"] = value
            else:
                raise SyntaxError("Unsupported operator")

        return Q(join_type="AND", **q_kwargs)  # type: ignore[call-arg]

    @classmethod
    def to_q(cls, filters: dict[str, Any], Q: type[T]) -> T:
        if len(filters) == 0:
            return Q()
        # split filters
        if len(filters) > 1:
            expressions = [
                cls.to_q({f"{key}": value}, Q) for key, value in filters.items()
            ]
            return Q(*expressions, join_type=AND)  # type: ignore[call-arg]

        # logical filter
        key, conditions = next(iter(filters.items()))
        if key in LOGICAL_OP_PROPERTIES:
            logical_op = key
            return cls._logical_filter_to_q(logical_op, conditions, Q)

        # field filter
        field = key
        return cls._field_filter_to_q(field, conditions, Q)
