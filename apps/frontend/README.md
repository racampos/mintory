# Shapecraft Frontend

Next.js frontend for the Shapecraft AI-powered NFT creation platform.

## Features

- **Curator Chat**: Interactive AI assistant with Vercel AI SDK and MCP tool integration
- **Agent Console**: Real-time updates from backend via EventSource streaming
- **Wallet Integration**: viem-powered wallet connection with Shape testnet support
- **Voting System**: Interactive modal for artwork voting
- **Checkpoint Actions**: Approve, edit, proceed, and finalize buttons for workflow control
- **Floating Panel**: Gasback rewards and medal tracking

## Architecture

### Left Panel: Curator Chat

- Uses Vercel AI SDK for chat interface
- Integrates with MCP server for read-only tools (chain info, gasback, medals)
- Handles creation run initialization

### Right Panel: Agent Console

- EventSource connection to `/runs/{id}/stream`
- Real-time updates from LangGraph orchestrator
- Timeline view with agent activities and links
- Run state display (lore pack, art set, vote results, mint receipts)

### Wallet Integration

- viem-powered wallet client
- Shape testnet (Chain ID: 360) support
- PreparedTx signing workflow
- Network switching helpers

### Components Structure

```
src/
├── app/
│   ├── api/chat/route.ts    # Vercel AI SDK endpoint
│   ├── globals.css          # Tailwind styles
│   ├── layout.tsx          # Root layout
│   └── page.tsx            # Main application
├── components/
│   ├── agent-console.tsx   # EventSource streaming console
│   ├── checkpoint-actions.tsx # Workflow control buttons
│   ├── curator-chat.tsx    # AI chat with MCP tools
│   ├── floating-panel.tsx  # Gasback/medals display
│   ├── voting-modal.tsx    # Interactive voting interface
│   ├── wallet-connection.tsx # Wallet connect/switch
│   └── ui/                 # shadcn/ui components
└── lib/
    ├── mcp-client.ts       # MCP HTTP client
    ├── wallet.ts           # viem wallet manager
    ├── types.ts            # TypeScript definitions
    └── utils.ts            # Helper functions
```

## Environment Variables

```env
BACKEND_URL=http://localhost:8000
MCP_URL=http://localhost:3001
CHAIN_ID=360
```

## Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at http://localhost:3002

## Key Workflows

### 1. Starting a Creation Run

1. Enter historical date in Curator chat
2. Backend creates run and returns run_id
3. EventSource connects to stream updates
4. Lore Agent begins processing

### 2. Checkpoint Interactions

1. Agent reaches checkpoint (lore_approval, art_sanity, finalize_mint)
2. Checkpoint Actions component shows relevant buttons
3. User decisions sent to `/runs/{id}/resume`
4. Workflow continues based on user input

### 3. Voting Flow

1. Art generation completes
2. Voting modal opens with artwork grid
3. User selects preferred artwork
4. Vote transaction prepared via MCP
5. Wallet signs and submits transaction

### 4. MCP Tool Calls

- Chain info, gasback, and medal data fetched via HTTP
- Read-only tools integrated into AI chat
- Write tools return PreparedTx for wallet signing

## Development Notes

- Uses TypeScript with strict mode
- Tailwind CSS for styling with custom design system
- shadcn/ui component library for consistent UI
- EventSource with exponential backoff reconnection
- Responsive design optimized for desktop
- Error handling with toast notifications

## Production Considerations

- Replace demo toast system with proper library (sonner, etc.)
- Add proper error boundaries
- Implement loading states and skeletons
- Add comprehensive testing
- Set up monitoring and analytics
- Optimize bundle size and performance
