# Mintory: Make history mintable

> **One-liner:** _AI researches the story, the community picks the art, and Shape mints the memory._

**🎥 [Watch the 3-minute demo](https://youtu.be/LG9ovU99eD8?si=AeQ47qKMF85ZVY7U)** — See the full pipeline in action from lore generation to NFT mint!

---

## Why this exists (storytelling & vision)

History isn’t just dates—it’s shared meaning. Mintory began as **“Historic Dates as NFTs endorsed by the people who lived them.”** As we iterated, we realized the real value isn’t a celebrity shout-out—it’s **provable provenance**: a transparent pipeline that turns **facts → narrative → artwork → community choice → on-chain artifact**.

Our vision is a **public provenance layer for culture**: each mint is the visible tip of a verifiable process. We want people to _see_ why an image represents a moment—what sources informed it, which community chose it, and how it was put on chain.

---

## What we shipped during the hackathon

We executed the **entire pipeline on Shape testnet**:

1. **Lore** → an AI agent composes a concise, source-backed summary for a chosen date/topic.
2. **Image generation** → an “Artist” agent produces 4–6 candidate artworks and pins them.
3. **Voting setup** → a “Vote” agent opens an on-chain vote with the candidates.
4. **Voting process** → allowlisted wallets cast 1p1v votes; the UI streams the tally.
5. **Finalization & mint** → the winning artwork is bound to rich metadata (summary, sources, prompt seed) and **minted as an ERC-721**.

**Result:** One click → narrative drafted → art proposed → community chooses → **NFT minted with receipts** (CIDs, tx hashes, tokenURI).

**🎬 [See it in action](https://youtu.be/LG9ovU99eD8?si=AeQ47qKMF85ZVY7U)** — Full demo walkthrough from start to finish.

---

## 🎥 Demo Video

[![Mintory Demo - 3 minute walkthrough](https://img.youtube.com/vi/LG9ovU99eD8/maxresdefault.jpg)](https://youtu.be/LG9ovU99eD8?si=AeQ47qKMF85ZVY7U)

**[▶️ Watch the 3-minute demo](https://youtu.be/LG9ovU99eD8?si=AeQ47qKMF85ZVY7U)**

See the complete pipeline in action: from historical research through AI art generation, community voting, to final NFT mint with full provenance on Shape testnet.

---

## The experience (what a user does)

1. Pick a historic date / moment.
2. Review and approve the **Lore** (short neutral summary + facts + source links).
3. View **art proposals** and open voting.
4. Participate in the **on-chain vote**.
5. **Finalize** the mint of the winning artwork; get IPFS & explorer links.

We optimized for a **three-minute demo**: clear steps, visible receipts, minimal ceremony.

> **🎥 Want to see the UX?** [Watch the demo video](https://youtu.be/LG9ovU99eD8?si=AeQ47qKMF85ZVY7U) to experience the full user journey.

---

## How it works (architecture at a glance)

```
User ──▶ Orchestrator (LangGraph)
         ├─ 🧠 Lore Agent: builds LorePack {summary_md, facts[], sources[], prompt_seed}
         ├─ 🎨 Artist Agent: generates ArtSet {cids[], thumbs[], style_notes[]}
         ├─ 🗳 Vote Agent: opens & monitors the vote (allowlist, 1p1v, short window)
         └─ 🪙 Mint Agent: pins metadata JSON → mints ERC-721 with tokenURI
```

- **Backend:** Python **LangGraph** orchestrator with **REST + SSE**, checkpoints at _lore approval_, _vote tx approval_, and _finalize mint_.
- **Frontend:** Next.js + Vercel AI SDK; an event feed ("Agent Console") streams progress and links (CIDs, txs, tokenURI).
- **MCP Server (Tool API):** HTTP server for IPFS pinning & blockchain calldata preparation; browser wallet signs via **viem/wagmi**.
- **Contracts (used in demo):**

  - `DropManager.sol` — opens/closes votes & coordinates with `HistorianMedals` for the actual mint.
  - `HistorianMedals.sol` — ERC-721 contract that mints the commemorative NFTs (called by `DropManager`).

---

## What’s special (technical highlights)

- **Explicit multi-agent design** with typed IO (LorePack, ArtSet, VoteResult).
- **Human-in-the-loop** at the points that matter (taste & irreversible actions).
- **Deterministic provenance**: metadata stores the **summary, sources, and prompt seed** that produced the winning art.
- **PreparedTx pattern**: servers never hold keys; the wallet signs everything.
- **Simple, reliable voting** for the hackathon (allowlist + 1p1v + timeout fallback).

---

## Curator agent (status: **partially implemented**)

We built a **partial Curator agent** that narrates progress and surfaces approvals, tied to the backend run via SSE.
**What’s missing:** richer chat UX, tool-driven summaries, and inline forms for edits.
**Why it matters:** it’s the _front-of-house producer_—the user-facing “voice” that turns a complex pipeline into a guided experience.

---

## What we didn’t finish (and what’s next)

1. **Curator agent — complete the experience**

   - _Next:_ finalize a chat-first UI (Vercel AI SDK) wired to `/resume` decisions, with clear “Approve / Edit / Finalize” controls and copy-ready receipts.

2. **Participation Medals — reward voters**

   - _Plan:_ Additional ERC-1155 contract or `HistorianMedals` extension to mint **participation medals** (e.g., "Historian Voter") to all participants after `VoteClosed`; cheap to airdrop, optionally soulbound.
   - _UI:_ medal panel + explorer links.

3. **Attestation — cryptographic endorsements**

   - _Plan:_ Client-side SIWE JSON pinned to IPFS and referenced in metadata; later, an EAS schema for verifiable endorsements & revocation.

**Longer-term roadmap**

- Sybil-resistant gates (Passport/VCs); quadratic voting.
- Gasback integration & live accrual panel.
- Public indexer page per drop with all proofs.
- Charity rails & compliance for cause-based drops.
- Curated datasets + model cards for image generation transparency.

---

## Quickstart (dev)

> Testnet only; addresses & env values are placeholders.

**Prerequisites:** Node.js 18+, Python 3.9+, MetaMask or compatible wallet

```bash
# 1) Contracts (Hardhat) - Deploy first to get addresses
cd packages/contracts
npm i
npx hardhat compile
npm run deploy-testnet  # deploys to shapetestnet and exports ABIs
# This creates infra/deploy/addresses.json needed by other services

# 2) MCP Server (Tool API) - Start second
cd packages/mcp-server
npm i
cp addresses.json.example addresses.json  # then update with deployed addresses
npm run dev  # runs on http://localhost:3001

# 3) Backend orchestrator (FastAPI + LangGraph) - Start third
cd apps/backend
pip install -r requirements.txt
# Copy env.template to .env and configure OPENAI_API_KEY
uvicorn main:app --reload --port 8000

# 4) Frontend (Next.js) - Start last
cd apps/frontend
npm i
# Create .env.local with environment variables (see below)
npm run dev  # runs on http://localhost:3002
```

**Env essentials**

```
# Frontend (.env.local in apps/frontend)
NEXT_PUBLIC_CHAIN_ID=11011
BACKEND_URL=http://localhost:8000
MCP_URL=http://localhost:3001

# Backend (.env in apps/backend)
OPENAI_API_KEY=your_openai_key
BACKEND_PORT=8000

# MCP Server (.env in packages/mcp-server)
PORT=3001
RPC_URL=https://shape-sepolia.g.alchemy.com/v2/your_alchemy_key
CORS_ORIGINS=http://localhost:3002
```

---

## Data & metadata (what’s in the token)

```json
{
  "name": "Ethereum Genesis Block — 2015-07-30",
  "description": "Commemorative NFT curated by agents and chosen on-chain.",
  "image": "ipfs://<winner_cid>",
  "attributes": [
    { "trait_type": "Date", "value": "2015-07-30" },
    { "trait_type": "WinnerCID", "value": "<winner_cid>" },
    { "trait_type": "Sources", "value": "6" }
  ],
  "properties": {
    "summary_md": "<200-word neutral summary>",
    "sources": ["https://...", "https://..."],
    "prompt_seed": { "style": "...", "palette": "...", "motifs": ["..."] },
    "attestation_uri": "ipfs://<siwe.json> (future)"
  }
}
```

---

## Philosophy & guardrails

- **Provenance over hype:** value comes from _how_ the artifact was made and proved.
- **Transparency by default:** pin the prompts, sources, and decisions that shaped the outcome.
- **Human agency matters:** agents propose; people approve and own the irreversible steps.
- **Ethics:** positive portrayals of people; clear model/licensing notes; no server-side keys.

---

## Credits & acknowledgments

- **Project:** **Mintory** (Mint + History).
- **Origin:** “Historic Dates as NFTs,” reimagined as a verifiable, community-curated process.
- **Hackathon:** Shapecraft (Shape Network).
- **Open source:** OpenZeppelin, viem/wagmi, LangGraph, Next.js, Vercel AI SDK.

---

## Contact

If you want to collaborate on the Curator agent, medals, or attestations—or bring a historical drop to life—reach out. Mintory aims to become a shared provenance layer for cultural memory.
