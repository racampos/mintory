import { openai } from '@ai-sdk/openai';
import { streamText, tool } from 'ai';
import { z } from 'zod';

export const runtime = 'edge';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = await streamText({
    model: openai('gpt-4-turbo'),
    messages,
    tools: {
      get_chain_info: tool({
        description: 'Get blockchain network information',
        parameters: z.object({}),
        execute: async () => {
          // This will be handled by the client-side tool call
          return {};
        },
      }),
      
      get_gasback_info: tool({
        description: 'Get gasback information for a contract address',
        parameters: z.object({
          contract: z.string().describe('Contract address to check gasback for'),
        }),
        execute: async ({ contract }) => {
          // This will be handled by the client-side tool call
          return { contract };
        },
      }),
      
      get_user_medals: tool({
        description: 'Get medals owned by an address',
        parameters: z.object({
          address: z.string().describe('Wallet address to check medals for'),
        }),
        execute: async ({ address }) => {
          // This will be handled by the client-side tool call
          return { address };
        },
      }),
      
      get_vote_status: tool({
        description: 'Get the status of a vote',
        parameters: z.object({
          vote_id: z.string().describe('Vote ID to check status for'),
        }),
        execute: async ({ vote_id }) => {
          // This will be handled by the client-side tool call
          return { vote_id };
        },
      }),
    },
    system: `You are an AI curator for Shapecraft, an NFT creation platform. You help users:

1. Get information about the blockchain (chain info, gasback, medals)
2. Start new creation runs with historical date labels
3. Monitor the progress of creation runs

When users ask about blockchain data, use the available tools:
- get_chain_info: Get current blockchain network details
- get_gasback_info: Check gasback rewards for contracts  
- get_user_medals: Check medals owned by an address
- get_vote_status: Check voting status for active votes

Be helpful and informative. Explain what each piece of data means and how it relates to the Shapecraft platform.

For starting new runs, suggest interesting historical dates and explain how they will influence the AI art generation process.`,
  });

  return result.toAIStreamResponse();
}
