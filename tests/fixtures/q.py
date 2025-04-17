from __future__ import annotations
from typing import Any, Literal


class Q:
    join_type: Literal["AND", "OR"]
    children: list[Q]
    filters: dict[str, Any]

    def __init__(
        self,
        *args: Q,
        join_type: Literal["AND", "OR"] = "AND",
        **kwargs: dict[str, Any],
    ) -> None:
        if args and kwargs:
            self.children = [*args, Q(join_type=join_type, **kwargs)]
            self.filters = {}
        elif args:
            self.children = [*args]
            self.filters = {}
        elif kwargs:
            self.children = []
            self.filters = kwargs
        else:
            self.children = []
            self.filters = {}

        self.join_type = join_type
        self._is_negated = False

    def negate(self):
        self._is_negated = not self._is_negated

    def __and__(self, other: Q) -> Q:
        return Q(self, other, join_type="AND")

    def __or__(self, other: Q) -> Q:
        return Q(self, other, join_type="OR")

    def __invert__(self) -> Q:
        q = Q(*self.children, join_type=self.join_type)
        q.negate()
        return q
