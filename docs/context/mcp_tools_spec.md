# MCP Tools — Contract for Frontend/Backend

> MCP server returns JSON and **PreparedTx** blobs. The browser wallet signs/sends.

## Read Tools

### GET /mcp/chain_info

→ `{ chainId, name }`

### GET /mcp/gasback_info?contract=ADDRESS

→ `{ accrued: "0", claimable: "0" }` # strings, wei or humanized — be consistent

### GET /mcp/medal_of?address=ADDRESS

→ `{ medals: [ { id: "1", balance: "1" } ] }`

## Write Tools (prepare calldata only)

### POST /mcp/pin_cid

Body: file bytes or URL → `{ cid: "ipfs://..." }`

### POST /mcp/pin_metadata

Body: JSON → `{ cid: "ipfs://..." }`

### POST /mcp/start_vote

Body: `{ artCids: string[], cfg: { method: "simple", gate: "allowlist"|"open"|"passport_stub", duration_s: number } }`
→ `{ vote_id: "0x…", tx: { to, data, value? } }`

### GET /mcp/vote_status?vote_id=BYTES32

→ `{ open: boolean, tallies: number[], endsAt: ISOString }`

### POST /mcp/tally_vote

Body: `{ vote_id }` → `{ winner_cid, tally: { "0": 2, "1": 1 } }`

### POST /mcp/mint_final

Body: `{ winner_cid, metadataCid }` → `{ tx: { to, data } }`

### POST /mcp/issue_medal

Body: `{ toAddress, id: 1 }` → `{ tx: { to, data } }`

### POST /mcp/eas_attest (optional)

Body: `{ tokenId, tokenHash, statementUri }` → `{ tx: { to, data } }`

## PreparedTx Schema

```ts
type PreparedTx = {
  to: `0x${string}`;
  data: `0x${string}`;
  value?: `0x${string}`;
  gas?: number;
};
```

