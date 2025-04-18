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


class FieldFilterContext(TypedDict):
    field_prefix: str


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
        expressions = [
            cls._to_q(
                condition,
                Q,
                {
                    "field_prefix": "",
                },
            )
            for condition in conditions
        ]
        q = Q(*expressions, join_type=LOGICAL_OP_PROPERTIES[logical_op]["join_type"])  # type: ignore[call-arg]
        if LOGICAL_OP_PROPERTIES[logical_op]["is_negated"]:
            return ~q  # type: ignore[operator,no-any-return]
        else:
            return q

    @classmethod
    def _field_filter_to_q(
        cls,
        field: str,
        conditions: dict[str, Any],
        Q: type[T],
        context: FieldFilterContext,
    ) -> T:
        expressions = []
        for key, value in conditions.items():
            if key in FIELD_OP_PROPERTIES:
                expressions.append(
                    Q(
                        join_type="AND",
                        **{
                            f"{context['field_prefix']}{field}{FIELD_OP_PROPERTIES[key]['suffix']}": value
                        },
                    )  # type: ignore[call-arg]
                )
            else:
                expressions.append(
                    cls._field_filter_to_q(
                        key,
                        value,
                        Q,
                        {
                            "field_prefix": f"{context['field_prefix']}{field}__",
                        },
                    )
                )

        if len(expressions) == 1:
            return expressions[0]
        else:
            return Q(*expressions, join_type="AND")  # type: ignore[call-arg]

    @classmethod
    def _to_q(cls, filters: dict[str, Any], Q: type[T], context: dict[str, Any]) -> T:
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

        if not key.startswith("$"):
            # field filter
            field = key
            return cls._field_filter_to_q(
                field,
                conditions,
                Q,
                {
                    "field_prefix": "",
                },
            )

        raise SyntaxError("Unsupported operator or field")

    @classmethod
    def to_q(cls, filters: dict[str, Any], Q: type[T]) -> T:
        return cls._to_q(
            filters,
            Q,
            {
                "field_prefix": "",
            },
        )
