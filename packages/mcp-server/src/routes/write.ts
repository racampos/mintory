import { Router } from 'express';
import { z } from 'zod';
import { 
  dropManagerContract, 
  createOpenVoteTx, 
  createCloseVoteTx, 
  createFinalizeMintTx, 
  createIssueMedalTx,
  estimateGas 
} from '../blockchain.js';
import { pinFile, pinJSON, pinFromUrl } from '../ipfs.js';
import {
  StartVoteRequestSchema,
  TallyVoteRequestSchema,
  CloseVoteRequestSchema,
  MintFinalRequestSchema,
  IssueMedalRequestSchema,
  PreparedTxSchema,
  type VoteStatus,
  type TallyResult,
  type PinResult,
} from '../types.js';

const router = Router();

// POST /mcp/pin_cid
router.post('/pin_cid', async (req, res) => {
  try {
    // Check if we should use stub pinning
    const useStubs = process.env.ENABLE_STUB_PIN === '1';
    
    if (useStubs) {
      // Return fake IPFS CID for testing
      const fakeHash = Math.random().toString(36).substring(2, 15);
      const result: PinResult = {
        cid: `ipfs://FAKE_${fakeHash}`,
      };
      return res.json(result);
    }

    // Real IPFS pinning logic
    const contentType = req.headers['content-type'];
    let result: PinResult;

    if (contentType?.startsWith('application/json')) {
      // Handle URL in JSON body
      const { url } = req.body;
      if (!url || typeof url !== 'string') {
        return res.status(400).json({ error: 'Missing or invalid URL' });
      }
      result = await pinFromUrl(url);
    } else {
      // Handle raw file bytes
      if (!Buffer.isBuffer(req.body)) {
        return res.status(400).json({ error: 'Request body must be file bytes or JSON with URL' });
      }
      result = await pinFile(req.body);
    }

    res.json(result);
  } catch (error) {
    console.error('Pin CID error:', error);
    res.status(500).json({ error: 'Failed to pin content' });
  }
});

// POST /mcp/pin_metadata
router.post('/pin_metadata', async (req, res) => {
  try {
    // Check if we should use stub pinning
    const useStubs = process.env.ENABLE_STUB_PIN === '1';
    
    if (useStubs) {
      // Return fake IPFS CID for testing
      const fakeHash = Math.random().toString(36).substring(2, 15);
      const result: PinResult = {
        cid: `ipfs://FAKE_${fakeHash}`,
      };
      return res.json(result);
    }

    // Real IPFS pinning logic
    const result = await pinJSON(req.body);
    res.json(result);
  } catch (error) {
    console.error('Pin metadata error:', error);
    res.status(500).json({ error: 'Failed to pin metadata' });
  }
});

// POST /mcp/start_vote
router.post('/start_vote', async (req, res) => {
  try {
    const parsed = StartVoteRequestSchema.parse(req.body);
    
    // Create transaction
    const tx = createOpenVoteTx(parsed.artCids, parsed.cfg);
    
    // Estimate gas
    tx.gas = await estimateGas(tx);
    
    // Validate PreparedTx
    const validatedTx = PreparedTxSchema.parse(tx);

    // Generate mock vote ID for response (in real implementation, this would be derived from tx)
    const vote_id = `0x${'0'.repeat(64)}`;

    res.json({
      vote_id,
      tx: validatedTx,
    });
  } catch (error) {
    console.error('Start vote error:', error);
    if (error instanceof z.ZodError) {
      res.status(400).json({ error: 'Invalid request body' });
    } else {
      res.status(500).json({ error: 'Failed to start vote' });
    }
  }
});

// GET /mcp/vote_status?vote_id=BYTES32
router.get('/vote_status', async (req, res) => {
  try {
    const { vote_id } = req.query;
    
    if (!vote_id || typeof vote_id !== 'string') {
      return res.status(400).json({ error: 'Missing or invalid vote_id' });
    }

    if (!vote_id.match(/^0x[a-fA-F0-9]{64}$/)) {
      return res.status(400).json({ error: 'Invalid vote ID format' });
    }

    try {
      // Get vote data from contract
      const voteData = await dropManagerContract.read.getVote([vote_id as `0x${string}`]);
      
      const [cids, config, voteCounts, totalVotes, winnerCid, finalized] = voteData;
      
      const response: VoteStatus = {
        open: config.isOpen && !finalized,
        tallies: voteCounts.map(count => Number(count)),
        endsAt: new Date((Number(config.startTime) + Number(config.duration)) * 1000).toISOString(),
      };

      res.json(response);
    } catch (contractError) {
      console.warn('Contract call failed for vote status:', contractError);
      // Return mock data if contract call fails
      const response: VoteStatus = {
        open: false,
        tallies: [],
        endsAt: new Date().toISOString(),
      };
      res.json(response);
    }
  } catch (error) {
    console.error('Vote status error:', error);
    res.status(500).json({ error: 'Failed to get vote status' });
  }
});

// POST /mcp/tally_vote
router.post('/tally_vote', async (req, res) => {
  try {
    const parsed = TallyVoteRequestSchema.parse(req.body);
    
    try {
      // Get vote data to determine winner
      const voteData = await dropManagerContract.read.getVote([parsed.vote_id as `0x${string}`]);
      const [cids, config, voteCounts] = voteData;
      
      // Find winner (highest vote count)
      let winnerIndex = 0;
      let maxVotes = 0;
      const tally: Record<string, number> = {};
      
      voteCounts.forEach((count, index) => {
        const votes = Number(count);
        tally[index.toString()] = votes;
        if (votes > maxVotes) {
          maxVotes = votes;
          winnerIndex = index;
        }
      });

      const result: TallyResult = {
        winner_cid: cids[winnerIndex] || '',
        tally,
      };

      res.json(result);
    } catch (contractError) {
      console.warn('Contract call failed for tally vote:', contractError);
      // Return mock data if contract call fails
      const result: TallyResult = {
        winner_cid: 'ipfs://mock-winner-cid',
        tally: { '0': 1 },
      };
      res.json(result);
    }
  } catch (error) {
    console.error('Tally vote error:', error);
    if (error instanceof z.ZodError) {
      res.status(400).json({ error: 'Invalid request body' });
    } else {
      res.status(500).json({ error: 'Failed to tally vote' });
    }
  }
});

// POST /mcp/close_vote
router.post('/close_vote', async (req, res) => {
  try {
    const parsed = CloseVoteRequestSchema.parse(req.body);
    
    console.log(`🗳️ MCP: Creating close vote transaction for vote ${parsed.vote_id}`);
    
    // First check if vote is still open - if already closed, skip close vote step
    try {
      const voteStatus = await dropManagerContract.read.getVote([parsed.vote_id as `0x${string}`]);
      const isOpen = voteStatus[1].isOpen; // VoteConfig.isOpen
      
      if (!isOpen) {
        console.log(`🗳️ MCP: Vote ${parsed.vote_id} already closed, skipping close vote transaction`);
        return res.json({ 
          skip_close: true,
          message: "Vote already closed, ready for mint"
        });
      }
    } catch (contractError) {
      console.log(`🗳️ MCP: Could not check vote status: ${contractError}, proceeding with close vote`);
    }
    
    const tx = createCloseVoteTx(parsed.vote_id);
    
    // Estimate gas with higher limit for close vote operations (needs more due to winner calculation)
    const estimatedGas = await estimateGas(tx);
    tx.gas = Math.max(estimatedGas || 100000, 300000); // Ensure at least 300k gas for close vote
    
    console.log(`🗳️ MCP: Close vote gas estimated: ${estimatedGas} → using: ${tx.gas}`);
    
    // Validate PreparedTx
    const validatedTx = PreparedTxSchema.parse(tx);

    res.json({ tx: validatedTx });
  } catch (error) {
    console.error('Close vote error:', error);
    if (error instanceof z.ZodError) {
      res.status(400).json({ error: 'Invalid request body' });
    } else {
      res.status(500).json({ error: 'Failed to create close vote transaction' });
    }
  }
});

// POST /mcp/mint_final
router.post('/mint_final', async (req, res) => {
  try {
    const parsed = MintFinalRequestSchema.parse(req.body);
    
    // Use the real vote ID from the request
    const { vote_id, winner_cid, metadataCid } = parsed;
    console.log(`🪙 MCP: Creating mint transaction for vote ${vote_id}`);
    
    const tx = createFinalizeMintTx(vote_id, winner_cid, metadataCid);
    
    // Estimate gas with higher limit for finalize mint operations (now includes NFT minting)
    const estimatedGas = await estimateGas(tx);
    tx.gas = Math.max(estimatedGas || 150000, 400000); // Ensure at least 400k gas for finalize+mint
    
    console.log(`🪙 MCP: Finalize mint gas estimated: ${estimatedGas} → using: ${tx.gas}`);
    
    // Validate PreparedTx
    const validatedTx = PreparedTxSchema.parse(tx);

    res.json({ tx: validatedTx });
  } catch (error) {
    console.error('Mint final error:', error);
    if (error instanceof z.ZodError) {
      res.status(400).json({ error: 'Invalid request body' });
    } else {
      res.status(500).json({ error: 'Failed to create mint transaction' });
    }
  }
});

// POST /mcp/issue_medal
router.post('/issue_medal', async (req, res) => {
  try {
    const parsed = IssueMedalRequestSchema.parse(req.body);
    
    const tx = createIssueMedalTx(parsed.toAddress, parsed.id);
    
    // Estimate gas
    tx.gas = await estimateGas(tx);
    
    // Validate PreparedTx
    const validatedTx = PreparedTxSchema.parse(tx);

    res.json({ tx: validatedTx });
  } catch (error) {
    console.error('Issue medal error:', error);
    if (error instanceof z.ZodError) {
      res.status(400).json({ error: 'Invalid request body' });
    } else {
      res.status(500).json({ error: 'Failed to create medal transaction' });
    }
  }
});

export { router as writeRouter };
