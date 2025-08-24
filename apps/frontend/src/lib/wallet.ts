import { createWalletClient, createPublicClient, custom, http, type Chain, parseEventLogs, getContract } from "viem";
import type { PreparedTx } from "./types";

// DropManager ABI (minimal - just for vote events)
const dropManagerABI = [
  {
    "type": "function",
    "name": "openVote",
    "inputs": [
      {
        "name": "artCids",
        "type": "string[]"
      },
      {
        "name": "config",
        "type": "tuple",
        "components": [
          {"name": "method", "type": "uint8"},
          {"name": "gate", "type": "uint8"}, 
          {"name": "duration_s", "type": "uint256"},
          {"name": "startTime", "type": "uint256"},
          {"name": "isOpen", "type": "bool"}
        ]
      }
    ],
    "outputs": [
      {
        "name": "voteId",
        "type": "bytes32"
      }
    ],
    "stateMutability": "nonpayable"
  },
  {
    "type": "error",
    "name": "VoteNotFound",
    "inputs": [
      {
        "name": "voteId",
        "type": "bytes32"
      }
    ]
  },
  {
    "type": "event",
    "name": "VoteOpened",
    "inputs": [
      {
        "name": "voteId",
        "type": "bytes32",
        "indexed": true
      },
      {
        "name": "cids",
        "type": "string[]",
        "indexed": false
      },
      {
        "name": "config",
        "type": "tuple",
        "indexed": false,
        "components": [
          {"name": "method", "type": "uint8"},
          {"name": "gate", "type": "uint8"},
          {"name": "duration_s", "type": "uint256"},
          {"name": "startTime", "type": "uint256"},
          {"name": "isOpen", "type": "bool"}
        ]
      }
    ]
  }
] as const;

// Shape testnet configuration
export const shapeTestnet: Chain = {
  id: 11011,
  name: 'Shape Testnet',
  nativeCurrency: {
    decimals: 18,
    name: 'Ether',
    symbol: 'ETH',
  },
  rpcUrls: {
    public: { http: ['https://shape-sepolia.g.alchemy.com/v2/lFQY2zhDOR9h_q3Z0CNTWMdLy7q8n692'] },
    default: { http: ['https://shape-sepolia.g.alchemy.com/v2/lFQY2zhDOR9h_q3Z0CNTWMdLy7q8n692'] },
  },
  blockExplorers: {
    default: { name: 'Shape Explorer', url: 'https://explorer.shape.network' },
  },
  testnet: true,
};

export class WalletManager {
  private client?: any;
  private publicClient;

  constructor() {
    // Create public client for reading blockchain data
    this.publicClient = createPublicClient({
      chain: shapeTestnet,
      transport: http('https://shape-sepolia.g.alchemy.com/v2/lFQY2zhDOR9h_q3Z0CNTWMdLy7q8n692'),
    });

    if (typeof window !== 'undefined' && window.ethereum) {
      this.client = createWalletClient({
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
        params: [{ chainId: '0x2B03' }], // 11011 in hex
      });
    } catch (error: any) {
      // Chain doesn't exist, add it
      if (error.code === 4902) {
        await window.ethereum.request({
          method: 'wallet_addEthereumChain',
          params: [{
            chainId: '0x2B03',
            chainName: 'Shape Testnet',
            rpcUrls: ['https://shape-sepolia.g.alchemy.com/v2/lFQY2zhDOR9h_q3Z0CNTWMdLy7q8n692'],
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
      value: tx.value || "0x0",  // Convert null/undefined to "0x0"
      gas: tx.gas,
      account,
      chain: shapeTestnet,  // Provide chain context for the transaction
    });

    return hash;
  }

  /**
   * Wait for transaction receipt and extract vote ID if it's a vote transaction
   */
  async waitForTransactionAndExtractVoteId(txHash: string): Promise<{ txHash: string; voteId?: string }> {
    console.log('🔍 Waiting for transaction receipt:', txHash);
    
    try {
      // Wait for transaction receipt
      const receipt = await this.publicClient.waitForTransactionReceipt({ 
        hash: txHash as `0x${string}`,
        timeout: 60_000, // 60 second timeout
      });

      console.log('📄 Transaction receipt received:', receipt);

      // Try to parse vote events from the receipt
      try {
        const logs = parseEventLogs({
          abi: dropManagerABI,
          logs: receipt.logs,
        });

        console.log('📊 Parsed logs:', logs);

        // Look for VoteOpened event
        const voteOpenedEvent = logs.find(log => log.eventName === 'VoteOpened');
        console.log('🔍 VoteOpened event found:', voteOpenedEvent);
        
        if (voteOpenedEvent && voteOpenedEvent.args) {
          const voteId = voteOpenedEvent.args.voteId as string;
          console.log('🗳️ Extracted vote ID:', voteId);
          console.log('📦 Returning:', { txHash, voteId });
          return { txHash, voteId };
        } else {
          console.warn('⚠️ VoteOpened event not found or missing args');
        }
      } catch (parseError) {
        console.warn('⚠️ Could not parse vote events from receipt:', parseError);
        // This might not be a vote transaction, or the ABI might not match
      }

      // Return just the tx hash if no vote ID found
      return { txHash };

    } catch (error) {
      console.error('❌ Failed to get transaction receipt:', error);
      throw new Error(`Transaction receipt timeout or failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
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
