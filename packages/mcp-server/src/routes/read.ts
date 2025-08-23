import { Router } from 'express';
import { publicClient, dropManagerContract, historianMedalsContract } from '../blockchain.js';
import { NETWORK_CONFIG } from '../config.js';
import type { ChainInfo, GasbackInfo, MedalsResponse } from '../types.js';

const router = Router();

// GET /mcp/chain_info
router.get('/chain_info', async (req, res) => {
  try {
    const chainInfo: ChainInfo = {
      chainId: NETWORK_CONFIG.CHAIN_ID,
      name: NETWORK_CONFIG.CHAIN_NAME,
    };
    res.json(chainInfo);
  } catch (error) {
    console.error('Chain info error:', error);
    res.status(500).json({ error: 'Failed to get chain info' });
  }
});

// GET /mcp/gasback_info?contract=ADDRESS
router.get('/gasback_info', async (req, res) => {
  try {
    const { contract } = req.query;
    
    if (!contract || typeof contract !== 'string') {
      return res.status(400).json({ error: 'Missing or invalid contract address' });
    }

    // For demo purposes, return mock gasback data
    // In a real implementation, this would query the gasback contract
    const gasbackInfo: GasbackInfo = {
      accrued: '0', // Wei amount
      claimable: '0', // Wei amount
    };

    res.json(gasbackInfo);
  } catch (error) {
    console.error('Gasback info error:', error);
    res.status(500).json({ error: 'Failed to get gasback info' });
  }
});

// GET /mcp/medal_of?address=ADDRESS
router.get('/medal_of', async (req, res) => {
  try {
    const { address } = req.query;
    
    if (!address || typeof address !== 'string') {
      return res.status(400).json({ error: 'Missing or invalid address' });
    }

    // Get user's medal tokens
    try {
      const tokens = await historianMedalsContract.read.tokensOfOwner([address as `0x${string}`]);
      
      const medals = tokens.map((tokenId) => ({
        id: tokenId.toString(),
        balance: '1', // ERC-721 always has balance of 1
      }));

      const response: MedalsResponse = { medals };
      res.json(response);
    } catch (contractError) {
      console.warn('Contract call failed, returning empty medals:', contractError);
      // Return empty array if contract call fails
      const response: MedalsResponse = { medals: [] };
      res.json(response);
    }
  } catch (error) {
    console.error('Medal info error:', error);
    res.status(500).json({ error: 'Failed to get medal info' });
  }
});

export { router as readRouter };
