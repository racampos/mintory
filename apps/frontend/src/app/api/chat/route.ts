import { streamText, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

export const runtime = 'edge';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = await streamText({
    model: openai('gpt-4-turbo') as any,
    messages,
    maxToolRoundtrips: 5, // Allow multiple tool calls and responses
    tools: {
      get_chain_info: tool({
        description: 'Get blockchain network information',
        parameters: z.object({}),
        execute: async () => {
          console.log('[Chat API] get_chain_info tool called on server');
          try {
            const mcpUrl = `${process.env.MCP_URL || 'http://localhost:3001'}/mcp/chain_info`;
            console.log('[Chat API] Fetching from:', mcpUrl);
            
            const response = await fetch(mcpUrl);
            if (!response.ok) {
              throw new Error(`MCP request failed: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('[Chat API] MCP response:', data);
            return data;
          } catch (error) {
            console.error('[Chat API] MCP request failed:', error);
            return { error: 'Failed to fetch chain information' };
          }
        },
      }),
      
      get_gasback_info: tool({
        description: 'Get gasback information for a contract address',
        parameters: z.object({
          contract: z.string().describe('Contract address to check gasback for'),
        }),
        execute: async ({ contract }) => {
          console.log('[Chat API] get_gasback_info tool called with contract:', contract);
          try {
            const mcpUrl = `${process.env.MCP_URL || 'http://localhost:3001'}/mcp/gasback_info?contract=${encodeURIComponent(contract)}`;
            console.log('[Chat API] Fetching from:', mcpUrl);
            
            const response = await fetch(mcpUrl);
            if (!response.ok) {
              throw new Error(`MCP request failed: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('[Chat API] MCP response:', data);
            return data;
          } catch (error) {
            console.error('[Chat API] MCP request failed:', error);
            return { error: 'Failed to fetch gasback information' };
          }
        },
      }),
      
      get_user_medals: tool({
        description: 'Get medals owned by an address',
        parameters: z.object({
          address: z.string().describe('Wallet address to check medals for'),
        }),
        execute: async ({ address }) => {
          console.log('[Chat API] get_user_medals tool called with address:', address);
          try {
            const mcpUrl = `${process.env.MCP_URL || 'http://localhost:3001'}/mcp/medal_of?address=${encodeURIComponent(address)}`;
            console.log('[Chat API] Fetching from:', mcpUrl);
            
            const response = await fetch(mcpUrl);
            if (!response.ok) {
              throw new Error(`MCP request failed: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('[Chat API] MCP response:', data);
            return data;
          } catch (error) {
            console.error('[Chat API] MCP request failed:', error);
            return { error: 'Failed to fetch medal information' };
          }
        },
      }),
      
      get_vote_status: tool({
        description: 'Get the status of a vote',
        parameters: z.object({
          vote_id: z.string().describe('Vote ID to check status for'),
        }),
        execute: async ({ vote_id }) => {
          console.log('[Chat API] get_vote_status tool called with vote_id:', vote_id);
          try {
            const mcpUrl = `${process.env.MCP_URL || 'http://localhost:3001'}/mcp/vote_status?vote_id=${encodeURIComponent(vote_id)}`;
            console.log('[Chat API] Fetching from:', mcpUrl);
            
            const response = await fetch(mcpUrl);
            if (!response.ok) {
              throw new Error(`MCP request failed: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('[Chat API] MCP response:', data);
            return data;
          } catch (error) {
            console.error('[Chat API] MCP request failed:', error);
            return { error: 'Failed to fetch vote status' };
          }
        },
      }),
    },
    system: `You are an AI curator for Shapecraft, an NFT creation platform. You help users:

1. Get information about the blockchain (chain info, gasback, medals)
2. Start new creation runs with historical date labels
3. Monitor the progress of creation runs

WORKFLOW: When users ask questions requiring blockchain data:
1. Use the appropriate tool to get the data
2. ALWAYS continue with a conversational response interpreting the results
3. Never stop after just calling a tool - always provide analysis

Available tools:
- get_chain_info: Get current blockchain network details
- get_gasback_info: Check gasback rewards for contracts  
- get_user_medals: Check medals owned by an address
- get_vote_status: Check voting status for active votes

RESPONSE FORMAT: After calling a tool, ALWAYS follow up with natural language. Examples:

User: "What chain are we on?"
- Call get_chain_info
- Respond: "You are currently connected to Shape Network (Chain ID: 11011). This is Shapecraft's primary blockchain for NFT creation and gasback rewards."

User: "Check gasback for contract 0x123..."
- Call get_gasback_info  
- Respond: "This contract has 0 ETH accrued in gasback rewards, with 0 ETH currently claimable. Gasback rewards accumulate when users interact with Shape Network contracts."

User: "What medals do I have?"
- Call get_user_medals
- Respond: "This address owns 2 Historian medals" OR "This address doesn't have any medals yet. You can earn medals by participating in Shapecraft votes and minting activities."

CRITICAL: Always provide context and explanation after tool results. Help users understand what the data means for their Shapecraft experience.`,
  });

  return result.toAIStreamResponse();
}
