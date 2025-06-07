# Records

Records is a Python package intended to be consumed by AI Agents managing small amounts of data.

It offers an extremely lenient interface to manage structured data, tracks changes and allows for step-by-step reviews. This makes it easy to codify tasks, keep data out of agents' context windows and re-do mistakes.

## Usage

```python
from src.records import Records

records = Records()
records.location(lat=12.345, long=67.890)
```

On program end, the data is automatically persisted to JSON and a change report is generated like so:

```text
Structure changes:
+ location._id: int
+ location.lat: float
+ location.long: float

Content changes:
+ location(lat=12.345, long=67.89)

To undo all of the above changes, invoke `records.undo()` once.
```

This should allow an AI agent to decide whether its changes were successful, and if not, to re-do them.
Moreover, the data is loaded from JSON on program start, so it can be used again on a next step in a process.

```python
from src.records import Records

records = Records()
records.location.all()
# [
#	{"_id": 0, "lat": 12.345, "long": 67.890}
# ]
```

## Why

Recently I prompted an AI with access to Google Maps and a browser for the following;

1. "Find me boxing gyms near Amsterdam"
2. "What's the time to reach them with public transport from Amsterdam Lelylaan"
3. "Remove those that are more than 30 minutes away"
4. "Find out which of them offer heavy bag training in the evening"
5. "What's the top 3 with the best reviews"

These tasks require an agent to maintain a body of data which is manipulated at each step in the process.
At each step of this process we are exposed to risks. I wondered about how I could get the following guarantees;

- Can we guarantee data being output by an agent is exactly what was yielded by external tools?
- Can we guarantee data follows a consistent format?
- Can we avoid having to feed large amounts of data into the agent's context window?
- Can we avoid having to feed unsafe data into the agent's context window?
- Can we re-do most of the process without having to explicitly re-prompt the agent?
- Can we undo a mistake when it is detected later on in the process?
- Can we validate that each step of the process does what it is supposed to do?

## API

### Initialization

```python
from src.records import Records
# Uses "records.json" by default
records = Records()
```

### Inserts

```python
loc = records.location(lat=12.345, long=67.890)
```

Note:
- Using a record type for the first time, defines it.
- Using a record attribute for the first time, defines it.
- Attribute values are limited to JSON-native types.
- Attribute values may not be set to different types once set, other than `None`.
- An attribute `_id` is always automatically assigned an integer value.

### Updates

```python
loc.address = "123 Main St, Amsterdam, Netherlands"
```

The same rules apply as for inserts.

### Queries

```python
records.location.all()
# [
#	{"_id": 0, "lat": 12.345, "long": 67.890, "address": "123 Main St, Amsterdam, Netherlands"}
# ]
```

Note:
- All data is stored in memory, there is no query language.

### Deletes

```python
records.location.delete(0)
```

### Structure

```python
records.structure()
# {
#	"location": {
#       "_id": "int",
#		"lat": "float", 
#		"long": "float",
#		"address": "str",
#	}
# }
```
## Development

### Tests

```bash
./run_tests.sh
```
