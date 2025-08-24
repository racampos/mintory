import { config } from 'dotenv';
import { readFileSync } from 'fs';
import { join } from 'path';

config();

// Load addresses from local deployment file (Railway-compatible)
const addressesPath = join(process.cwd(), 'addresses.json');
export const ADDRESSES = JSON.parse(readFileSync(addressesPath, 'utf-8')) as {
  chainId: number;
  DropManager: string;
  HistorianMedals: string;
  NFT: string;
};

// Network configuration
export const NETWORK_CONFIG = {
  CHAIN_ID: ADDRESSES.chainId,
  RPC_URL: process.env.RPC_URL || 'https://shape-sepolia.g.alchemy.com/v2/lFQY2zhDOR9h_q3Z0CNTWMdLy7q8n692',
  EXPLORER_BASE: process.env.EXPLORER_BASE || 'https://sepolia.shapescan.xyz',
  CHAIN_NAME: 'Shape Network Sepolia',
} as const;

// Server configuration
export const SERVER_CONFIG = {
  PORT: process.env.PORT || 3001,
  CORS_ORIGINS: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:3000'],
} as const;

// IPFS configuration
export const IPFS_CONFIG = {
  GATEWAY: process.env.IPFS_GATEWAY || 'https://ipfs.io/ipfs',
} as const;
