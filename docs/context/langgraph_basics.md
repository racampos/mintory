# LangGraph Patterns for This Project

## Core concepts we use

- **State object** (`RunState`) carried through the graph.
- **Checkpointer** (SQLite or Redis) to resume between steps.
- **Interrupts** at checkpoints; graph yields and waits for `/resume`.
- **Streaming updates** via `astream(..., stream_mode="updates")`.

## Node types (subgraphs)

- Lore → Artist → Vote → Mint → (Attest)
- Each node:
  1. reads the needed slice from state,
  2. calls tools (MCP or model),
  3. validates output,
  4. returns a **pure** delta to merge into state.

## Suggested skeleton (Python pseudocode)

```python
class RunState(TypedDict):
    run_id: str
    date_label: str
    lore: Optional[LorePack]
    art: Optional[ArtSet]
    vote: Optional[VoteState]
    mint: Optional[MintReceipt]
    attest: Optional[AttestationReceipt]
    checkpoint: Optional[str]
    error: Optional[str]

@node
def lore_node(state: RunState) -> dict:
    # call model to draft, collect sources (static/mock OK), build prompt_seed
    lore = build_lore(...)
    return {"lore": lore, "checkpoint": "lore_approval"}

@interrupt(condition=lambda s: s["checkpoint"] == "lore_approval")
def wait_lore_approval(): pass

# …similar for artist_node, vote_node, mint_node

graph = Graph()
graph.add(lore_node).then(wait_lore_approval).then(artist_node)...
```

## Resilience

- Each node retries with exponential backoff on transient errors (pinning, RPC).
- Irreversible side-effects only after the **finalize_mint** checkpoint.

