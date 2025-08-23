# MCP Server API Reference

## Read Tools

### GET /mcp/chain_info

Returns basic chain information.

**Response:**

```json
{
  "chainId": 11011,
  "name": "Shape Network"
}
```

### GET /mcp/gasback_info?contract=ADDRESS

Returns gasback information for a given contract address.

**Parameters:**

- `contract` (query) - Contract address

**Response:**

```json
{
  "accrued": "0",
  "claimable": "0"
}
```

### GET /mcp/medal_of?address=ADDRESS

Returns medals owned by an address.

**Parameters:**

- `address` (query) - Wallet address

**Response:**

```json
{
  "medals": [
    {
      "id": "1",
      "balance": "1"
    }
  ]
}
```

## Write Tools

### POST /mcp/pin_cid

Pins content to IPFS. Accepts either raw bytes or JSON with URL.

**Body (raw bytes):** File data
**Body (JSON):**

```json
{
  "url": "https://example.com/image.jpg"
}
```

**Response:**

```json
{
  "cid": "ipfs://QmHash..."
}
```

### POST /mcp/pin_metadata

Pins JSON metadata to IPFS.

**Body:** Any JSON object

**Response:**

```json
{
  "cid": "ipfs://QmHash..."
}
```

### POST /mcp/start_vote

Creates a vote transaction.

**Body:**

```json
{
  "artCids": ["ipfs://QmHash1", "ipfs://QmHash2"],
  "cfg": {
    "method": "simple",
    "gate": "open",
    "duration_s": 3600
  }
}
```

**Response:**

```json
{
  "vote_id": "0x...",
  "tx": {
    "to": "0x...",
    "data": "0x...",
    "gas": 100000
  }
}
```

### GET /mcp/vote_status?vote_id=BYTES32

Returns vote status.

**Parameters:**

- `vote_id` (query) - Vote ID (32-byte hex)

**Response:**

```json
{
  "open": true,
  "tallies": [5, 3, 1],
  "endsAt": "2024-01-01T12:00:00.000Z"
}
```

### POST /mcp/tally_vote

Tallies votes and returns winner.

**Body:**

```json
{
  "vote_id": "0x..."
}
```

**Response:**

```json
{
  "winner_cid": "ipfs://QmWinnerHash",
  "tally": {
    "0": 5,
    "1": 3,
    "2": 1
  }
}
```

### POST /mcp/mint_final

Creates final mint transaction.

**Body:**

```json
{
  "winner_cid": "ipfs://QmWinnerHash",
  "metadataCid": "ipfs://QmMetadataHash"
}
```

**Response:**

```json
{
  "tx": {
    "to": "0x...",
    "data": "0x...",
    "gas": 100000
  }
}
```

### POST /mcp/issue_medal

Creates medal issuance transaction.

**Body:**

```json
{
  "toAddress": "0x...",
  "id": 1
}
```

**Response:**

```json
{
  "tx": {
    "to": "0x...",
    "data": "0x...",
    "gas": 100000
  }
}
```

## Common Types

### PreparedTx

All write endpoints return PreparedTx objects for wallet signing:

```json
{
  "to": "0x...", // Contract address
  "data": "0x...", // Encoded function call
  "value": "0x...", // ETH value (optional)
  "gas": 100000 // Gas estimate (optional)
}
```
