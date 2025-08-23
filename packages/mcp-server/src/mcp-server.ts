#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';

// Import our existing functionality
import { NETWORK_CONFIG, ADDRESSES } from './config.js';
import { 
  createOpenVoteTx, 
  createFinalizeMintTx, 
  createIssueMedalTx, 
  dropManagerContract,
  historianMedalsContract,
  estimateGas 
} from './blockchain.js';
import { pinJSON, pinFile, pinFromUrl } from './ipfs.js';
import {
  StartVoteRequestSchema,
  TallyVoteRequestSchema,
  MintFinalRequestSchema,
  IssueMedalRequestSchema,
  type ChainInfo,
  type GasbackInfo,
  type MedalsResponse,
  type VoteStatus,
  type TallyResult,
  type PinResult,
} from './types.js';

class ShapeCraftMCPServer {
  private server: Server;

  constructor() {
    this.server = new Server(
      {
        name: 'shapecraft-mcp-server',
        version: '0.1.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    this.setupErrorHandling();
  }

  private setupErrorHandling(): void {
    this.server.onerror = (error) => {
      console.error('[MCP Error]', error);
    };

    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  private setupToolHandlers(): void {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'get_chain_info',
            description: 'Get blockchain network information',
            inputSchema: {
              type: 'object',
              properties: {},
              required: [],
            },
          },
          {
            name: 'get_gasback_info',
            description: 'Get gasback information for a contract',
            inputSchema: {
              type: 'object',
              properties: {
                contract: {
                  type: 'string',
                  description: 'Contract address to check gasback for',
                },
              },
              required: ['contract'],
            },
          },
          {
            name: 'get_user_medals',
            description: 'Get medals owned by an address',
            inputSchema: {
              type: 'object',
              properties: {
                address: {
                  type: 'string',
                  description: 'Wallet address to check medals for',
                },
              },
              required: ['address'],
            },
          },
          {
            name: 'pin_metadata_to_ipfs',
            description: 'Pin JSON metadata to IPFS',
            inputSchema: {
              type: 'object',
              properties: {
                metadata: {
                  type: 'object',
                  description: 'JSON metadata to pin',
                },
              },
              required: ['metadata'],
            },
          },
          {
            name: 'create_vote_transaction',
            description: 'Create a transaction to start a vote',
            inputSchema: {
              type: 'object',
              properties: {
                artCids: {
                  type: 'array',
                  items: { type: 'string' },
                  description: 'Array of art CIDs to vote on',
                },
                cfg: {
                  type: 'object',
                  properties: {
                    method: { type: 'string', enum: ['simple'] },
                    gate: { type: 'string', enum: ['allowlist', 'open', 'passport_stub'] },
                    duration_s: { type: 'number' },
                  },
                  required: ['method', 'gate', 'duration_s'],
                },
              },
              required: ['artCids', 'cfg'],
            },
          },
          {
            name: 'get_vote_status',
            description: 'Get the status of a vote',
            inputSchema: {
              type: 'object',
              properties: {
                vote_id: {
                  type: 'string',
                  description: 'Vote ID to check status for',
                },
              },
              required: ['vote_id'],
            },
          },
          {
            name: 'tally_vote',
            description: 'Get vote tallies and determine winner',
            inputSchema: {
              type: 'object',
              properties: {
                vote_id: {
                  type: 'string',
                  description: 'Vote ID to tally',
                },
              },
              required: ['vote_id'],
            },
          },
          {
            name: 'create_mint_transaction',
            description: 'Create a transaction to finalize an NFT mint',
            inputSchema: {
              type: 'object',
              properties: {
                winner_cid: {
                  type: 'string',
                  description: 'CID of the winning art',
                },
                metadataCid: {
                  type: 'string',
                  description: 'CID of the metadata',
                },
              },
              required: ['winner_cid', 'metadataCid'],
            },
          },
          {
            name: 'create_medal_transaction',
            description: 'Create a transaction to issue a medal',
            inputSchema: {
              type: 'object',
              properties: {
                toAddress: {
                  type: 'string',
                  description: 'Address to issue medal to',
                },
                id: {
                  type: 'number',
                  description: 'Medal ID to issue',
                },
              },
              required: ['toAddress', 'id'],
            },
          },
        ],
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'get_chain_info':
            return await this.handleGetChainInfo();

          case 'get_gasback_info':
            return await this.handleGetGasbackInfo(args);

          case 'get_user_medals':
            return await this.handleGetUserMedals(args);

          case 'pin_metadata_to_ipfs':
            return await this.handlePinMetadata(args);

          case 'create_vote_transaction':
            return await this.handleCreateVoteTransaction(args);

          case 'get_vote_status':
            return await this.handleGetVoteStatus(args);

          case 'tally_vote':
            return await this.handleTallyVote(args);

          case 'create_mint_transaction':
            return await this.handleCreateMintTransaction(args);

          case 'create_medal_transaction':
            return await this.handleCreateMedalTransaction(args);

          default:
            throw new McpError(
              ErrorCode.MethodNotFound,
              `Unknown tool: ${name}`
            );
        }
      } catch (error) {
        if (error instanceof McpError) {
          throw error;
        }
        
        throw new McpError(
          ErrorCode.InternalError,
          `Error executing tool ${name}: ${error}`
        );
      }
    });
  }

  private async handleGetChainInfo() {
    const chainInfo: ChainInfo = {
      chainId: NETWORK_CONFIG.CHAIN_ID,
      name: NETWORK_CONFIG.CHAIN_NAME,
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(chainInfo, null, 2),
        },
      ],
    };
  }

  private async handleGetGasbackInfo(args: any) {
    const contract = args.contract;
    if (!contract) {
      throw new McpError(ErrorCode.InvalidParams, 'Missing contract parameter');
    }

    // For demo purposes, return mock data
    const gasbackInfo: GasbackInfo = {
      accrued: '0',
      claimable: '0',
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(gasbackInfo, null, 2),
        },
      ],
    };
  }

  private async handleGetUserMedals(args: any) {
    const address = args.address;
    if (!address) {
      throw new McpError(ErrorCode.InvalidParams, 'Missing address parameter');
    }

    try {
      const tokens = await historianMedalsContract.read.tokensOfOwner([address as `0x${string}`]);
      
      const medals = tokens.map((tokenId) => ({
        id: tokenId.toString(),
        balance: '1',
      }));

      const response: MedalsResponse = { medals };

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(response, null, 2),
          },
        ],
      };
    } catch (error) {
      // Return empty array if contract call fails
      const response: MedalsResponse = { medals: [] };
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(response, null, 2),
          },
        ],
      };
    }
  }

  private async handlePinMetadata(args: any) {
    const metadata = args.metadata;
    if (!metadata) {
      throw new McpError(ErrorCode.InvalidParams, 'Missing metadata parameter');
    }

    try {
      const result = await pinJSON(metadata);
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new McpError(ErrorCode.InternalError, `Failed to pin metadata: ${error}`);
    }
  }

  private async handleCreateVoteTransaction(args: any) {
    try {
      const parsed = StartVoteRequestSchema.parse(args);
      
      const tx = createOpenVoteTx(parsed.artCids, parsed.cfg);
      tx.gas = await estimateGas(tx);

      // Generate mock vote ID for response
      const vote_id = `0x${'0'.repeat(64)}`;

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              vote_id,
              tx,
            }, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new McpError(ErrorCode.InvalidParams, `Invalid vote parameters: ${error}`);
    }
  }

  private async handleGetVoteStatus(args: any) {
    const voteId = args.vote_id;
    if (!voteId) {
      throw new McpError(ErrorCode.InvalidParams, 'Missing vote_id parameter');
    }

    try {
      const voteData = await dropManagerContract.read.getVote([voteId as `0x${string}`]);
      const [cids, config, voteCounts, totalVotes, winnerCid, finalized] = voteData;
      
      const response: VoteStatus = {
        open: config.isOpen && !finalized,
        tallies: voteCounts.map(count => Number(count)),
        endsAt: new Date((Number(config.startTime) + Number(config.duration)) * 1000).toISOString(),
      };

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(response, null, 2),
          },
        ],
      };
    } catch (error) {
      // Return mock data if contract call fails
      const response: VoteStatus = {
        open: false,
        tallies: [],
        endsAt: new Date().toISOString(),
      };

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(response, null, 2),
          },
        ],
      };
    }
  }

  private async handleTallyVote(args: any) {
    try {
      const parsed = TallyVoteRequestSchema.parse(args);
      
      try {
        const voteData = await dropManagerContract.read.getVote([parsed.vote_id as `0x${string}`]);
        const [cids, config, voteCounts] = voteData;
        
        // Find winner (highest vote count)
        let winnerIndex = 0;
        let maxVotes = 0;
        const tally: Record<string, number> = {};
        
        voteCounts.forEach((count, index) => {
          const votes = Number(count);
          tally[index.toString()] = votes;
          if (votes > maxVotes) {
            maxVotes = votes;
            winnerIndex = index;
          }
        });

        const result: TallyResult = {
          winner_cid: cids[winnerIndex] || '',
          tally,
        };

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      } catch (contractError) {
        // Return mock data if contract call fails
        const result: TallyResult = {
          winner_cid: 'ipfs://mock-winner-cid',
          tally: { '0': 1 },
        };

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }
    } catch (error) {
      throw new McpError(ErrorCode.InvalidParams, `Invalid tally parameters: ${error}`);
    }
  }

  private async handleCreateMintTransaction(args: any) {
    try {
      const parsed = MintFinalRequestSchema.parse(args);
      
      // For this endpoint, we need a vote_id to finalize
      const mockVoteId = '0x' + '0'.repeat(64);
      
      const tx = createFinalizeMintTx(mockVoteId, parsed.winner_cid, parsed.metadataCid);
      tx.gas = await estimateGas(tx);

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ tx }, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new McpError(ErrorCode.InvalidParams, `Invalid mint parameters: ${error}`);
    }
  }

  private async handleCreateMedalTransaction(args: any) {
    try {
      const parsed = IssueMedalRequestSchema.parse(args);
      
      const tx = createIssueMedalTx(parsed.toAddress, parsed.id);
      tx.gas = await estimateGas(tx);

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ tx }, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new McpError(ErrorCode.InvalidParams, `Invalid medal parameters: ${error}`);
    }
  }

  async run(): Promise<void> {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('ShapeCraft MCP server running on stdio');
  }
}

const server = new ShapeCraftMCPServer();
server.run().catch(console.error);

