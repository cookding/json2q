# json2q

A library to convert JSON filters to Q expressions.

## Usage

```python
from tortoise.expressions import Q
from json2q import json2q

filters = {
    "age": {
        "$eq": 10
    },
    "name": {
        "$startsWith": "A"
    },
}

q = json2q(filters, Q)
# Q(age=10) & Q(name__startswith='A')
```

```python
from tortoise.expressions import Q
from json2q import json2q

filters = {
    "$or": [
        {
            "age": {
                "$eq": 10
            }
        },
        {
            "name": {
                "$startsWith": "A"
            }
        }
    ]
}

q = json2q(filters, Q)
# Q(age=10) | Q(name__startswith='A')
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

- Support nested fields
- Support more operators
- More JSON filters structure validation
