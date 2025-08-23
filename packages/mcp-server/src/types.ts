import { z } from 'zod';

// PreparedTx schema from mcp_tools_spec.md
export const PreparedTxSchema = z.object({
  to: z.string().regex(/^0x[a-fA-F0-9]{40}$/, 'Invalid Ethereum address'),
  data: z.string().regex(/^0x[a-fA-F0-9]*$/, 'Invalid hex data'),
  value: z.string().regex(/^0x[a-fA-F0-9]+$/, 'Invalid hex value').optional(),
  gas: z.number().optional(),
});

export type PreparedTx = z.infer<typeof PreparedTxSchema>;

// Vote configuration schemas
export const VoteConfigSchema = z.object({
  method: z.enum(['simple']),
  gate: z.enum(['allowlist', 'open', 'passport_stub']),
  duration_s: z.number().positive(),
});

export type VoteConfig = z.infer<typeof VoteConfigSchema>;

// Request/Response schemas
export const StartVoteRequestSchema = z.object({
  artCids: z.array(z.string()),
  cfg: VoteConfigSchema,
});

export const TallyVoteRequestSchema = z.object({
  vote_id: z.string().regex(/^0x[a-fA-F0-9]{64}$/, 'Invalid vote ID'),
});

export const MintFinalRequestSchema = z.object({
  winner_cid: z.string(),
  metadataCid: z.string(),
});

export const IssueMedalRequestSchema = z.object({
  toAddress: z.string().regex(/^0x[a-fA-F0-9]{40}$/, 'Invalid Ethereum address'),
  id: z.number().positive(),
});

// Response types
export interface ChainInfo {
  chainId: number;
  name: string;
}

export interface GasbackInfo {
  accrued: string;
  claimable: string;
}

export interface MedalBalance {
  id: string;
  balance: string;
}

export interface MedalsResponse {
  medals: MedalBalance[];
}

export interface VoteStatus {
  open: boolean;
  tallies: number[];
  endsAt: string; // ISO string
}

export interface TallyResult {
  winner_cid: string;
  tally: Record<string, number>;
}

// IPFS response
export interface PinResult {
  cid: string;
}
