# ShapeCraft2 Contracts

This package contains the Solidity smart contracts for ShapeCraft2, including the DropManager for voting functionality and HistorianMedals NFT contract.

## Contracts

### DropManager

Manages voting sessions for NFT drops with the following features:

- Open/close voting sessions
- Support for simple and quadratic voting
- Token-gated voting (optional)
- Integration with HistorianMedals NFT contract

### HistorianMedals

ERC721 NFT contract for minting commemorative tokens with:

- IPFS metadata support
- Batch minting functionality
- Integration with DropManager for controlled minting

## Development

### Prerequisites

- Node.js >= 18
- npm or yarn

### Installation

```bash
npm install
```

### Compilation

```bash
npm run compile
```

### Testing

```bash
npm test
```

### Deployment

1. Set up your environment variables in `.env`:

```bash
PRIVATE_KEY=your_private_key_here
SHAPE_RPC_URL=https://sepolia.shape.network
CHAIN_ID=11011
```

2. Deploy contracts:

```bash
npm run deploy
```

This will:

- Deploy both contracts to the specified network
- Configure contracts to work together
- Generate `infra/deploy/addresses.json` with deployed addresses

### ABI Export

Export contract ABIs for use in frontend/other services:

```bash
npm run export-abi
```

This will generate:

- `abi/DropManager.json` - Filtered ABI with only necessary functions
- `abi/HistorianMedals.json` - Filtered ABI
- `abi/combined.json` - Combined ABI for convenience
- `abi/index.ts` - TypeScript exports

### Build

```bash
npm run build
```

## Contract Functions

### DropManager

#### Core Functions

- `openVote(string[] cids, VoteConfig config)` - Start a new voting session
- `castVote(bytes32 voteId, uint256 index)` - Cast a vote in an active session
- `closeVote(bytes32 voteId)` - Close a voting session
- `finalizeMint(bytes32 voteId, string winnerCid, string tokenURI)` - Finalize minting

#### View Functions

- `getVote(bytes32 voteId)` - Get vote details
- `getVoteIds()` - Get all vote IDs
- `hasVoted(bytes32 voteId, address voter)` - Check if address has voted

### HistorianMedals

#### Core Functions

- `mint(address to, string tokenURI)` - Mint a single token (DropManager only)
- `batchMint(address[] recipients, string[] tokenURIs)` - Batch mint tokens

#### View Functions

- `totalSupply()` - Get total token supply
- `tokensOfOwner(address owner)` - Get all tokens owned by address
- `exists(uint256 tokenId)` - Check if token exists
- `getTokenMetadata(uint256 tokenId)` - Get enhanced token metadata

## Network Configuration

### Shape Mainnet Deployment

1. Configure your `.env` for Shape Mainnet:

```bash
SHAPE_RPC_URL=https://shape-mainnet.g.alchemy.com/v2/YOUR_API_KEY
CHAIN_ID=360
```

2. Deploy to Shape Mainnet:

```bash
npm run deploy-mainnet
```

3. Verify contracts on Shape Mainnet:

```bash
npm run verify-mainnet
```

**Note**: Shape Mainnet uses its own verification system, not Etherscan. The verification process may require manual steps through the Shape explorer.

### Shape Testnet Deployment (for testing)

1. Configure your `.env` for Shape Testnet:

```bash
SHAPE_RPC_URL=https://sepolia.shape.network
CHAIN_ID=11011
```

2. Deploy to Shape Testnet:

```bash
npm run deploy-testnet
```

### General Deployment

The contracts can be deployed to any EVM-compatible network by updating the network configuration in `hardhat.config.ts`.

**Shape Mainnet Chain ID**: 360
**Shape Testnet Chain ID**: 11011

## Security Considerations

- Contracts use OpenZeppelin libraries for battle-tested implementations
- ReentrancyGuard is used on critical functions
- Only DropManager can mint tokens on HistorianMedals
- Owner controls can update contract references

## Events

### DropManager Events

- `VoteOpened(bytes32 voteId, string[] cids, VoteConfig config)`
- `VoteCast(bytes32 voteId, address voter, uint256 index)`
- `VoteClosed(bytes32 voteId, string winnerCid)`
- `MintFinalized(bytes32 voteId, uint256 tokenId, string tokenURI)`

### HistorianMedals Events

- `TokenMinted(uint256 tokenId, address to, string tokenURI)`
