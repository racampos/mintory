import { z } from 'zod';

// Base types
export const DateLabelSchema = z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Date must be in YYYY-MM-DD format");
export type DateLabel = z.infer<typeof DateLabelSchema>;

export const IpfsCidSchema = z.string().regex(/^ipfs:\/\/[a-zA-Z0-9]+$/, "Must be a valid IPFS CID starting with ipfs://");
export type IpfsCid = z.infer<typeof IpfsCidSchema>;

export const HttpUrlSchema = z.string().url().refine(url => url.startsWith('http://') || url.startsWith('https://'), "URL must use http or https protocol");
export type HttpUrl = z.infer<typeof HttpUrlSchema>;

export const EthereumAddressSchema = z.string().regex(/^0x[a-fA-F0-9]{40}$/, "Must be a valid Ethereum address");
export type EthereumAddress = z.infer<typeof EthereumAddressSchema>;

export const TransactionHashSchema = z.string().regex(/^0x[a-fA-F0-9]{64}$/, "Must be a valid transaction hash");
export type TransactionHash = z.infer<typeof TransactionHashSchema>;

export const Bytes32Schema = z.string().regex(/^0x[a-fA-F0-9]{64}$/, "Must be a valid bytes32");
export type Bytes32 = z.infer<typeof Bytes32Schema>;

// Prompt seed schema
export const PromptSeedSchema = z.object({
  style: z.string().min(1, "Style cannot be empty"),
  palette: z.string().min(1, "Palette cannot be empty"),
  motifs: z.array(z.string()).optional().default([])
});
export type PromptSeed = z.infer<typeof PromptSeedSchema>;

// Lore Agent types
export const LorePackSchema = z.object({
  summary_md: z.string()
    .min(1, "Summary cannot be empty")
    .refine(summary => summary.split(/\s+/).length <= 200, "Summary must be 200 words or less"),
  bullet_facts: z.array(z.string())
    .min(5, "Must have at least 5 bullet facts")
    .max(10, "Cannot have more than 10 bullet facts"),
  sources: z.array(HttpUrlSchema)
    .min(5, "Must have at least 5 sources"),
  prompt_seed: PromptSeedSchema
});
export type LorePack = z.infer<typeof LorePackSchema>;

// Artist Agent types
export const ArtSetSchema = z.object({
  cids: z.array(IpfsCidSchema)
    .min(4, "Must have at least 4 CIDs")
    .max(6, "Cannot have more than 6 CIDs")
    .refine(cids => new Set(cids).size === cids.length, "All CIDs must be unique"),
  thumbnails: z.array(z.string()).optional(), // Base64 encoded images
  style_notes: z.string().optional()
});
export type ArtSet = z.infer<typeof ArtSetSchema>;

// Vote Agent types
export const VoteMethodSchema = z.enum(['quadratic', 'simple']);
export type VoteMethod = z.infer<typeof VoteMethodSchema>;

export const VoteGateSchema = z.enum(['open', 'token_gated']);
export type VoteGate = z.infer<typeof VoteGateSchema>;

export const VoteConfigSchema = z.object({
  method: VoteMethodSchema,
  gate: VoteGateSchema,
  duration: z.number().positive("Duration must be positive")
});
export type VoteConfig = z.infer<typeof VoteConfigSchema>;

export const VoteResultSchema = z.object({
  winner_cid: IpfsCidSchema,
  tally: z.record(IpfsCidSchema, z.number()),
  fallback: z.boolean().optional()
});
export type VoteResult = z.infer<typeof VoteResultSchema>;

// Mint Agent types
export const MintReceiptSchema = z.object({
  tx_hash: TransactionHashSchema,
  token_id: z.bigint().positive("Token ID must be positive"),
  token_uri: IpfsCidSchema
});
export type MintReceipt = z.infer<typeof MintReceiptSchema>;

// Attestation Agent types
export const AttestationReceiptSchema = z.object({
  id: Bytes32Schema,
  uri: IpfsCidSchema
});
export type AttestationReceipt = z.infer<typeof AttestationReceiptSchema>;

// Guard Agent types
export const PolicyOKSchema = z.object({
  approved: z.boolean(),
  reason: z.string().optional()
});
export type PolicyOK = z.infer<typeof PolicyOKSchema>;

// NFT Metadata types (from metadata_schema.md)
export const AttributeSchema = z.object({
  trait_type: z.string(),
  value: z.union([z.string(), z.number()])
});
export type Attribute = z.infer<typeof AttributeSchema>;

export const NFTMetadataSchema = z.object({
  name: z.string(),
  description: z.string(),
  image: IpfsCidSchema,
  attributes: z.array(AttributeSchema),
  properties: z.object({
    summary_md: z.string(),
    sources: z.array(HttpUrlSchema),
    prompt_seed: PromptSeedSchema,
    attestation_uri: IpfsCidSchema.optional()
  })
});
export type NFTMetadata = z.infer<typeof NFTMetadataSchema>;

// Contract types (from contracts_and_addresses.md)
export const VoteParamsSchema = z.object({
  method: z.number().min(0).max(255, "Method must fit in uint8"),
  gate: z.number().min(0).max(255, "Gate must fit in uint8"),
  duration: z.bigint().positive("Duration must be positive")
});
export type VoteParams = z.infer<typeof VoteParamsSchema>;

export const AddressesConfigSchema = z.object({
  chainId: z.number().positive("Chain ID must be positive"),
  DropManager: EthereumAddressSchema,
  HistorianMedals: EthereumAddressSchema,
  NFT: EthereumAddressSchema
});
export type AddressesConfig = z.infer<typeof AddressesConfigSchema>;

// Network configuration
export const NetworkConfigSchema = z.object({
  CHAIN_ID: z.number().positive("Chain ID must be positive"),
  RPC_URL: z.string().url("RPC URL must be valid"),
  EXPLORER_BASE: z.string().url("Explorer base URL must be valid")
});
export type NetworkConfig = z.infer<typeof NetworkConfigSchema>;

// Agent Input/Output types
export const LoreAgentInputSchema = z.object({
  date_label: DateLabelSchema
});
export type LoreAgentInput = z.infer<typeof LoreAgentInputSchema>;

export const LoreAgentOutputSchema = LorePackSchema;
export type LoreAgentOutput = z.infer<typeof LoreAgentOutputSchema>;

export const ArtistAgentInputSchema = LorePackSchema;
export type ArtistAgentInput = z.infer<typeof ArtistAgentInputSchema>;

export const ArtistAgentOutputSchema = ArtSetSchema;
export type ArtistAgentOutput = z.infer<typeof ArtistAgentOutputSchema>;

export const VoteAgentInputSchema = z.object({
  artSet: ArtSetSchema,
  voteConfig: VoteConfigSchema
});
export type VoteAgentInput = z.infer<typeof VoteAgentInputSchema>;

export const VoteAgentOutputSchema = VoteResultSchema;
export type VoteAgentOutput = z.infer<typeof VoteAgentOutputSchema>;

export const MintAgentInputSchema = z.object({
  lorePack: LorePackSchema,
  winner_cid: IpfsCidSchema
});
export type MintAgentInput = z.infer<typeof MintAgentInputSchema>;

export const MintAgentOutputSchema = MintReceiptSchema;
export type MintAgentOutput = z.infer<typeof MintAgentOutputSchema>;

export const AttestationAgentInputSchema = z.object({
  token_id: z.bigint().positive("Token ID must be positive"),
  winner_cid: IpfsCidSchema,
  statement_uri: IpfsCidSchema
});
export type AttestationAgentInput = z.infer<typeof AttestationAgentInputSchema>;

export const AttestationAgentOutputSchema = AttestationReceiptSchema;
export type AttestationAgentOutput = z.infer<typeof AttestationAgentOutputSchema>;

export const GuardAgentInputSchema = LorePackSchema;
export type GuardAgentInput = z.infer<typeof GuardAgentInputSchema>;

export const GuardAgentOutputSchema = PolicyOKSchema;
export type GuardAgentOutput = z.infer<typeof GuardAgentOutputSchema>;

// Validation helper functions
export function validateLorePack(data: unknown): LorePack {
  return LorePackSchema.parse(data);
}

export function validateArtSet(data: unknown): ArtSet {
  return ArtSetSchema.parse(data);
}

export function validateVoteConfig(data: unknown): VoteConfig {
  return VoteConfigSchema.parse(data);
}

export function validateVoteResult(data: unknown): VoteResult {
  return VoteResultSchema.parse(data);
}

export function validateMintReceipt(data: unknown): MintReceipt {
  return MintReceiptSchema.parse(data);
}

export function validateAttestationReceipt(data: unknown): AttestationReceipt {
  return AttestationReceiptSchema.parse(data);
}

export function validateNFTMetadata(data: unknown): NFTMetadata {
  return NFTMetadataSchema.parse(data);
}

export function validateAddressesConfig(data: unknown): AddressesConfig {
  return AddressesConfigSchema.parse(data);
}
