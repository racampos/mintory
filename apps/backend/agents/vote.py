"""
Vote Agent - Handle voting via MCP tools with real blockchain integration
"""
import uuid
import asyncio
from typing import Dict, Any
from state import RunState, VoteConfig, VoteState, VoteResult
from services.mcp_client import get_mcp_client


async def vote_agent(state: RunState) -> Dict[str, Any]:
    """
    Vote Agent: Create blockchain vote via MCP integration
    
    Input: ArtSet from artist_agent
    Output: VoteState + PreparedTx + checkpoint for user confirmation
    
    Phase 5.5.1: Real MCP integration with vote_tx_approval checkpoint
    """
    run_id = state.get("run_id", "unknown")
    art = state.get("art")
    
    if not art or not art.get("cids"):
        error_message = {
            "agent": "Vote",
            "level": "error",
            "message": "No art data available for voting",
            "ts": str(uuid.uuid4())
        }
        return {
            "error": "No art data available for voting", 
            "messages": [error_message]
        }
    
    try:
        # Small delay for SSE streaming
        await asyncio.sleep(0.05)
        
        # Get MCP client for real blockchain integration
        mcp_client = get_mcp_client()
        
        # Extract art CIDs for voting
        art_cids = art["cids"]  # Real IPFS CIDs from artist agent
        
        # Vote configuration for hackathon demo
        vote_config = VoteConfig(
            method="simple",
            gate="allowlist",  # Simplified allowlist for demo reliability
            duration_s=120  # 2 minutes vote duration
        )
        
        print(f"🗳️ VOTE: Starting real blockchain vote for {run_id}")
        print(f"🗳️ VOTE: Art options: {len(art_cids)} CIDs")
        print(f"🗳️ VOTE: Config: {vote_config.dict()}")
        
        # ✅ REAL MCP INTEGRATION: Call start_vote
        vote_id, prepared_tx = await mcp_client.start_vote(art_cids, vote_config)
        
        print(f"🗳️ VOTE: Real vote created with ID: {vote_id}")
        print(f"🗳️ VOTE: PreparedTx ready for wallet signing")
        
        # Create VoteState with real blockchain data
        vote_state = VoteState(
            id=vote_id,  # Real blockchain vote ID
            config=vote_config,
            result=None  # Will be populated by tally_vote_agent
        )
        
        # Create success message with voting options
        start_message = {
            "agent": "Vote",
            "level": "info",
            "message": f"🗳️ Created blockchain vote {vote_id} with {len(art_cids)} options - Please confirm transaction",
            "ts": str(uuid.uuid4()),
            "links": [
                {"label": f"Option {i+1}", "href": cid}
                for i, cid in enumerate(art_cids)
            ]
        }
        
        # ✅ CHECKPOINT: Add vote_tx_approval for user transaction confirmation
        return {
            "vote": vote_state.dict(),
            "prepared_tx": {  # PreparedTx for frontend wallet signing
                "to": prepared_tx.to,
                "data": prepared_tx.data,
                "value": prepared_tx.value if hasattr(prepared_tx, 'value') else "0x0",
                "gas": prepared_tx.gas if hasattr(prepared_tx, 'gas') else None
            },
            "checkpoint": "vote_tx_approval",  # ✅ NEW CHECKPOINT
            "messages": [start_message]
        }
        
    except Exception as e:
        print(f"🗳️ VOTE: Failed to create vote: {e}")
        
        error_message = {
            "agent": "Vote",
            "level": "error",
            "message": f"Vote creation failed: {str(e)}",
            "ts": str(uuid.uuid4())
        }
        
        return {
            "error": f"Vote creation failed: {str(e)}",
            "messages": [error_message]
        }


async def tally_vote_agent(state: RunState) -> Dict[str, Any]:
    """
    Tally vote and determine winner
    """
    vote = state.get("vote")
    art = state.get("art")
    
    if not vote or not art:
        return {
            "error": "Missing vote or art data for tally",
            "messages": [{
                "agent": "Vote", 
                "level": "error",
                "message": "Missing data for vote tally",
                "ts": str(uuid.uuid4())
            }]
        }
    
    try:
        # Small delay to allow SSE polling to detect intermediate state changes
        import asyncio
        await asyncio.sleep(0.05)  # 50ms delay for real-time streaming
        
        # In production, call MCP server to get vote results
        # For demo, simulate a vote result
        
        # Pick first art as winner for demo
        winner_cid = art["cids"][0]
        
        vote_result = VoteResult(
            winner_cid=winner_cid,
            tally={"0": 3, "1": 1, "2": 0, "3": 1},  # Option 0 wins
            participation=5
        )
        
        # Update vote state
        updated_vote = vote.copy()
        updated_vote["result"] = vote_result.dict()
        
        message = {
            "agent": "Vote",
            "level": "info",
            "message": f"Vote completed! Winner: {winner_cid}",
            "ts": str(uuid.uuid4()),
            "links": [
                {"label": "Winning Art", "href": winner_cid}
            ]
        }
        
        return {
            "vote": updated_vote,
            # Note: finalize_mint checkpoint is handled by LangGraph interrupt_after=["mint"]
            "messages": [message]
        }
        
    except Exception as e:
        return {
            "error": f"Vote tally failed: {str(e)}",
            "messages": [{
                "agent": "Vote",
                "level": "error", 
                "message": f"Vote tally failed: {str(e)}",
                "ts": str(uuid.uuid4())
            }]
        }
