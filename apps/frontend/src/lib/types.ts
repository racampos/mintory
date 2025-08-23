// Frontend Types for Shapecraft2

export interface PreparedTx {
  to: `0x${string}`;
  data: `0x${string}`;
  value?: `0x${string}`;
  gas?: number;
}

export interface RunState {
  run_id: string;
  date_label: string;
  status: 'running' | 'waiting' | 'completed' | 'error';
  current_agent?: string;
  checkpoint?: 'lore_approval' | 'art_sanity' | 'finalize_mint';
  lore_pack?: LorePack;
  art_set?: ArtSet;
  vote_result?: VoteResult;
  mint_receipt?: MintReceipt;
}

export interface LorePack {
  summary_md: string;
  bullet_facts: string[];
  sources: string[];
  prompt_seed: {
    style: string;
    palette: string;
    motifs?: string[];
  };
}

export interface ArtSet {
  cids: string[];
  thumbnails: string[];
  style_notes: string;
}

export interface VoteResult {
  winner_cid: string;
  tally: Record<string, number>;
  vote_id?: string;
}

export interface MintReceipt {
  tx_hash: string;
  token_id: string;
  token_uri: string;
}

export interface StreamUpdate {
  agent: string;
  level: 'info' | 'warning' | 'error' | 'success';
  message: string;
  state_delta?: Partial<RunState>;
  links?: string[];
  timestamp?: string;
}

// MCP Tool Types
export interface ChainInfo {
  chainId: number;
  name: string;
}

export interface GasbackInfo {
  accrued: string;
  claimable: string;
}

export interface Medal {
  id: string;
  balance: string;
}

export interface MedalInfo {
  medals: Medal[];
}

export interface CheckpointAction {
  checkpoint: 'lore_approval' | 'art_sanity' | 'finalize_mint';
  decision: 'approve' | 'edit' | 'proceed' | 'regen' | 'finalize';
  payload: any;
}
