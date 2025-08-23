# Frontend: Vercel AI SDK + EventSource

## Tool usage

- Use AI SDK `tool()` for read-only MCP calls like `gasback_info`, `chain_info`.
- Use `generateObject` to collect user edits to `LorePack` at checkpoints.

## EventSource client (SSE)

```ts
const es = new EventSource(`${BACKEND_URL}/runs/${runId}/stream`);
es.onmessage = (ev) => {
  const update = JSON.parse(ev.data);
  // append to Agent Console
};
es.onerror = () => {
  /* auto-reconnect with backoff */
};
```

## Checkpoint actions

- POST `/runs/{id}/resume` with `{ checkpoint, decision, payload }`.
- Map UI buttons to decisions: approve/edit/proceed/regen/finalize.

## UI Hints

- Left: Curator chat (AI SDK).
- Right: Agent Console (timeline with emojis, links).
- Floating panel: Gasback counter + "Your medal(s)".

