# Attested History — Multi-Agent Curator for Shapecraft (Hackathon Build Spec)

> This document is written so an AI coding assistant can generate the repo, code files, and configs for a working demo on **Shape testnet**. It specifies agents, APIs, contracts, schemas, and build steps.

---

## 0) Goals & Judging Alignment

- **Deliver a visible, multi-agent system** that curates, generates, votes, and mints historical NFTs on **Shape testnet**.
- Showcase **Shape primitives** (Gasback, Stack medals) without reinventing core infra.
- Optimize for a **3-minute demo**: one click → agents execute → UI streams events → on-chain links open.

**Judging interpretation**

- _AI Agent Effectiveness_: autonomous orchestration with human approvals at key gates.
- _Innovation (without wheel-reinvention)_: use Gasback + Stack medals + explicit agent modules.
- _Technical Excellence_: clean interfaces, typed IO, observable runs, and resilient retries.

---

## 1) Top-Level System Overview

### 1.1 Components

- **Frontend (Next.js + Vercel AI SDK)**

  - “**Curator Agent**” chat interface.
  - **Agent Console** (event feed per agent).
  - Wallet connect, signing, vote UI, medal claim CTA.
  - Subscribes to backend **SSE** stream for run updates.

- **Backend (LangGraph service)**

  - Orchestrator supergraph + subgraphs:

    - **Lore Agent** (research/context)
    - **Artist Agent** (image proposals + IPFS pin)
    - **Vote Agent** (open/monitor/close vote)
    - **Mint Agent** (finalize metadata + mint)
    - **Attestation Agent** (optional SIWE/EAS)
    - **Guard Agent** (policy checks; stub)

  - **Checkpointer** (SQLite/Redis) + **interrupts** at decision gates.
  - **REST** control plane + **SSE** progress stream.

- **MCP Tool Layer**

  - Read tools: chain stats, gasback info, medal lookups.
  - Write tools: `start_vote`, `vote_status`, `tally_vote`, `mint_final`, `issue_medal`, `pin_cid`, `pin_metadata`, `eas_attest` (optional).
  - **Prepare calldata**; signing happens in the browser wallet.

- **Smart Contracts (testnet)**

  - `DropManager` (opens vote, finalizes mint).
  - `HistorianMedals` (ERC-1155) for Stack/medal-like UX (or integrate with an existing Stack helper if available).
  - Minimal, event-rich, safe.

### 1.2 Happy-Path Sequence (high level)

1. User chooses a **historical date/topic** → Curator starts a run.
2. **Lore Agent** produces `LorePack` → _Checkpoint: approve/edit_.
3. **Artist Agent** generates 4–6 images → pins to IPFS (`ArtSet`).
4. **Vote Agent** opens an on-chain vote (allowlist or open).
5. Voting concludes → **Mint Agent** mints with the winning CID → metadata pinned.
6. (Optional) **Attestation Agent** posts SIWE link/EAS attestation.
7. System mints a **“Historian Voter” medal** to participants; UI shows **Gasback** accrual.

---

## 2) Explicit Multi-Agent Design

### 2.1 Typed IO Contracts (shared `packages/types`)

```ts
// Lore
export interface LorePack {
  summary_md: string; // <= 200 words
  bullet_facts: string[]; // 5-10 crisp facts
  sources: string[]; // URLs, 5+ preferred
  prompt_seed: {
    style: string;
    palette: string;
    motifs: string[];
    negative?: string;
  };
}

// Artist
export interface ArtSet {
  cids: string[]; // IPFS CIDs for full images
  thumbnails: string[]; // IPFS or data URLs (<=200KB each)
  style_notes: string[]; // one per image
  reject_reasons?: string[]; // if any candidates filtered
}

// Voting
export type VoteGate = "allowlist" | "open" | "passport_stub";
export interface VoteConfig {
  method: "simple";
  gate: VoteGate;
  duration_s: number;
}

export interface VoteResult {
  winner_cid: string;
  tally: Record<string, number>;
  participation: number;
}

// Mint
export interface MintReceipt {
  tx_hash: string;
  token_id: string | number;
  token_uri: string;
}

export interface AttestationReceipt {
  id: string;
  uri: string;
}

// Orchestrator state
export interface RunState {
  run_id: string;
  date_label: string; // e.g., "2015-07-30 – Ethereum Genesis Block"
  lore?: LorePack;
  art?: ArtSet;
  vote?: { id: string; config: VoteConfig; result?: VoteResult };
  mint?: MintReceipt;
  attest?: AttestationReceipt;
  checkpoint?: "lore_approval" | "art_sanity" | "finalize_mint" | null;
  error?: string | null;
}
```

### 2.2 Agent Responsibilities

- **Lore Agent**

  - Input: `{ date_label }`
  - Output: `LorePack`
  - Validations: ≥5 sources; ≤200-word summary; sanitized prompt seed.

- **Artist Agent**

  - Input: `LorePack`
  - Output: `ArtSet` (4–6 CIDs)
  - Validations: ≥4 images; size limits; basic safety filter.

- **Vote Agent**

  - Input: `ArtSet`, `VoteConfig`
  - Output: `VoteResult`
  - Behavior: open → stream status → close on timeout/quorum.

- **Mint Agent**

  - Input: `{ LorePack, winner_cid }`
  - Output: `MintReceipt`
  - Behavior: build metadata JSON, pin, mint, verify tokenURI.

- **Attestation Agent (optional)**

  - Input: `{ token_id, winner_cid, statement_uri }`
  - Output: `AttestationReceipt`

- **Guard Agent (stub)**

  - Input: `LorePack`, `ArtSet`
  - Output: `PolicyOK | Block(reason)`

---

## 3) Orchestration (LangGraph)

### 3.1 Checkpoints & Interrupts

- **CHECKPOINT #1 – `lore_approval`**: human can edit/approve `summary_md` + `prompt_seed`.
- **OPTIONAL CHECKPOINT – `art_sanity`**: human can request 1 regen wave.
- **CHECKPOINT #2 – `finalize_mint`**: confirm proceed to irreversible mint.

### 3.2 State Machine (Mermaid)

```mermaid
stateDiagram-v2
  [*] --> DraftMetadata
  DraftMetadata --> LoreApproval: LorePack ready (interrupt)
  LoreApproval --> ArtGeneration: approved/edit applied
  ArtGeneration --> ArtSanity: ArtSet ready (interrupt optional)
  ArtSanity --> VoteLive: proceed
  VoteLive --> VoteClosed: duration/quorum
  VoteClosed --> FinalizeMint: winner_cid determined (interrupt)
  FinalizeMint --> Attest: (optional)
  Attest --> Complete
  FinalizeMint --> Complete
  [*] <-- Complete
```

### 3.3 Backend Interfaces (REST + SSE)

- `POST /runs`

  - Body: `{ date_label: string }`
  - Returns: `{ run_id: string }` and starts orchestration.

- `GET /runs/{run_id}` → current `RunState`.

- `GET /runs/{run_id}/stream` (**SSE**)

  - Emits `event: update` with `data: RunState` deltas whenever an agent finishes a step.

- `POST /runs/{run_id}/resume`

  - Body: `{ checkpoint: string, decision: "approve" | "edit" | "proceed" | "regen" | "finalize", payload?: any }`
  - Advances the graph after a checkpoint.

**SSE event envelope (example)**

```json
event: update
data: {
  "run_id": "abc123",
  "phase": "Artist",
  "message": "Generated 6 images and pinned to IPFS",
  "state": { ...RunState delta... },
  "links": [
    {"label": "CID #1", "href": "ipfs://..."},
    {"label": "CID #2", "href": "ipfs://..."}
  ]
}
```

> Implementation hint: Use LangGraph’s `astream(..., stream_mode="updates")` and push each update line to the SSE response.

---

## 4) Frontend (Next.js + Vercel AI SDK)

### 4.1 Pages & Components

- `/` — Curator chat + **Agent Console** split view.

  - **Curator Chat**: Vercel AI SDK for streaming model replies + tool calls (read-only MCP tools).
  - **Agent Console**: subscribes to `/runs/{id}/stream` (EventSource) and renders agent-prefixed events (🧠 Lore, 🎨 Artist, 🗳 Vote, 🪙 Mint, 🧾 Attest).

- **WalletConnect** (wagmi/viem)

  - Used to sign vote txs, mint finalize, and (optional) SIWE.

- **Voting UI**

  - Displays candidate thumbnails; writes signed tx via prepared calldata from MCP `start_vote`.

- **Gasback Panel**

  - Polls MCP `gasback_info(contract)`; displays accrual/claimable.

- **Medal Badge**

  - After vote close, calls `issue_medal(address)`; shows token id / link.

### 4.2 Curator Tooling (AI SDK)

- Frontend calls read MCP tools (stats, gasback) and backend REST for long tasks.
- Use `generateObject`/`streamObject` to build a clean `LorePack` edit payload at `lore_approval`.

---

## 5) MCP Tools (HTTP MCP server)

> Implement as a tiny Node/Express or Python FastAPI service that exposes MCP-compatible endpoints; backend and frontend both consume it.

### 5.1 Read Tools

- `chain_info()` → network/meta.
- `gasback_info(contract: string)` → `{ accrued: string, claimable: string }`
- `medal_of(address: string)` → owned medal IDs.
- `nft_insights(collection: string)` → minimal stats for demo.

### 5.2 Write Tools (prepare calldata; no private keys)

- `pin_cid(bytes|url)` → `cid`
- `pin_metadata(json)` → `cid`
- `start_vote(artCids: string[], cfg: VoteConfig)` → `{ vote_id, tx: PreparedTx }`
- `vote_status(vote_id)` → status struct
- `tally_vote(vote_id)` → `{ winner_cid, tally }`
- `mint_final(winner_cid, metadataCid)` → `{ tx: PreparedTx }`
- `issue_medal(toAddress)` → `{ tx: PreparedTx }`
- `eas_attest(payload)` (optional) → `{ tx: PreparedTx }`

**PreparedTx schema**

```ts
export interface PreparedTx {
  to: string;
  data: `0x${string}`;
  value?: `0x${string}`;
  gas?: number;
}
```

---

## 6) Smart Contracts (Solidity, testnet-oriented)

> Keep contracts minimal, event-rich, and safe. Use OpenZeppelin.

### 6.1 `DropManager.sol`

- **Storage**

  - `mapping(bytes32 => Vote)` by `voteId` (e.g., keccak(date_label + timestamp))
  - `address public nft;` (ERC-721 or 1155)
  - `address public medal;` (ERC-1155)

- **Events**

  - `event VoteOpened(bytes32 voteId, string[] cids, VoteConfig cfg);`
  - `event VoteClosed(bytes32 voteId, string winnerCid, uint256 totalVotes);`
  - `event MintFinalized(uint256 tokenId, string tokenURI, string winnerCid);`

- **Functions**

  - `openVote(string[] memory cids, VoteConfig cfg) returns (bytes32 voteId)`
  - `castVote(bytes32 voteId, uint index)` (simple 1p1v; for demo)
  - `closeVote(bytes32 voteId)` (sets winner per tally)
  - `finalizeMint(bytes32 voteId, string winnerCid, string tokenURI) returns (uint256 tokenId)`

> For the hack, **simplify voting**: 1p1v, indexed choice, allowlist gate by msg.sender checking a small mapping (UI pre-populated).

### 6.2 `HistorianMedals.sol` (ERC-1155)

- `mint(address to, uint256 id, uint256 amount, bytes memory data)` gated to owner.
- Medal ID constant `HISTORIAN_VOTER = 1`.
- Event on mint; link in UI.

### 6.3 Metadata

- Off-chain pinned JSON:

```json
{
  "name": "Ethereum Genesis Block — July 30, 2015",
  "description": "Commemorative NFT for the Ethereum genesis block. Includes curated summary and sources.",
  "image": "ipfs://<winner_cid>",
  "attributes": [
    { "trait_type": "Date", "value": "2015-07-30" },
    { "trait_type": "WinnerCID", "value": "<cid>" },
    { "trait_type": "Sources", "value": "<count>" }
  ],
  "properties": {
    "summary_md": "<markdown>",
    "sources": ["https://...", "..."],
    "prompt_seed": { "style": "...", "palette": "...", "motifs": ["..."] },
    "attestation_uri": "ipfs://... (optional)"
  }
}
```

---

## 7) Gasback & Medals (Demo-ready)

- **Gasback**

  - Ensure `DropManager` is registered (if needed) for Gasback tracking on testnet.
  - Expose MCP `gasback_info(DropManager)` and show the counter in UI (OK if simulated with a simple `.accumulated +=` based on txs, but prefer real).

- **Stack / Medal**

  - If a ready-made stack medal helper isn’t available, mint from `HistorianMedals` after `VoteClosed`.
  - UI shows a **“You earned the Historian Voter medal”** toast with link to the token on the explorer.

---

## 8) Repo Layout

```
attested-history/
├─ apps/
│  ├─ frontend/          # Next.js + Vercel AI SDK + wagmi
│  └─ backend/           # FastAPI (or Node) LangGraph service (REST+SSE)
├─ packages/
│  ├─ mcp-server/        # MCP tools (HTTP server)
│  ├─ contracts/         # Foundry/Hardhat (DropManager, HistorianMedals, ERC721 impl)
│  └─ types/             # Shared TS types (LorePack, ArtSet, etc.)
├─ infra/
│  ├─ .env.example
│  └─ deploy/            # scripts for testnet deploy + addresses.json
├─ README.md
└─ docs/                  # this spec + demo script
```

---

## 9) Environment & Config

`.env.example` (root or per app)

```
# Frontend
NEXT_PUBLIC_MCP_URL=http://localhost:4000
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_SHAPE_RPC_URL=<testnet rpc>
NEXT_PUBLIC_CHAIN_ID=<shape testnet id>

# Backend
BACKEND_PORT=8000
CHECKPOINTER_URL=sqlite:///state.db  # or redis://...

# MCP
MCP_PORT=4000
IPFS_PIN_URL=<pinning service endpoint>
IPFS_PIN_KEY=<token>

# Contracts
DROP_MANAGER_ADDRESS=0x...
HISTORIAN_MEDALS_ADDRESS=0x...
NFT_ADDRESS=0x...
```

---

## 10) Build Order (Time-boxed)

1. **Contracts**

   - Implement `DropManager`, `HistorianMedals`, simple ERC-721 for NFTs.
   - Deploy to testnet; write `addresses.json`.

2. **MCP server**

   - Stub read tools (`chain_info`, `gasback_info` mocked).
   - Implement `pin_cid`, `pin_metadata`.
   - Implement `start_vote` (returns `PreparedTx` for `openVote`) and `mint_final`.

3. **Backend**

   - LangGraph: supergraph + subgraphs; checkpointer; SSE stream.
   - Nodes: Lore → Artist → Vote → Mint (+ optional Attest).
   - `/runs`, `/runs/{id}`, `/runs/{id}/stream`, `/runs/{id}/resume`.

4. **Frontend**

   - Wallet connect; Curator chat (AI SDK).
   - Agent Console with SSE subscription.
   - Voting page/modal (send signed tx using `PreparedTx`).
   - Medal toast + Gasback panel.

5. **Polish**

   - Optional Attestation Agent (SIWE/EAS link stored in metadata).
   - README with demo steps + disclaimers.

---

## 11) Demo Script (≤3 minutes)

1. **Start run** for “**2015-07-30 — Ethereum Genesis Block**”.
2. Curator shows **Lore Agent** summary → _approve_.
3. **Artist Agent** renders 4 thumbnails (CIDs visible) → _proceed_.
4. **Vote Agent** opens vote; cast votes from 2 wallets; stream tally.
5. Vote closes; **Mint Agent** mints → show tokenURI + explorer.
6. Medal drops to voter → show medal link; **Gasback** panel ticks up.
7. (Optional) Show “Attestation URI” attribute on token metadata.

---

## 12) Failure Modes & Recovery

- **IPFS pin fails** → retry with backoff; if persistent, set `checkpoint="art_sanity"` and ask to regenerate or proceed with fewer images.
- **Vote capture/low participation** → timeout fallback: pick best-of-N by heuristic (e.g., CLIP score) and surface rationale in console.
- **Mint revert** → show revert reason; allow _retry finalize_.
- **SSE disconnect** → frontend auto-reconnects; backend streams last known state on connect.

---

## 13) Security & Constraints (Hackathon-pragmatic)

- **Signing only in browser wallets**; MCP prepares calldata only.
- **No private keys** in servers or repos.
- **Positive depictions/naming only**; avoid sensitive/negative portrayals.
- **Model/license README**: state which image model is used and license terms.
- **Data minimization**: stream only non-secret status via SSE.

---

## 14) Optional: Attestation Design (SIWE/EAS-style without infra lock-in)

- **SIWE message template** (string fields; signed client-side):

  ```
  I endorse token {token_id} with image {winner_cid} on {chain_name}.
  TokenURI: {token_uri}
  Statement URI: {statement_uri}
  Nonce: {nonce}
  ```

- Upload signature JSON to IPFS as `{ "siwe_signature": "...hex...", "message": "...", "address": "0x..." }`
- Store `attestation_uri` in token metadata.
- If time permits, create an EAS attestation with fields `{ endorser, token, tokenHash, statementURI }`.

---

## 15) Frontend Event Schema (Agent Console)

```ts
export interface AgentEvent {
  ts: string; // ISO time
  agent: "Lore" | "Artist" | "Vote" | "Mint" | "Attest" | "Guard" | "Curator";
  level: "info" | "warn" | "error";
  message: string;
  links?: { label: string; href: string }[];
  data?: Record<string, any>;
}
```

- Render prefix emojis:

  - 🧠 Lore, 🎨 Artist, 🗳 Vote, 🪙 Mint, 🧾 Attest, 🛡️ Guard, 🧑‍⚖️ Curator

---

## 16) Minimal Voting UX (for reliability)

- **Allowlist gate**: JSON list baked into frontend for demo (two or three addresses).
- **Method**: simple majority; duration 60–120 seconds.
- **Fallback**: if no votes → pick index `0` and log “fallback due to no participation”.

---

## 17) Testing Checklist

- Unit: contracts (open/close vote; finalize mint; medal mint).
- Integration: MCP `start_vote` returns executable calldata; viem sends tx.
- E2E: start run → approve lore → vote → finalize → token URI resolves → medal minted.
- Reconnect: close browser tab mid-vote, reopen, **SSE** resumes state.

---

## 18) Deliverables

- **Deployed testnet addresses** in `infra/deploy/addresses.json`.
- **Screenshare-able demo** at `/` with two wallets handy.
- **README** with:

  - env setup
  - deploy scripts
  - “Run backend”, “Run MCP”, “Run frontend”
  - caveats and “future work” (Passport gate, quadratic voting, charity rails).

---

## 19) Future Work (post-hackathon)

- Proper sybil-resistant gates (Passport/VCs; quadratic voting).
- Real **Gasback** accrual visualization with claim flow.
- Production attestation (EAS) + public indexer page.
- Charity split contracts + compliance notes.
- Model fine-tuning for stylistic coherence across dates.

---

### Appendix A — Suggested Prompts (for AI coding assistant)

- “Generate a **FastAPI** service with `POST /runs`, `GET /runs/{id}`, `GET /runs/{id}/stream` (SSE), `POST /runs/{id}/resume`. Integrate **LangGraph** with a SQLite checkpointer. Implement subgraphs: `Lore`, `Artist`, `Vote`, `Mint`. Use the typed IO from `packages/types` and the checkpoints described above.”
- “Create a **Next.js** app with Vercel AI SDK chat on the left and a live **Agent Console** on the right. Subscribe to `/runs/{id}/stream` via `EventSource`. Render per-agent events with emojis and explorer/IPFS links.”
- “Implement an **MCP** HTTP server that exposes the read/write tools outlined, returning **PreparedTx** objects. Provide a `viem` snippet in the frontend to sign & submit those transactions.”
- “Write **Solidity** contracts `DropManager` and `HistorianMedals` per spec. Include events, minimal safety, and test scripts to deploy to a Shape-compatible testnet. Export addresses to `infra/deploy/addresses.json`.”

---

This is everything needed to scaffold and implement a credible, **explicit multi-agent** Shapecraft demo on testnet, with Shape-native features and a clean, judge-friendly UX.
