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
  checkpoint?: 'lore_approval' | 'art_sanity' | 'vote_tx_approval' | 'close_vote' | 'finalize_mint';
  lore_pack?: LorePack;
  art_set?: ArtSet;
  vote?: Vote;
  prepared_tx?: PreparedTx;
  vote_result?: VoteResult;
  mint_receipt?: MintReceipt;
  metadata?: {
    name: string;
    description: string;
    image: string;
    attributes: Array<{trait_type: string; value: any}>;
    properties: Record<string, any>;
  };
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

export interface Vote {
  id: string;
  config?: {
    method: string;
    gate: string;
    duration_s: number;
  };
  result?: VoteResult | null;
  tx_hash?: string;
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
  checkpoint: 'lore_approval' | 'art_sanity' | 'vote_tx_approval' | 'close_vote' | 'finalize_mint';
  decision: 'approve' | 'edit' | 'proceed' | 'regen' | 'confirm' | 'finalize' | 'close';
  payload: any;
}
