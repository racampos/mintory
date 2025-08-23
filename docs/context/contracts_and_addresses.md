# Contracts, Networks, and Addresses

## networks.ts (TS object your code imports)

```ts
export const NETWORK = {
  CHAIN_ID: CHAIN_ID, // number
  RPC_URL: "RPC_URL",
  EXPLORER_BASE: "EXPLORER_BASE",
} as const;
```

## addresses.json (to be generated after deploy)

```json
{
  "chainId": CHAIN_ID,
  "DropManager": "0xDROP_MANAGER_ADDRESS",
  "HistorianMedals": "0xHISTORIAN_MEDALS_ADDRESS",
  "NFT": "0xNFT_ADDRESS"
}
```

## Minimal ABIs (only functions we call)

```json
[
  {
    "type": "function",
    "name": "openVote",
    "inputs": [
      { "name": "cids", "type": "string[]" },
      {
        "name": "cfg",
        "type": "tuple",
        "components": [
          { "name": "method", "type": "uint8" },
          { "name": "gate", "type": "uint8" },
          { "name": "duration", "type": "uint256" }
        ]
      }
    ],
    "outputs": [{ "type": "bytes32" }]
  },
  {
    "type": "function",
    "name": "castVote",
    "inputs": [
      { "name": "voteId", "type": "bytes32" },
      { "name": "index", "type": "uint256" }
    ],
    "outputs": []
  },
  {
    "type": "function",
    "name": "closeVote",
    "inputs": [{ "name": "voteId", "type": "bytes32" }],
    "outputs": []
  },
  {
    "type": "function",
    "name": "finalizeMint",
    "inputs": [
      { "name": "voteId", "type": "bytes32" },
      { "name": "winnerCid", "type": "string" },
      { "name": "tokenURI", "type": "string" }
    ],
    "outputs": [{ "type": "uint256" }]
  },
  {
    "type": "event",
    "name": "VoteOpened",
    "inputs": [{ "indexed": false, "name": "voteId", "type": "bytes32" }],
    "anonymous": false
  },
  {
    "type": "event",
    "name": "VoteClosed",
    "inputs": [
      { "indexed": false, "name": "voteId", "type": "bytes32" },
      { "indexed": false, "name": "winnerCid", "type": "string" }
    ],
    "anonymous": false
  },
  {
    "type": "event",
    "name": "MintFinalized",
    "inputs": [
      { "indexed": false, "name": "tokenId", "type": "uint256" },
      { "indexed": false, "name": "tokenURI", "type": "string" }
    ],
    "anonymous": false
  }
]
```

> NOTE: Use real ABIs from your contracts once compiled; these stubs unblock the assistant.

