# Backend Orchestrator API (REST + SSE)

## POST /runs

Body: `{ "date_label": "2015-07-30 — Ethereum Genesis Block" }`
→ `{ "run_id": "abc123" }` (starts orchestration)

## GET /runs/{run_id}

→ `RunState` (see agents_spec.md)

## GET /runs/{run_id}/stream (SSE)

- `event: update`
- `data: { agent, level, message, state_delta, links[] }`

## POST /runs/{run_id}/resume

Body:

```json
{
  "checkpoint": "lore_approval" | "art_sanity" | "finalize_mint",
  "decision": "approve" | "edit" | "proceed" | "regen" | "finalize",
  "payload": {}
}
```

### Error contract

- 4xx with `{ error: "HUMAN_READABLE" }`
- Stream `level: "error"` messages before returning error if mid-flow.

