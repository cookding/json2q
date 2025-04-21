from dataclasses import dataclass
from typing import Any, Optional, TypedDict, TypeVar

T = TypeVar("T")

AND = "AND"
OR = "OR"


class LogicalOperatorProperty(TypedDict):
    join_type: str
    is_negated: bool


LOGICAL_OP_PROPERTIES: dict[str, LogicalOperatorProperty] = {
    "$and": {"join_type": AND, "is_negated": False},
    "$or": {"join_type": OR, "is_negated": False},
    "$not": {"join_type": AND, "is_negated": True},
}


class FieldOperatorProperty(TypedDict):
    suffix: str


FIELD_OP_PROPERTIES: dict[str, FieldOperatorProperty] = {
    "$eq": {"suffix": ""},
    "$ne": {"suffix": "__not"},
    "$lt": {"suffix": "__lt"},
    "$lte": {"suffix": "__lte"},
    "$gt": {"suffix": "__gt"},
    "$gte": {"suffix": "__gte"},
    "$in": {"suffix": "__in"},
    "$contains": {"suffix": "__contains"},
    "$startsWith": {"suffix": "__startswith"},
    "$endsWith": {"suffix": "__endswith"},
}


class LogicalFilterContext(TypedDict):
    depth: int


class FieldFilterContext(TypedDict):
    field_prefix: str
    depth: int


class JSON2Q:
    @dataclass
    class ConvertionOptions:
        """Options to configure the convertion in ``json2q.to_q``."""

        max_depth: int = 8
        """By default, when nesting logical operators or fields, ``json2q`` will only decode up to 8 children deep.
        This depth can be overridden by setting the ``max_depth``.
        The depth limit helps mitigate abuse when ``json2q`` is used to parse user input,
        and it is recommended to keep it a reasonably small number."""

        max_keys: int = 64
        """By default, ``json2q`` will only parse up to 64 keys in each level. This can be overridden by
        passing a ``max_keys`` option."""

    @classmethod
    def _logical_filter_to_q(
        cls,
        logical_op: str,
        conditions: list[dict[str, Any]],
        Q: type[T],
        options: ConvertionOptions,
        context: LogicalFilterContext,
    ) -> T:
        if context["depth"] > options.max_depth:
            raise ValueError("Filters depth exceeded max_depth")
        expressions = [
            cls._to_q(
                condition,
                Q,
                options,
                {
                    "depth": context["depth"] + 1,
                },
            )
            for condition in conditions
        ]
        q = Q(
            *expressions,
            join_type=LOGICAL_OP_PROPERTIES[logical_op]["join_type"],
        )  # type: ignore[call-arg]
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
        options: ConvertionOptions,
        context: FieldFilterContext,
    ) -> T:
        if context["depth"] > options.max_depth:
            raise ValueError("Filters depth exceeded max_depth")
        expressions = []
        for key, value in conditions.items():
            if key in FIELD_OP_PROPERTIES:
                op = key
                q_filter_key = f"{context['field_prefix']}{field}{FIELD_OP_PROPERTIES[op]['suffix']}"
                q_filter_value = value
                expressions.append(
                    Q(
                        join_type="AND",
                        **{f"{q_filter_key}": q_filter_value},
                    )  # type: ignore[call-arg]
                )
            else:
                sub_field = key
                sub_conditions = value
                sub_field_prefix = f"{context['field_prefix']}{field}__"
                expressions.append(
                    cls._field_filter_to_q(
                        sub_field,
                        sub_conditions,
                        Q,
                        options,
                        {
                            "field_prefix": sub_field_prefix,
                            "depth": context["depth"] + 1,
                        },
                    )
                )

        if len(expressions) == 1:
            return expressions[0]
        else:
            return Q(
                *expressions,
                join_type="AND",
            )  # type: ignore[call-arg]

    @classmethod
    def _to_q(
        cls,
        filters: dict[str, Any],
        Q: type[T],
        options: ConvertionOptions,
        context: LogicalFilterContext,
    ) -> T:
        if len(filters) == 0:
            return Q()
        if len(filters) > 1:
            # split filters
            if len(filters) > options.max_keys:
                raise ValueError("Filters keys exceeded max_keys")
            expressions = [
                cls._to_q(
                    {f"{key}": value},
                    Q,
                    options,
                    {
                        "depth": context["depth"],
                    },
                )
                for key, value in filters.items()
            ]
            return Q(
                *expressions,
                join_type=AND,
            )  # type: ignore[call-arg]

        key, conditions = next(iter(filters.items()))
        if key in LOGICAL_OP_PROPERTIES:
            # logical filter
            logical_op = key
            return cls._logical_filter_to_q(
                logical_op,
                conditions,
                Q,
                options,
                {
                    "depth": context["depth"],
                },
            )

        if not key.startswith("$"):
            # field filter
            field = key
            return cls._field_filter_to_q(
                field,
                conditions,
                Q,
                options,
                {
                    "field_prefix": "",
                    "depth": context["depth"],
                },
            )

        raise SyntaxError("Unsupported operator or field")

    @classmethod
    def to_q(
        cls,
        filters: dict[str, Any],
        Q: type[T],
        options: Optional[ConvertionOptions] = None,
    ) -> T:
        return cls._to_q(
            filters,
            Q,
            options if options != None else cls.ConvertionOptions(),
            {"depth": 1},
        )
