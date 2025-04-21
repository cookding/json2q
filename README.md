# json2q

A library to convert JSON filters to Q expressions.

## Usage

* Filter fields
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

* Filter fields with logical operators
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

* Filter fields with convertion options
```python
from tortoise.expressions import Q
from json2q import json2q

filters = {
    "extras": {
        "name": {
                "$startsWith": "A"
        },
        "age": {
            "$eq": 10
        },
    },
}

q = json2q(filters, Q, json2q.ConvertionOptions(max_depth=2))
# OK
q = json2q(filters, Q, json2q.ConvertionOptions(max_depth=1))
# raise ValueError

q = json2q(filters, Q, json2q.ConvertionOptions(max_keys=2))
# OK
q = json2q(filters, Q, json2q.ConvertionOptions(max_keys=1))
# raise ValueError
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

## Convertion Options

| Option    | Default | Description                                       |
|-----------|---------|---------------------------------------------------|
| max_depth | 8       | Max depth of  nesting logical operators or fields |
| max_keys  | 64      | Max keys in each level of filters                 |

## Todo

- Support more operators
- More filters structure validation
