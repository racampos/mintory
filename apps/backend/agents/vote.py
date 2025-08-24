"""
Vote Agent - Handle voting via MCP tools
"""
import uuid
import httpx
from typing import Dict, Any
from state import RunState, VoteConfig, VoteState, VoteResult


async def vote_agent(state: RunState) -> Dict[str, Any]:
    """
    Vote Agent: Manage voting process via MCP tools
    
    Input: ArtSet, VoteConfig
    Output: VoteState with vote ID and eventual result
    """
    art = state.get("art")
    if not art:
        return {
            "error": "No art data available for voting",
            "messages": [{
                "agent": "Vote",
                "level": "error",
                "message": "Missing art data",
                "ts": str(uuid.uuid4())
            }]
        }
    
    # Default vote config for demo
    vote_config = VoteConfig(
        method="simple",
        gate="allowlist",  # Simplified for hackathon
        duration_s=120  # 2 minutes
    )
    
    try:
        # Small delay to allow SSE polling to detect intermediate state changes
        import asyncio
        await asyncio.sleep(0.05)  # 50ms delay for real-time streaming
        
        # Call MCP server to start vote
        # In production, this would call the actual MCP server
        # For now, simulate the vote process
        
        vote_id = f"vote_{uuid.uuid4().hex[:8]}"
        
        vote_state = VoteState(
            id=vote_id,
            config=vote_config,
            result=None  # Will be populated when vote closes
        )
        
        message = {
            "agent": "Vote",
            "level": "info", 
            "message": f"Started vote {vote_id} with {len(art['cids'])} options",
            "ts": str(uuid.uuid4()),
            "links": [
                {"label": f"Option {i+1}", "href": cid}
                for i, cid in enumerate(art["cids"])
            ]
        }
        
        return {
            "vote": vote_state.dict(),
            "messages": [message]
        }
        
    except Exception as e:
        return {
            "error": f"Vote creation failed: {str(e)}",
            "messages": [{
                "agent": "Vote",
                "level": "error",
                "message": f"Vote creation failed: {str(e)}",
                "ts": str(uuid.uuid4())
            }]
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
            # "checkpoint": "finalize_mint",  # Removed for automatic progression in development
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
