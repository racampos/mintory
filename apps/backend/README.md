# Attested History Backend

FastAPI + LangGraph orchestrator for the multi-agent NFT curation system.

## Features

- **LangGraph Orchestration**: Multi-agent workflow with checkpoints
- **SQLite Checkpointer**: Persistent state management
- **REST API**: Control plane for run management
- **SSE Streaming**: Real-time updates via Server-Sent Events
- **Interrupts**: Human approval gates at key decision points

## Architecture

```
POST /runs → Start Run → Lore Agent → [checkpoint] → Artist Agent → Vote Agent → Tally → [checkpoint] → Mint Agent → End
                                        ↑                                                        ↑
                                   lore_approval                                          finalize_mint
```

## API Endpoints

- `POST /runs` - Start new orchestration run
- `GET /runs/{id}` - Get current run state
- `GET /runs/{id}/stream` - SSE stream of run updates
- `POST /runs/{id}/resume` - Resume after checkpoint approval
- `GET /health` - Health check

## Setup

1. Install dependencies:

```bash
cd apps/backend
pip install -r requirements.txt
```

2. Set environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run the server:

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Agents

### Lore Agent

- **Input**: `date_label`
- **Output**: `LorePack` (summary, facts, sources, prompt_seed)
- **Checkpoint**: `lore_approval` - human can edit/approve

### Artist Agent

- **Input**: `LorePack`
- **Output**: `ArtSet` (CIDs, thumbnails, style_notes)
- **Note**: Stub implementation with placeholder CIDs

### Vote Agent

- **Input**: `ArtSet`, `VoteConfig`
- **Output**: `VoteState` with vote ID
- **Integration**: Uses MCP tools for blockchain interaction

### Mint Agent

- **Input**: `LorePack`, `winner_cid`
- **Output**: `MintReceipt` (tx_hash, token_id, token_uri)
- **Checkpoint**: `finalize_mint` - human confirms irreversible action

## Streaming

The `/runs/{id}/stream` endpoint provides Server-Sent Events with:

```json
{
  "event": "update",
  "data": {
    "run_id": "abc123",
    "agent": "Lore",
    "level": "info",
    "message": "Generated historical context",
    "links": [{ "label": "Source 1", "href": "https://..." }]
  }
}
```

## Development

- Agents are in `agents/` directory
- State definitions in `state.py`
- Main FastAPI app in `main.py`
- SQLite database created automatically as `state.db`

## Integration

- **Frontend**: Next.js app consumes REST API and SSE stream
- **MCP Server**: Blockchain operations via MCP tools
- **Contracts**: Shape testnet deployment via MCP prepared transactions
