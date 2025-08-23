# Gasback and Medals (Offline Implementation Plan)

## Gasback (read-only for demo)

- Show an "Accrued Gasback" number tied to `DROP_MANAGER_ADDRESS`.
- Poll an MCP read tool: `gasback_info(contract)` → `{ accrued, claimable }`.
- If real endpoint not wired, **simulate** accrued = k × (# of txs our contract emitted in session).

## Medals

- Minimal ERC-1155 (`HistorianMedals`) with ID `1` = "Historian Voter".
- Mint after vote close to all participating addresses.
- UI: Show a toast + link to `EXPLORER_BASE/token/HISTORIAN_MEDALS_ADDRESS?id=1`.

## UX hooks

- In the Agent Console, after `VoteClosed`, print:
  - "🪙 Minting medal to N voters… tx: 0x…"
  - "🎉 Medal minted to 0x…"

