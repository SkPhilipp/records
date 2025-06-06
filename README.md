# Records

Records is a Python package for managing small amounts of data, tailored to be used by AI Agents in the scope of tasks.

## Why

Recently I prompted an AI with access to Google Maps and a browser for the following;

1. "Find me boxing gyms near Amsterdam"
2. "What's the time to reach them with public transport from Amsterdam Lelylaan"
3. "Remove those that are more than 30 minutes away"
4. "Find out which of them offer heavy bag training in the evening"
5. "What's the top 3 with the best reviews"

These tasks require an agent to maintain a body of data which is manipulated at each step in the process.
At each step of this process we are exposed to risks. I wondered about how I could get the following guarantees;

| Guarantee          | Description                                                                                   |
| ------------------ | --------------------------------------------------------------------------------------------- |
| Data integrity     | Can we guarantee data being output by an agent is exactly what was yielded by external tools? |
| Data consistency   | Can we guarantee data follows a consistent format?                                            |
| Context limits     | Can we avoid having to feed large amounts of data into the agent's context window?            |
| Context safety     | Can we avoid having to feed unsafe data into the agent's context window?                      |
| Process repetition | Can we re-do most of the process without having to explicitly re-prompt the agent?            |
| Process mistakes   | Can we undo a mistake when it is detected later on in the process?                            |
| Process review     | Can we validate that each step of the process does what it is supposed to do?                 |

## Concept

The concept of Records is;
1. Codify tasks to keep data out of agents' context windows.
2. Hand these agents an extremely lenient interface to manage structured data.
3. Infer and constrain the data's structure as it is worked with.
4. Track changes, allowing for step-by-step reviews and re-do's.

## `records`

`records` is the main interface through which data and their structure is managed.

```python
from dataclasses import dataclass
from records import records
import google_maps

loc = records.location(lat=12.345, long=67.890)
loc.address = google_maps.lookup(loc.lat, loc.long)

records.structure()
# {
#	"location": {
#       "id": int,
#		"lat": float,
#		"long": float,
#		"address": Address,
#	}
# }

records.location.all()
# [
#	{"id": 0, "lat": 12.345, "long": 67.890, "address": {...}}
# ]

records.location.delete(id=0)
```

On program end, the data is persisted to a database and a change report is generated.

```log
Structure change report:
+ location.lat: float
+ location.long: float
+ location.address: {street: str, city: str, state: str, zip: str}

Content change report summary:
+ location(lat=12.345, long=67.890, address: Address(street="123 Main St", ...))
+ (10 locations omitted)

To undo all of the above changes, invoke `records.undo()` once.
```
