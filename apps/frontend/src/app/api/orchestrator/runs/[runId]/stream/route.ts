import { NextRequest } from 'next/server';

const BACKEND_BASE_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: { runId: string } }
) {
  const { runId } = params;
  
  console.log(`[Orchestrator SSE Proxy] Connecting to run ${runId} stream`);

  // Create a ReadableStream to forward the SSE data
  const stream = new ReadableStream({
    async start(controller) {
      try {
        // Forward query parameters from the frontend request to the backend
        const { searchParams } = new URL(request.url);
        const queryString = searchParams.toString();
        const backendUrl = `${BACKEND_BASE_URL}/runs/${runId}/stream${queryString ? `?${queryString}` : ''}`;
        console.log(`[Orchestrator SSE Proxy] Fetching ${backendUrl}`);
        
        const response = await fetch(backendUrl, {
          headers: {
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache',
          },
        });

        if (!response.ok) {
          console.error(`[Orchestrator SSE Proxy] Error ${response.status}: ${response.statusText}`);
          controller.enqueue(`data: ${JSON.stringify({ error: 'Failed to connect to backend stream' })}\n\n`);
          controller.close();
          return;
        }

        const reader = response.body?.getReader();
        if (!reader) {
          console.error('[Orchestrator SSE Proxy] No reader available');
          controller.enqueue(`data: ${JSON.stringify({ error: 'Stream not available' })}\n\n`);
          controller.close();
          return;
        }

        // Forward the stream data
        try {
          while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
              console.log('[Orchestrator SSE Proxy] Stream ended');
              break;
            }
            
            // Forward the chunk as-is
            controller.enqueue(value);
          }
        } catch (error) {
          console.error('[Orchestrator SSE Proxy] Stream error:', error);
          controller.enqueue(`data: ${JSON.stringify({ error: 'Stream connection lost' })}\n\n`);
        } finally {
          reader.releaseLock();
          controller.close();
        }
        
      } catch (error) {
        console.error('[Orchestrator SSE Proxy] Connection error:', error);
        controller.enqueue(`data: ${JSON.stringify({ error: 'Failed to connect to backend' })}\n\n`);
        controller.close();
      }
    },

    cancel() {
      console.log('[Orchestrator SSE Proxy] Stream cancelled');
    }
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET',
      'Access-Control-Allow-Headers': 'Cache-Control',
    },
  });
}
