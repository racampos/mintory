# Shape Basics (Offline)

## What is Shape (for the assistant)

- EVM-compatible L2/sidechain with standard RPC.
- Supports NFTs (ERC-721/1155) and standard toolchains (viem/wagmi).
- We will deploy to **testnet**. Treat it like any EVM chain:
  - `CHAIN_ID`: <number> # FILL AFTER DEPLOY
  - `RPC_URL`: <https://...> # FILL AFTER DEPLOY
  - `EXPLORER_BASE`: <https://...> # FILL AFTER DEPLOY

## Dev assumptions (bake these into code)

- Gas token behaves like ETH.
- Block times: assume ~2–5s for UX.
- Finality: wait 1–2 confirmations for demo UI before declaring success.

## Primitives we showcase

- **Gasback**: a creator rebate on network fees. For demo: read accrued/eligible, show a counter in UI.
- **Stack / Medals**: achievement-like tokens to reward voters/curators. For demo, we mint our own ERC-1155 medal if native endpoints aren't available.

## Testnet posture

- It's acceptable to run the _entire_ demo on testnet.
- If explorers/analytics lag, the UI still links tokenURI IPFS and local state so judges see progress.

