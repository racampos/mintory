## 0) Ground Rules & Feature Flags

**Architecture**

- **Backend:** Python **LangGraph** orchestrator (FastAPI) with **REST + SSE**, **checkpointer**, and **interrupts**.
- **Frontend:** Next.js + **Vercel AI SDK** + **viem/wagmi**; “Curator” chat + **Agent Console**; wallet signs **PreparedTx** only.
- **MCP server:** HTTP server exposing read/write tools; returns **calldata**; never stores keys.
- **Contracts:** Hardhat (TS) — `DropManager` + `HistorianMedals` on **Shape testnet**.
- **Storage:** Pin **images + metadata** to IPFS before mint; metadata includes summary/sources/prompt_seed.

**Mandatory checkpoints**

- `lore_approval` (required)
- `finalize_mint` (required)
- `art_sanity` (optional)

**Feature flags** (toggle via `.env`)

```
ENABLE_STUB_ART=1     # use placeholder images in Artist Agent
ENABLE_STUB_PIN=1     # return fake ipfs:// CIDs from MCP
ENABLE_STUB_VOTE=1    # auto-pick index 0 if voting not ready
```

**Shared types** live in `packages/types/` and must mirror `docs/context/agents_spec.md`.

---

## Phase 1 — Types & Contracts (Hardhat)

**Objective:** Freeze data contracts (types/ABIs/addresses) so all layers can build.

### Tasks

1. **Types (TS)**

   - Create `packages/types/src/index.ts` with:

     - `LorePack`, `ArtSet`, `VoteConfig`, `VoteResult`, `MintReceipt`, `AttestationReceipt`, `RunState`, `PreparedTx`

   - Add **zod** validators (UI runtime), export schemas.
   - Add `packages/types/package.json` with proper exports.

2. **Hardhat scaffolding**

   - Init Hardhat TS project in `packages/contracts/`.
   - Add OZ contracts, dotenv, ethers plugins.
   - Write `hardhat.config.ts` with `shapetest` network using `RPC_URL`, `CHAIN_ID`, `DEPLOYER_PK`.

3. **Contracts**

   - `contracts/DropManager.sol`

     - `openVote(string[] cids, VoteConfig cfg) returns (bytes32 voteId)`
     - `castVote(bytes32 voteId, uint index)`
     - `closeVote(bytes32 voteId)`
     - `finalizeMint(bytes32 voteId, string winnerCid, string tokenURI) returns (uint256 tokenId)`
     - Events: `VoteOpened`, `VoteClosed`, `MintFinalized`
     - 1p1v + tiny **allowlist** mapping for demo reliability

   - `contracts/HistorianMedals.sol` (ERC-1155)

     - `mint(address to, uint256 id, uint256 amt, bytes data)` owner-only
     - `uint256 public constant HISTORIAN_VOTER = 1;`

   - (Optional) Minimal ERC-721 (`YourERC721.sol`) for NFT if not minting from `DropManager`.

4. **Deploy & export artifacts**

   - `scripts/deploy.ts`: deploy NFT (if used), Medals, DropManager; write `infra/deploy/addresses.json`.
   - `scripts/export-abis.ts`: copy ABIs to `packages/contracts/abi/`.

### Artifacts

- `infra/deploy/addresses.json`
- `packages/contracts/abi/{DropManager.json,HistorianMedals.json,YourERC721.json}`
- `packages/types/dist/*`

### Acceptance Criteria

- `openVote/closeVote/finalizeMint` work in Hardhat scripts.
- `addresses.json` written; ABIs exported.

**Commands**

```bash
cd packages/contracts
npm i
npx hardhat compile
npx hardhat run scripts/deploy.ts --network shapetest
node scripts/export-abis.ts
```

---

## Phase 2 — MCP Server Stubs (HTTP, Node/Express or FastAPI)

**Objective:** Provide **tool endpoints** that return **PreparedTx** and mock pinning/Gasback.

### Routes (minimum)

**Read**

- `GET /mcp/chain_info` → `{ chainId, name }`
- `GET /mcp/gasback_info?contract=0x...` → `{ accrued, claimable }` (mock OK)
- `GET /mcp/medal_of?address=0x...` → `{ medals: [{id:"1", balance:"1"}] }`

**Write (return calldata only, no signing)**

- `POST /mcp/pin_cid` → `{ cid }` (if `ENABLE_STUB_PIN=1`, return `ipfs://FAKE_<hash>`)
- `POST /mcp/pin_metadata` → `{ cid }`
- `POST /mcp/start_vote` → `{ vote_id, tx: PreparedTx }`
- `GET /mcp/vote_status?vote_id=0x...` → `{ open, tallies: number[], endsAt }`
- `POST /mcp/tally_vote` → `{ winner_cid, tally }`
- `POST /mcp/mint_final` → `{ tx: PreparedTx }`
- `POST /mcp/issue_medal` → `{ tx: PreparedTx }`
- `POST /mcp/eas_attest` (optional) → `{ tx: PreparedTx }`

**PreparedTx**

```ts
type PreparedTx = {
  to: `0x${string}`;
  data: `0x${string}`;
  value?: `0x${string}`;
  gas?: number;
};
```

### File layout

```
packages/mcp-server/
  src/index.ts
  src/routes/*.ts
  src/lib/abi.ts            # import from packages/contracts/abi
  src/lib/ipfs.ts           # stubbed pinning
  src/lib/tx.ts             # encodeFunctionData helpers
```

### Acceptance Criteria

- `start_vote` builds calldata using real ABI + addresses.
- A Node script can **send** the PreparedTx with viem and get a tx hash.

---

## Phase 3 — Backend Orchestrator (Python LangGraph) + SSE

**Objective:** Orchestrate the multi-agent flow with **SSE** updates and **interrupts** using **stubs** for art/pin.

### Endpoints

- `POST /runs` → start a run; returns `{ run_id }`
- `GET /runs/{id}` → full `RunState`
- `GET /runs/{id}/stream` → **SSE** of updates (`event: update`, `data: {...}`)
- `POST /runs/{id}/resume` → payload `{ checkpoint, decision, payload? }`

### Modules

```
apps/backend/
  main.py             # FastAPI app + routes
  graph.py            # LangGraph graph + subgraphs + run loop
  models.py           # Pydantic mirrors of types
  nodes/
    lore.py           # returns LorePack + sets checkpoint=lore_approval
    artist.py         # returns ArtSet (stub or real)
    vote.py           # opens/monitors vote via MCP
    mint.py           # pins metadata, prepares mint tx via MCP
    attest.py         # optional SIWE/EAS
  services/
    mcp_client.py     # HTTP client to MCP server
    ipfs_client.py    # optional
  store/
    checkpointer.py   # SQLite or Redis
```

### Behavior

- Use `graph.astream(..., stream_mode="updates")` to push progress lines to SSE.
- Set `checkpoint` in state at `lore_approval` (required) and `finalize_mint` (required); optional `art_sanity`.
- Respect `ENABLE_STUB_*` flags for fast iteration.

### Acceptance Criteria

- `curl -N /runs/{id}/stream` shows events from Lore → Artist → Vote → Mint.
- `/resume` advances state after checkpoints.

**Run**

```bash
uvicorn apps.backend.main:app --reload --port 8000
```

---

## Phase 4 — Frontend (Next.js + Vercel AI SDK + viem)

**Objective:** Deliver the **judge-visible** UI: multi-agent console, chat, wallet, and on-chain flow.

### File layout

```
apps/frontend/
  app/page.tsx                 # main UI
  components/CuratorChat.tsx   # AI SDK chat + tool calls (read only)
  components/AgentConsole.tsx  # SSE timeline with emojis + links
  lib/eventSource.ts           # SSE client with backoff
  lib/wallet.ts                # viem client + sendPreparedTx()
  lib/api.ts                   # calls to backend + MCP
  env.d.ts
```

### UI requirements

- **Left pane:** Curator chat (AI SDK); uses `generateObject` to collect edits at `lore_approval`.
- **Right pane:** Agent Console with events:

  - 🧠 Lore, 🎨 Artist, 🗳️ Vote, 🪙 Mint, 🧾 Attest, 🛡️ Guard

- **Buttons** map to `/runs/{id}/resume`: `approve`, `edit`, `proceed`, `regen`, `finalize`.
- **Wallet**: viem/wagmi; `sendPreparedTx` signs calldata from MCP.
- **Voting modal**: show candidate thumbnails; cast vote tx (you can call DropManager directly with ABI or through MCP-prepared tx).

### Acceptance Criteria

- Full vertical slice on testnet: Start run → approve lore → images (stub) → open vote → cast votes from 2 wallets → close → mint → show tokenURI/IPFS links.

---

## Phase 5 — Replace ALL Agent Stubs with Real Implementations

**Objective:** Upgrade all agents from stubs to real LLM/API/IPFS integration.

### Phase 5.1: MCP Client Infrastructure ✅ **COMPLETED**

_Foundation for all agent integrations_

**✅ Implemented:**

- **MCP Client** (`apps/backend/services/mcp_client.py`): Full HTTP client with all endpoints, error handling, retries, singleton pattern
- **LLM Client** (`apps/backend/services/llm_client.py`): OpenAI integration with chat completions, structured outputs, specialized Lore Agent methods
- **Image Client** (`apps/backend/services/image_client.py`): Multi-provider support (OpenAI DALL-E, Stability AI, Mock), validation, file handling
- **Test Suite** (`apps/backend/test_services.py`): Comprehensive unit & integration tests with 25+ test methods
- **Configuration** (`apps/backend/env.template`): Complete environment variable documentation for all services
- **Dependencies** (`apps/backend/requirements.txt`): Added `openai>=1.0.0`, `pillow>=10.0.0`

**✅ Integration Verified:**

- MCP client successfully calls all endpoints (chain_info, gasback_info, medal_of, start_vote)
- All service imports working with singleton patterns
- Mock image generation tested and working
- Error handling robust across all external API calls

### Phase 5.2: Real Lore Agent ✅ **COMPLETED**

_Replace hardcoded research with LLM calls_

**✅ Implemented:**

- **Real LLM Integration** (`apps/backend/agents/lore.py`): OpenAI GPT-4o API calls for historical research
- **Structured Output Parsing**: JSON extraction with improved error handling for verbose LLM responses
- **Comprehensive Validation**: Enforces agents_spec.md requirements (≤200 words, 5-10 facts, 5+ sources)
- **Robust Fallback**: Graceful degradation when LLM API unavailable with historically-accurate fallback content
- **Environment Configuration**: Proper dotenv loading for API keys

**✅ Real LLM Results Verified:**

- **Moon Landing (July 20, 1969)**: 156 words, 10 facts, surrealist/futuristic art style, NASA/History.com sources
- **Bitcoin Whitepaper (Oct 31, 2008)**: 140 words, 10 facts, cyberpunk art style, Bitcoin.org/Forbes sources
- **API Integration**: 1133-1162 tokens per request, structured JSON parsing working
- **Validation**: All requirements met per agents_spec.md (word counts, fact counts, HTTP sources, prompt_seed completeness)

**✅ Test Coverage:**

- `test_lore_agent.py`: Unit tests + real API integration + fallback behavior
- `test_lore_integration.py`: LangGraph workflow integration tests
- Environment variable loading with python-dotenv

### Phase 5.3: Artist Agent - Image Generation ✅ **COMPLETED**

_Generate real images using OpenAI gpt-image-1_

**✅ Implemented:**

- **Real Image Generation**: OpenAI gpt-image-1 API integration with 1536x1024 resolution
- **Prompt Engineering**: Dynamic prompt creation from LorePack.prompt_seed (style, palette, motifs, negative)
- **Local Storage**: Images saved to `temp_images/{run_id}/` directory for Phase 5.4 IPFS integration
- **Error Handling**: Graceful fallback to placeholder images when API fails
- **Performance Optimization**: 180-second timeout with detailed progress logging

**✅ Real Image Generation Verified:**

- **Moon Landing Test**: 4/4 images generated successfully in ~60-78s each
- **File Output**: 3-3.5MB PNG files with proper base64 decoding
- **Prompt Variations**: Each image uses different motifs from prompt_seed
- **Integration**: Seamlessly works with existing LangGraph workflow

**✅ Test Coverage:**

- `test_artist_image_gen.py`: Full integration test with real OpenAI API calls
- Verified local file creation and file size validation

### Phase 5.4: Artist Agent - IPFS Integration

_Pin real images to IPFS_

- Add MCP `pin_cid` calls for generated images
- Generate proper thumbnails with PIL/Pillow
- Implement size validation (<2MB images, <200KB thumbs)
- **Test**: Images pinned to IPFS, CIDs resolve correctly
- **Files**: `apps/backend/agents/artist.py`

### Phase 5.5: Real Vote Agent

_Replace vote simulation with MCP integration_

**Overall Objective:** Transform stubbed voting into real blockchain integration with live polling, user confirmation, and timeout fallback.

#### Phase 5.5.1: Enhanced Vote Agent with MCP Integration ⏳ **IN PROGRESS**

_Integrate real MCP start_vote + add vote transaction checkpoint_

**✅ Implementation Plan:**
- Replace stubbed vote creation with real MCP `start_vote` call
- Add `vote_tx_approval` checkpoint for user transaction confirmation  
- Return `PreparedTx` for frontend wallet signing
- Maintain two-agent structure: `vote_agent` (start) + `tally_vote_agent` (poll)
- **Test**: MCP `start_vote` returns real vote_id + valid PreparedTx
- **Files**: `apps/backend/agents/vote.py`

#### Phase 5.5.2: Vote Transaction Checkpoint Handler

_Add workflow checkpoint for vote transaction confirmation_

**📋 Tasks:**
- Add `interrupt_after=["vote"]` to LangGraph workflow
- Implement checkpoint resume handler for `vote_tx_approval`
- Frontend integration: transaction confirmation → `/resume` with tx_hash
- Update workflow state management for vote PreparedTx
- **Test**: Vote checkpoint interrupts workflow, resume advances to tally
- **Files**: `apps/backend/main.py`, `apps/frontend/components/AgentConsole.tsx`

#### Phase 5.5.3: Polling Tally Agent with Timeout Fallback

_Real-time vote status polling with async SSE updates_

**📋 Tasks:**
- Replace stubbed tally with real MCP `get_vote_status` polling (5s interval)
- Implement async polling loop with SSE streaming updates ("Vote in progress...")
- Add timeout fallback: if `ends_at` expired → pick index 0, record `fallback: true`  
- Call MCP `tally_vote` for natural completion or implement fallback logic
- **Test**: Live polling updates, timeout triggers fallback correctly
- **Files**: `apps/backend/agents/vote.py`

#### Phase 5.5.4: Frontend Vote Progress Integration

_UI for vote confirmation and live progress_

**📋 Tasks:**
- Add vote transaction confirmation modal with PreparedTx details
- Display "Vote in progress..." during polling phase
- Handle vote checkpoint resume flow
- Show final vote results with winner announcement
- **Test**: Full frontend flow from vote creation to completion
- **Files**: `apps/frontend/components/AgentConsole.tsx`, `apps/frontend/lib/api.ts`

#### Phase 5.5.5: Testing & Validation

_End-to-end validation of real voting integration_

**📋 Tasks:**
- Unit tests: Mock MCP responses, timeout logic, error handling
- Integration tests: Real MCP server interaction scenarios
- E2E test: Full workflow with actual vote creation → polling → completion
- Validate blockchain vote IDs match MCP responses
- **Test**: Complete voting flow works end-to-end on testnet
- **Files**: `apps/backend/test_vote_integration.py`

### Overall Phase 5.5 Acceptance Criteria

- ✅ **Real MCP Integration**: `start_vote`, `get_vote_status`, `tally_vote` all working
- ✅ **Live Polling**: Vote progress streams to frontend every 5 seconds  
- ✅ **Timeout Fallback**: Expires → pick index 0 with `fallback: true`
- ✅ **PreparedTx Flow**: User confirms vote transaction via wallet
- ✅ **Real Vote IDs**: Blockchain vote identifiers used throughout
- ✅ **Error Resilience**: Happy path assumption, graceful degradation

### Phase 5.6: Real Mint Agent

_Complete metadata + real minting_

- Build complete metadata per `docs/context/metadata_schema.md`
- Real MCP `pin_metadata` and `mint_final` calls
- Proper `tx_hash` and `token_id` handling
- **Test**: Real NFT minted with complete metadata
- **Files**: `apps/backend/agents/mint.py`

### Phase 5.7: Validation & Polish

_Enforce all acceptance criteria_

- Size limits, word counts, CID validation per `agents_spec.md`
- Error handling for API failures
- Feature flag cleanup (`ENABLE_STUB_ART=0`, `ENABLE_STUB_PIN=0`)
- **Test**: End-to-end with all validation rules

### Overall Acceptance Criteria

- **Lore**: Real research relevant to `date_label` input
- **Artist**: Real images generated from research-derived `prompt_seed`
- **Vote**: Blockchain integration with timeout fallback
- **Mint**: Complete metadata schema compliance with real data
- **Integration**: Token's `tokenURI` resolves to JSON with real `image` (ipfs://CID) and complete `properties`

---

## Phase 6 — Medals & Gasback

**Objective:** Reward voters and showcase Shape-native value.

### Tasks

- After `VoteClosed`, iterate voter addresses and call MCP `issue_medal` (PreparedTx → wallet signs).
- Agent Console prints medal tx links; UI shows **“Historian Voter”** badge with link.
- **Gasback panel**: poll `gasback_info(DropManager)` and display accrued/claimable (mock OK if needed).

### Acceptance Criteria

- Medal minted to each participant wallet; visible in UI.
- Gasback panel shows non-zero counter (mock or real).

---

## Phase 7 — (Optional) Attestation & Polish

**Objective:** Add verifiable endorsement semantics and UX friction polish.

### Tasks

- **Attestation Agent**: Build SIWE message client-side; sign; upload `{ message, signature, address }` JSON to IPFS; store `attestation_uri` in metadata.
- Add **`art_sanity`** checkpoint with “Regenerate once” button.
- Add quick-copy buttons for CIDs, tx hashes, tokenURI; add explorer links.

### Acceptance Criteria

- NFT `properties.attestation_uri` exists; link downloadable.
- UI shows clean, legible event feed with timestamps and links.

---

## Testing & Demo Runbook

### Tests

- **Contracts (Hardhat)**

  - open/close vote; finalizeMint; medal mint; allowlist gating.

- **Integration**

  - MCP `start_vote` → PreparedTx executable with viem; `pin_metadata` returns CID.

- **E2E**

  - Start run → approve lore → art → vote → finalize → tokenURI resolves → medal minted → links display.

### Demo Script (≤ 3 min)

1. Start run: “**2015-07-30 — Ethereum Genesis Block**”.
2. Approve Lore summary (edit one word to show HIL).
3. Show 4–6 images → Proceed.
4. Open vote (60–120s) → cast from two wallets → stream tally.
5. Close → Finalize mint → open tokenURI on IPFS.
6. Medal toast for voters; Gasback counter ticks.
7. (If enabled) Show `attestation_uri`.

---

## Branch/PR Plan

- `feat/contracts` → contracts + deploy + ABIs + addresses
- `feat/mcp-stubs` → MCP read/write tools, PreparedTx
- `feat/backend-orchestrator` → FastAPI + LangGraph + SSE + interrupts
- `feat/frontend-sse-ui` → Next.js UI + Agent Console + wallet + voting modal
- `feat/real-art-ipfs` → image gen + pinning; metadata per schema
- `feat/medals-gasback` → medal mint + panel
- `feat/attestation` → SIWE JSON → attestation_uri

Each PR should reference the relevant **spec files** in `docs/context` (Cursor rules will remind you).

---

## Environment & Config (Quick)

**Root `.env.example`**

```
# Frontend
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_MCP_URL=http://localhost:4000
NEXT_PUBLIC_RPC_URL=<SHAPE_TESTNET_RPC>
NEXT_PUBLIC_CHAIN_ID=<CHAIN_ID>

# Backend
BACKEND_PORT=8000
CHECKPOINTER_URL=sqlite:///state.db

# MCP
MCP_PORT=4000
IPFS_PIN_URL=<pinning service or stub>
IPFS_PIN_KEY=<token or empty>

# Contracts (loaded from addresses.json in code too)
CHAIN_ID=<...>
RPC_URL=<...>
DEPLOYER_PK=<never commit>
```

---

## Definition of Done (DoD)

- [ ] End-to-end flow on **Shape testnet** with real images and IPFS metadata.
- [ ] **SSE** updates render in Agent Console; reconnect survives reload.
- [ ] **Two mandatory checkpoints** enforced; irreversible actions only after `finalize_mint`.
- [ ] All writes via **PreparedTx**; **no server-side keys**.
- [ ] `addresses.json` + ABIs wired; env documented; `README` updated.
- [ ] Medal minted to voters; Gasback panel visible (mock or real).
- [ ] Demo script reproducible in ≤3 minutes.
