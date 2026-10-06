# Presenter Script: Generating Sample Events

Demo file: `demos/generate_epr_events.py`. Time: 5 minutes.

## Goal

Show that EPR is a registry of events with a schema per event type, and fill it
with realistic data that the next two demos can query. The audience should leave
knowing the three record types (receiver, event, group) and how a receiver
relates to an event.

## Prerequisites

- EPR running at `http://localhost:8042`:
  `cd docs/tutorials/code && docker compose up -d --build`
- A terminal in the repository root, with uv installed.
- Check:
  `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8042/healthz/readiness`
  prints `200`.

## Before you start

- Decide whether to leave the existing data in place. Posting adds 11 receivers
  and 44 events every time; reset with
  `(cd docs/tutorials/code && docker compose down -v && docker compose up -d)`.
- Increase the terminal font. The curl lines are long.

## Steps

### 1. Show what would be sent (dry run)

Say: "First, with no side effects: what would this script send to EPR?"

```bash
uv run python demos/generate_epr_events.py --dry-run | head -4 | cut -c1-150
```

Expected output (the first lines are the receivers):

```text
Dry run: curl commands for event receivers:
curl -sS -X POST -H 'Content-Type: application/json' -d '{"name":"dev-cdevents-pipelinerun-started","version":"0.2.0","description":"Dev Cdevents Pipelinerun Started","type":"dev.cdevents.pipelinerun.started.0.2.0","schema":{}}' http://localhost:8042/api/v1/receivers
...
```

Talking points:

- A receiver declares a kind of event: a name, a type, a version, and a JSON
  schema the payload must match. Here the schema is empty, so any payload
  passes.
- There is one receiver per CDEvents type, 11 in all: pipeline runs, builds,
  artifacts, tests, environments, and services. CDEvents is the standard for
  continuous delivery events.
- It is plain curl. Everything the MCP server does later is just these same HTTP
  calls.

### 2. Count what it generates

```bash
uv run python demos/generate_epr_events.py --dry-run | grep -c '^curl'
```

Expected output: `55`.

Say: "11 receivers plus 44 events: four services named foo, bar, baz, and qux,
each with one event of each of the 11 types."

### 3. Show one event

```bash
uv run python demos/generate_epr_events.py --dry-run | grep 'api/v1/events' | head -1 | cut -c1-400
```

Talking points:

- An event links to its receiver through `event_receiver_id`. In a dry run that
  field is a placeholder because the receivers do not exist yet.
- The `payload` holds the CDEvent: a `context` (id, source, type, timestamp) and
  a `subject` (what the event is about).
- IDs are ULIDs: 26 characters, sortable by time. The script generates them
  itself; nothing extra is installed.

### 4. Post them for real

Say: "Now the real thing. Receivers first, then events that point at them."

```bash
uv run python demos/generate_epr_events.py
```

Expected output (abridged, the IDs differ):

```text
Posting 11 event receivers to http://localhost:8042/api/v1/receivers
dev.cdevents.pipelinerun.started.0.2.0: 200
dev.cdevents.pipelinerun.queued.0.2.0: 200
...
01M48VCRF6YEN43WKBBBRX83Y2: 200
...
Posted 44/44 events successfully
```

Talking points:

- Each line is an HTTP status from EPR. EPR answers a successful create with 200
  and returns only the new ID.
- The script exits 0 when everything posted and 1 if anything failed, so it can
  run in a pipeline.

### 5. Optional: write the data to files instead

```bash
uv run python demos/generate_epr_events.py --write-to-disk
```

This writes `epr_reports/event_receivers/`, `epr_reports/events/`, and two files
of curl commands, and posts nothing. Delete `epr_reports/` afterwards.

## Failure recovery

| Symptom                                  | Cause and fix                                                              |
| ---------------------------------------- | -------------------------------------------------------------------------- |
| `Request failed: ... Connection refused` | EPR is not running. Run the prerequisite command and wait a minute         |
| Every line says `ERROR`, exit code 1     | Same cause, or a wrong `--url`. Check the readiness curl                   |
| `HTTP error 400: ... schema is required` | Receiver JSON without a `schema`. The script always sends one; check edits |
| Fewer than 44 events posted              | Read the `Failed to post event` lines above the summary                    |
| Output is hard to follow                 | Use `--dry-run`, which prints without posting                              |

## Reset

`(cd docs/tutorials/code && docker compose down -v)` removes all EPR data.

Next: [OpenAPI demo](openapi_demo_script.md).
