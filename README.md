# json2q

A library to convert JSON filters to Q expressions.

## Usage

```python
from tortoise.expressions import Q
from json2q import json2q

filters = {
    "name": {
        "$startsWith": "A"
    },
    "extras": {
        "age": {
            "$eq": 10
        },
    }
}

q = json2q(filters, Q)
# Q(name__startswith='A') & Q(extras__age=10)
```

```python
from tortoise.expressions import Q
from json2q import json2q

filters = {
    "$or": [
        {
            "name": {
                "$startsWith": "A"
            }
        },
        {
            "$and": [
                {
                    "age": {
                        "$gt": 10
                    },
                },
                {
                    "age": {
                        "$lt": 20
                    },
                },
            ]
        },
    ]
}

q = json2q(filters, Q)
# Q(name__startswith='A') | (Q(age__gt=10) & Q(age__lt=20))
```

## Supported Operators

| Operator      | Description                          |
|---------------|--------------------------------------|
| `$eq`         | Equal                                |
| `$ne`         | Not equal                            |
| `$lt`         | Less than                            |
| `$lte`        | Less than or equal                   |
| `$gt`         | Greater than                         |
| `$gte`        | Greater than or equal                |
| `$in`         | Included in an array                 |
| `$contains`   | Contains                             |
| `$startsWith` | Starts with                          |
| `$endsWith`   | Ends with                            |
| `$and`        | Join the filters in "and" expression |
| `$or`         | Join the filters in "or" expression  |
| `$not`        | Join the filters in "not" expression |

## Todo

- Support more operators
- More filters structure validation
- Support config options to filters structure validation
