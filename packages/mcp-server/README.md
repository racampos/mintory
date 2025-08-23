# MCP Server

HTTP server implementing MCP (Model Context Protocol) tools for ShapeCraft2.

## Overview

This server provides read and write tools for interacting with the ShapeCraft2 contracts and IPFS, following the specification in `docs/context/mcp_tools_spec.md`.

## Features

### Read Tools

- `GET /mcp/chain_info` - Get chain information
- `GET /mcp/gasback_info?contract=ADDRESS` - Get gasback information
- `GET /mcp/medal_of?address=ADDRESS` - Get user's medals

### Write Tools

- `POST /mcp/pin_cid` - Pin content to IPFS
- `POST /mcp/pin_metadata` - Pin JSON metadata to IPFS
- `POST /mcp/start_vote` - Create vote transaction
- `GET /mcp/vote_status?vote_id=BYTES32` - Get vote status
- `POST /mcp/tally_vote` - Tally vote results
- `POST /mcp/mint_final` - Create final mint transaction
- `POST /mcp/issue_medal` - Create medal issuance transaction

All write tools return `PreparedTx` objects that can be signed by the frontend wallet.

## Setup

1. Install dependencies:

```bash
npm install
```

2. Create `.env` file from example:

```bash
cp .env.example .env
```

3. Start development server:

```bash
npm run dev
```

4. Build for production:

```bash
npm run build
npm start
```

## Configuration

The server uses:

- Contract addresses from `../../infra/deploy/addresses.json`
- ABIs from `../../packages/contracts/abi/`
- Environment variables for network and server config

## API Documentation

See `docs/context/mcp_tools_spec.md` for detailed API specifications.

## Environment Variables

For Phase 2 development, enable IPFS stubs:

```bash
ENABLE_STUB_PIN=1
```

This will make `/mcp/pin_cid` and `/mcp/pin_metadata` return fake CIDs like `ipfs://FAKE_abc123` instead of attempting real IPFS pinning.
