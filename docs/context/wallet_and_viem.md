# Wallet, viem, and PreparedTx Pattern

## PreparedTx → send with viem

```ts
import { createWalletClient, custom } from "viem";

const client = createWalletClient({ transport: custom(window.ethereum) });

async function sendPreparedTx(tx: {
  to: string;
  data: string;
  value?: string;
}) {
  const [account] = await window.ethereum.request({
    method: "eth_requestAccounts",
  });
  const hash = await client.sendTransaction({
    to: tx.to as `0x${string}`,
    data: tx.data as `0x${string}`,
    value: tx.value as `0x${string}` | undefined,
    account,
  });
  return hash;
}
```

## Chain switching

- Detect `CHAIN_ID`; prompt user to switch/add network if mismatched.

## Safety

- Never pass private keys to backend.
- Display decoded calldata summary before signing (optional nice-to-have).

