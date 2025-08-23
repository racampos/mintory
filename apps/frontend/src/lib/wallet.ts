import { createWalletClient, custom, type Chain } from "viem";
import type { PreparedTx } from "./types";

// Shape testnet configuration
export const shapeTestnet: Chain = {
  id: 360,
  name: 'Shape Testnet',
  network: 'shape-testnet',
  nativeCurrency: {
    decimals: 18,
    name: 'Ether',
    symbol: 'ETH',
  },
  rpcUrls: {
    public: { http: ['https://testnet.rpc.shape.network'] },
    default: { http: ['https://testnet.rpc.shape.network'] },
  },
  blockExplorers: {
    default: { name: 'Shape Explorer', url: 'https://explorer.shape.network' },
  },
  testnet: true,
};

export class WalletManager {
  private client?: any;

  constructor() {
    if (typeof window !== 'undefined' && window.ethereum) {
      this.client = createWalletClient({
        chain: shapeTestnet,
        transport: custom(window.ethereum),
      });
    }
  }

  async connect(): Promise<`0x${string}`[]> {
    if (!window.ethereum) {
      throw new Error('No wallet found. Please install MetaMask.');
    }

    const accounts = await window.ethereum.request({
      method: 'eth_requestAccounts',
    });

    return accounts;
  }

  async switchToShapeTestnet(): Promise<void> {
    if (!window.ethereum) {
      throw new Error('No wallet found');
    }

    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: '0x168' }], // 360 in hex
      });
    } catch (error: any) {
      // Chain doesn't exist, add it
      if (error.code === 4902) {
        await window.ethereum.request({
          method: 'wallet_addEthereumChain',
          params: [{
            chainId: '0x168',
            chainName: 'Shape Testnet',
            rpcUrls: ['https://testnet.rpc.shape.network'],
            nativeCurrency: {
              name: 'Ether',
              symbol: 'ETH',
              decimals: 18,
            },
            blockExplorerUrls: ['https://explorer.shape.network'],
          }],
        });
      } else {
        throw error;
      }
    }
  }

  async sendTransaction(tx: PreparedTx): Promise<`0x${string}`> {
    if (!this.client) {
      throw new Error('Wallet not connected');
    }

    const [account] = await this.connect();
    
    const hash = await this.client.sendTransaction({
      to: tx.to,
      data: tx.data,
      value: tx.value,
      gas: tx.gas,
      account,
    });

    return hash;
  }

  async getChainId(): Promise<number> {
    if (!window.ethereum) {
      throw new Error('No wallet found');
    }

    const chainId = await window.ethereum.request({
      method: 'eth_chainId',
    });

    return parseInt(chainId, 16);
  }
}

// Global wallet instance
export const walletManager = typeof window !== 'undefined' ? new WalletManager() : null;
