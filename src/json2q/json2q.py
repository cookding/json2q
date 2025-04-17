from typing import Any

AND = "AND"
OR = "OR"


class JSON2Q:
    @classmethod
    def to_q(self, filters: dict[str, Any], Q: type) -> Any:
        if len(filters) == 0:
            return Q()
        # split filters
        if len(filters) > 1:
            expressions = []
            for key, value in filters.items():
                expressions.append(self.to_q({f"{key}": value}, Q))
            return Q(*expressions, join_type=AND)

        # logical filter
        if "$and" in filters:
            expressions = []
            for filter_item in filters["$and"]:
                expressions.append(self.to_q(filter_item, Q))
            return Q(*expressions, join_type=AND)

        if "$or" in filters:
            expressions = []
            for filter_item in filters["$or"]:
                expressions.append(self.to_q(filter_item, Q))
            return Q(*expressions, join_type=OR)

        if "$not" in filters:
            expressions = []
            for filter_item in filters["$not"]:
                expressions.append(self.to_q(filter_item, Q))
            return ~Q(*expressions, join_type=AND)

        # field filter
        field, conditions = next(iter(filters.items()))
        q_kwargs = {}
        for op, value in conditions.items():
            match op:
                case "$eq":
                    q_kwargs[field] = value
                case "$ne":
                    q_kwargs[f"{field}__not"] = value
                case "$gt":
                    q_kwargs[f"{field}__gt"] = value
                case "$gte":
                    q_kwargs[f"{field}__gte"] = value
                case "$lt":
                    q_kwargs[f"{field}__lt"] = value
                case "$lte":
                    q_kwargs[f"{field}__lte"] = value
                case "$in":
                    q_kwargs[f"{field}__in"] = value
                case "$contains":
                    q_kwargs[f"{field}__contains"] = value
                case "$startsWith":
                    q_kwargs[f"{field}__startswith"] = value
                case "$endsWith":
                    q_kwargs[f"{field}__endswith"] = value
                case _:
                    raise SyntaxError("Unsupported operator")

        return Q(join_type="AND", **q_kwargs)
