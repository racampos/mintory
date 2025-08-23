import { createPublicClient, http, encodeFunctionData, getContract, parseEther } from 'viem';
import { defineChain } from 'viem';
import { NETWORK_CONFIG, ADDRESSES } from './config.js';
import { DropManagerAbi, HistorianMedalsAbi } from './abis.js';
import type { PreparedTx, VoteConfig } from './types.js';

// Define Shape network
const shapeNetwork = defineChain({
  id: NETWORK_CONFIG.CHAIN_ID,
  name: NETWORK_CONFIG.CHAIN_NAME,
  network: 'shape',
  nativeCurrency: {
    decimals: 18,
    name: 'Ethereum',
    symbol: 'ETH',
  },
  rpcUrls: {
    default: {
      http: [NETWORK_CONFIG.RPC_URL],
    },
    public: {
      http: [NETWORK_CONFIG.RPC_URL],
    },
  },
  blockExplorers: {
    default: { name: 'ShapeScan', url: NETWORK_CONFIG.EXPLORER_BASE },
  },
});

// Create public client
export const publicClient = createPublicClient({
  chain: shapeNetwork,
  transport: http(),
});

// Contract instances
export const dropManagerContract = getContract({
  address: ADDRESSES.DropManager as `0x${string}`,
  abi: DropManagerAbi,
  publicClient,
});

export const historianMedalsContract = getContract({
  address: ADDRESSES.HistorianMedals as `0x${string}`,
  abi: HistorianMedalsAbi,
  publicClient,
});

// Helper functions
export function mapVoteConfigToContractParams(cfg: VoteConfig) {
  const methodMap = { simple: 0 };
  const gateMap = { allowlist: 0, open: 1, passport_stub: 2 };

  return {
    method: methodMap[cfg.method],
    gate: gateMap[cfg.gate],
    duration: BigInt(cfg.duration_s),
    startTime: BigInt(Math.floor(Date.now() / 1000)),
    isOpen: true,
  };
}

export function createOpenVoteTx(cids: string[], cfg: VoteConfig): PreparedTx {
  const contractConfig = mapVoteConfigToContractParams(cfg);
  
  const data = encodeFunctionData({
    abi: DropManagerAbi,
    functionName: 'openVote',
    args: [cids, contractConfig],
  });

  return {
    to: ADDRESSES.DropManager as `0x${string}`,
    data,
  };
}

export function createCloseVoteTx(voteId: string): PreparedTx {
  const data = encodeFunctionData({
    abi: DropManagerAbi,
    functionName: 'closeVote',
    args: [voteId as `0x${string}`],
  });

  return {
    to: ADDRESSES.DropManager as `0x${string}`,
    data,
  };
}

export function createFinalizeMintTx(voteId: string, winnerCid: string, tokenURI: string): PreparedTx {
  const data = encodeFunctionData({
    abi: DropManagerAbi,
    functionName: 'finalizeMint',
    args: [voteId as `0x${string}`, winnerCid, tokenURI],
  });

  return {
    to: ADDRESSES.DropManager as `0x${string}`,
    data,
  };
}

export function createIssueMedalTx(toAddress: string, tokenId: number): PreparedTx {
  // Using mint function from HistorianMedals contract
  const data = encodeFunctionData({
    abi: HistorianMedalsAbi,
    functionName: 'mint',
    args: [toAddress as `0x${string}`, `ipfs://medal-${tokenId}`], // placeholder URI
  });

  return {
    to: ADDRESSES.HistorianMedals as `0x${string}`,
    data,
  };
}

// Gas estimation helper
export async function estimateGas(tx: PreparedTx): Promise<number> {
  try {
    const gas = await publicClient.estimateGas({
      to: tx.to as `0x${string}`,
      data: tx.data as `0x${string}`,
      value: tx.value ? BigInt(tx.value) : undefined,
      account: '0x0000000000000000000000000000000000000000', // Dummy account for estimation
    });
    return Number(gas);
  } catch (error) {
    console.warn('Gas estimation failed, using default:', error);
    return 100000; // Default gas limit
  }
}
