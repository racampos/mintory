# Attested History — Offline Context Pack

This folder contains authoritative, offline references for the Attested History project.
Everything here avoids live URLs or changing docs and includes placeholders (ALL_CAPS) to fill after deployment.

Files:

- shape_basics.md — What Shape is, network config, Gasback, Stack medals.
- gasback_and_stack.md — How to showcase Gasback and medals in the demo.
- mcp_tools_spec.md — Read/write tool contracts and example payloads.
- contracts_and_addresses.md — Network config, addresses.json schema, minimal ABIs you can hardcode.
- backend_api_spec.md — REST + SSE contract between frontend and the LangGraph orchestrator.
- langgraph_basics.md — State, checkpointers, interrupts, streaming patterns.
- agents_spec.md — Inputs/outputs/acceptance for Lore/Artist/Vote/Mint/Attest/Guard.
- prompts.md — Canonical prompts for Lore + Artist + Curator handoffs.
- frontend_ai_sdk.md — Vercel AI SDK usage (tool calls, generateObject), EventSource client.
- wallet_and_viem.md — PreparedTx pattern, chain switching, signing, safety rules.
- metadata_schema.md — NFT metadata JSON schema stored on IPFS.
- testing_plan.md — E2E and unit test scenarios (offline).
- env_and_configs.md — Required .env keys with examples and constraints.
- demo_script.md — 3-minute flow used in judging.
- security_and_licensing.md — What to avoid; model/license notes.

> Convention: Replace ALL_CAPS placeholders (e.g., `CHAIN_ID`, `DROP_MANAGER_ADDRESS`) once you deploy to Shape testnet.
