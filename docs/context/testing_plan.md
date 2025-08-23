# Testing Plan

## Unit (contracts)

- openVote stores candidates; emits VoteOpened.
- castVote tallies correctly; closeVote sets winner.
- finalizeMint emits MintFinalized; tokenURI set.

## Integration

- MCP start_vote returns PreparedTx executable by viem.
- pin_metadata → CID; metadata JSON matches schema.

## E2E

- Start run → lore_approval → art → vote → finalize → tokenURI resolves.
- Medal minted to voter, visible in UI list.

## Resilience

- Drop browser mid-vote; reconnect → SSE resumes state.
- Pinning failure → Artist retries; if fails twice, ask for regen.

