import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatAddress(address: string): string {
  if (!address) return '';
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

export function formatCid(cid: string): string {
  if (!cid) return '';
  if (cid.startsWith('ipfs://')) {
    const hash = cid.slice(7);
    return `${hash.slice(0, 8)}...${hash.slice(-8)}`;
  }
  return `${cid.slice(0, 8)}...${cid.slice(-8)}`;
}

export function getExplorerUrl(chainId: number, hash: string): string {
  // Shape testnet explorer
  if (chainId === 11011) {
    return `https://explorer.shape.network/tx/${hash}`;
  }
  return `https://etherscan.io/tx/${hash}`;
}

export function getIpfsUrl(cid: string): string {
  if (cid.startsWith('ipfs://')) {
    const hash = cid.slice(7);
    return `https://ipfs.io/ipfs/${hash}`;
  }
  return `https://ipfs.io/ipfs/${cid}`;
}
