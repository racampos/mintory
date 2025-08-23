import type { ChainInfo, GasbackInfo, MedalInfo, PreparedTx } from './types';

// Default MCP URL
const DEFAULT_MCP_URL = 'http://localhost:3001';

export class MCPClient {
  private baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || DEFAULT_MCP_URL;
  }

  // Read Tools
  async getChainInfo(): Promise<ChainInfo> {
    const response = await fetch(`${this.baseUrl}/mcp/chain_info`);
    if (!response.ok) {
      throw new Error(`Failed to get chain info: ${response.statusText}`);
    }
    return response.json();
  }

  async getGasbackInfo(contract: string): Promise<GasbackInfo> {
    const url = new URL(`${this.baseUrl}/mcp/gasback_info`);
    url.searchParams.set('contract', contract);
    
    const response = await fetch(url.toString());
    if (!response.ok) {
      throw new Error(`Failed to get gasback info: ${response.statusText}`);
    }
    return response.json();
  }

  async getMedalsOf(address: string): Promise<MedalInfo> {
    const url = new URL(`${this.baseUrl}/mcp/medal_of`);
    url.searchParams.set('address', address);
    
    const response = await fetch(url.toString());
    if (!response.ok) {
      throw new Error(`Failed to get medals: ${response.statusText}`);
    }
    return response.json();
  }

  async getVoteStatus(voteId: string): Promise<{
    open: boolean;
    tallies: number[];
    endsAt: string;
  }> {
    const url = new URL(`${this.baseUrl}/mcp/vote_status`);
    url.searchParams.set('vote_id', voteId);
    
    const response = await fetch(url.toString());
    if (!response.ok) {
      throw new Error(`Failed to get vote status: ${response.statusText}`);
    }
    return response.json();
  }

  // Write Tools (return PreparedTx)
  async pinMetadata(metadata: any): Promise<{ cid: string }> {
    const response = await fetch(`${this.baseUrl}/mcp/pin_metadata`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(metadata),
    });
    if (!response.ok) {
      throw new Error(`Failed to pin metadata: ${response.statusText}`);
    }
    return response.json();
  }

  async startVote(artCids: string[], config: {
    method: 'simple';
    gate: 'allowlist' | 'open' | 'passport_stub';
    duration_s: number;
  }): Promise<{ vote_id: string; tx: PreparedTx }> {
    const response = await fetch(`${this.baseUrl}/mcp/start_vote`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ artCids, cfg: config }),
    });
    if (!response.ok) {
      throw new Error(`Failed to start vote: ${response.statusText}`);
    }
    return response.json();
  }

  async tallyVote(voteId: string): Promise<{
    winner_cid: string;
    tally: Record<string, number>;
  }> {
    const response = await fetch(`${this.baseUrl}/mcp/tally_vote`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ vote_id: voteId }),
    });
    if (!response.ok) {
      throw new Error(`Failed to tally vote: ${response.statusText}`);
    }
    return response.json();
  }

  async mintFinal(winnerCid: string, metadataCid: string): Promise<{ tx: PreparedTx }> {
    const response = await fetch(`${this.baseUrl}/mcp/mint_final`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ winner_cid: winnerCid, metadataCid }),
    });
    if (!response.ok) {
      throw new Error(`Failed to prepare mint: ${response.statusText}`);
    }
    return response.json();
  }

  async issueMedal(toAddress: string, id: number): Promise<{ tx: PreparedTx }> {
    const response = await fetch(`${this.baseUrl}/mcp/issue_medal`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ toAddress, id }),
    });
    if (!response.ok) {
      throw new Error(`Failed to prepare medal: ${response.statusText}`);
    }
    return response.json();
  }
}

export const mcpClient = new MCPClient();
