import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { SERVER_CONFIG } from './config.js';
import { readRouter } from './routes/read.js';
import { writeRouter } from './routes/write.js';
import { shutdown } from './ipfs.js';

const app = express();

// Security middleware
app.use(helmet({
  crossOriginResourcePolicy: { policy: 'cross-origin' },
}));

// CORS configuration
app.use(cors({
  origin: SERVER_CONFIG.CORS_ORIGINS,
  credentials: true,
}));

// Body parsing middleware
app.use(express.json({ limit: '50mb' }));
app.use(express.raw({ type: '*/*', limit: '50mb' }));

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Routes
app.use('/mcp', readRouter);
app.use('/mcp', writeRouter);

// Error handling middleware
app.use((error: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Server error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Not found' });
});

// Start server
const port = SERVER_CONFIG.PORT;
const server = app.listen(port, () => {
  console.log(`MCP Server running on port ${port}`);
  console.log(`Health check: http://localhost:${port}/health`);
});

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\nShutting down gracefully...');
  server.close(async () => {
    await shutdown();
    process.exit(0);
  });
});

process.on('SIGTERM', async () => {
  console.log('SIGTERM received, shutting down gracefully...');
  server.close(async () => {
    await shutdown();
    process.exit(0);
  });
});

export default app;
