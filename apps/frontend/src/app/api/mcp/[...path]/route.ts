import { NextRequest, NextResponse } from 'next/server';

const MCP_BASE_URL = process.env.MCP_URL || 'http://localhost:3001';

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  console.log('[MCP Proxy GET] Route hit with params:', params);
  
  try {
    const path = params.path.join('/');
    const searchParams = request.nextUrl.searchParams;
    const queryString = searchParams.toString();
    
    const mcpUrl = `${MCP_BASE_URL}/mcp/${path}${queryString ? `?${queryString}` : ''}`;
    
    console.log(`[MCP Proxy GET] Proxying to: ${mcpUrl}`);
    
    const response = await fetch(mcpUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      console.error(`[MCP Proxy GET] Error ${response.status}: ${response.statusText}`);
      return NextResponse.json(
        { error: `MCP service error: ${response.statusText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('[MCP Proxy GET] Network error:', error);
    return NextResponse.json(
      { error: 'Failed to connect to MCP service' },
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    const path = params.path.join('/');
    const body = await request.json();
    
    const mcpUrl = `${MCP_BASE_URL}/mcp/${path}`;
    
    console.log(`[MCP Proxy POST] ${mcpUrl}`, { body });
    
    const response = await fetch(mcpUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      console.error(`[MCP Proxy POST] Error ${response.status}: ${response.statusText}`);
      return NextResponse.json(
        { error: `MCP service error: ${response.statusText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('[MCP Proxy POST] Network error:', error);
    return NextResponse.json(
      { error: 'Failed to connect to MCP service' },
      { status: 500 }
    );
  }
}
