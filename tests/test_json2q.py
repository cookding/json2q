from typing import Any

import pytest

from json2q import json2q
from tests.fixtures.q import Q


def test_empty_filters():
    q = json2q.to_q({}, Q)
    assert len(q.children) == 0
    assert len(q.filters) == 0


@pytest.mark.parametrize(
    "filters, kwargs",
    [
        ({"age": {"$eq": 10}}, {"age": 10}),
        ({"age": {"$ne": 10}}, {"age__not": 10}),
        ({"age": {"$lt": 10}}, {"age__lt": 10}),
        ({"age": {"$lte": 10}}, {"age__lte": 10}),
        ({"age": {"$gt": 10}}, {"age__gt": 10}),
        ({"age": {"$gte": 10}}, {"age__gte": 10}),
        ({"age": {"$in": [10, 20]}}, {"age__in": [10, 20]}),
        ({"name": {"$contains": "Alice"}}, {"name__contains": "Alice"}),
        ({"name": {"$startsWith": "Alice"}}, {"name__startswith": "Alice"}),
        ({"name": {"$endsWith": "Alice"}}, {"name__endswith": "Alice"}),
    ],
)
def test_single_field_filters(filters: dict[str, Any], kwargs: dict[str, Any]):
    q = json2q.to_q(filters, Q)

    assert q.join_type == "AND"
    assert len(q.children) == 0
    assert len(q.filters) == len(kwargs)
    for key in kwargs.keys():
        assert q.filters[key] == kwargs[key]
    assert q._is_negated == False


def test_multiple_fields_filters():
    filters = {
        "name": {"$startsWith": "Alice"},
        "age": {"$eq": 10},
    }

    q = json2q.to_q(filters, Q)

    assert q.join_type == "AND"
    assert len(q.children) == 2
    assert len(q.filters) == 0
    assert q._is_negated == False
    assert q.children[0].join_type == "AND"
    assert len(q.children[0].children) == 0
    assert q.children[0].filters == {"name__startswith": "Alice"}
    assert q.children[0]._is_negated == False
    assert q.children[1].join_type == "AND"
    assert len(q.children[1].children) == 0
    assert q.children[1].filters == {"age": 10}
    assert q.children[1]._is_negated == False


@pytest.mark.parametrize(
    "operator, join_type, is_negated",
    [("$and", "AND", False), ("$or", "OR", False), ("$not", "AND", True)],
)
def test_logical_operators(operator, join_type, is_negated):
    filters = {
        f"{operator}": [
            {"name": {"$startsWith": "Alice"}},
            {"age": {"$eq": 10}},
        ]
    }

    q = json2q.to_q(filters, Q)

    assert q.join_type == join_type
    assert len(q.children) == 2
    assert len(q.filters) == 0
    assert q._is_negated == is_negated
    assert q.children[0].join_type == "AND"
    assert len(q.children[0].children) == 0
    assert q.children[0].filters == {"name__startswith": "Alice"}
    assert q.children[0]._is_negated == False
    assert q.children[1].join_type == "AND"
    assert len(q.children[1].children) == 0
    assert q.children[1].filters == {"age": 10}
    assert q.children[1]._is_negated == False


def test_nested_fields():
    filters = {
        "extras": {
            "name": {"$startsWith": "Alice"},
            "age": {"$eq": 10},
        }
    }

    q = json2q.to_q(filters, Q)

    assert q.join_type == "AND"
    assert len(q.children) == 2
    assert len(q.filters) == 0
    assert q._is_negated == False
    assert q.children[0].join_type == "AND"
    assert len(q.children[0].children) == 0
    assert q.children[0].filters == {"extras__name__startswith": "Alice"}
    assert q.children[0]._is_negated == False
    assert q.children[1].join_type == "AND"
    assert len(q.children[1].children) == 0
    assert q.children[1].filters == {"extras__age": 10}
    assert q.children[1]._is_negated == False


def test_nested_logical_operators():
    filters = {
        "$and": [
            {
                "name": {
                    "$startsWith": "Alice",
                },
            },
            {
                "$or": [
                    {
                        "age": {
                            "$lt": 10,
                        },
                    },
                    {
                        "age": {
                            "$gt": 20,
                        },
                    },
                ],
            },
        ],
    }

    q = json2q.to_q(filters, Q)

    assert q.join_type == "AND"
    assert len(q.children) == 2
    assert len(q.filters) == 0
    assert q._is_negated == False
    assert q.children[0].join_type == "AND"
    assert len(q.children[0].children) == 0
    assert q.children[0].filters == {"name__startswith": "Alice"}
    assert q.children[0]._is_negated == False
    assert q.children[1].join_type == "OR"
    assert len(q.children[1].children) == 2
    assert len(q.children[1].filters) == 0
    assert q.children[1]._is_negated == False
    assert q.children[1].children[0].join_type == "AND"
    assert len(q.children[1].children[0].children) == 0
    assert q.children[1].children[0].filters == {"age__lt": 10}
    assert q.children[1].children[0]._is_negated == False
    assert q.children[1].children[1].join_type == "AND"
    assert len(q.children[1].children[1].children) == 0
    assert q.children[1].children[1].filters == {"age__gt": 20}
    assert q.children[1].children[1]._is_negated == False


def test_raise_when_filters_structure_invalid():
    filters = {
        "$eq": 1,
    }

    try:
        q = json2q.to_q(filters, Q)
    except SyntaxError as e:
        assert e.msg == "Unsupported operator or field"
