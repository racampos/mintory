"""
Vote Agent - Handle voting via MCP tools with real blockchain integration
"""
import uuid
import asyncio
from typing import Dict, Any
from datetime import datetime
import simple_state
from state import RunState, VoteConfig, VoteState, PreparedTx, VoteResult
from services.mcp_client import get_mcp_client, VoteStatus, TallyResult


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
            duration_s=120  # 2 minutes for realistic demo timing
        )
        
        print(f"🗳️ VOTE: Starting real blockchain vote for {run_id}")
        print(f"🗳️ VOTE: Art options: {len(art_cids)} CIDs")
        print(f"🗳️ VOTE: Config: {vote_config.dict()}")
        
        # ✅ REAL MCP INTEGRATION: Call start_vote
        vote_id, prepared_tx = await mcp_client.start_vote(art_cids, vote_config)
        
        print(f"🗳️ VOTE: Real vote created with ID: {vote_id}")
        print(f"🗳️ VOTE: PreparedTx ready for wallet signing")
        print(f"🗳️ VOTE: MCP returned gas limit: {getattr(prepared_tx, 'gas', 'None')}")
        
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
        prepared_tx_obj = PreparedTx(
            to=prepared_tx.to,
            data=prepared_tx.data,
            value=prepared_tx.value if hasattr(prepared_tx, 'value') and prepared_tx.value is not None else "0x0",
            gas=max(prepared_tx.gas if hasattr(prepared_tx, 'gas') and prepared_tx.gas else 0, 500000)
        )
        
        print(f"🗳️ VOTE: PreparedTx object: {prepared_tx_obj.dict()}")
        print(f"🗳️ VOTE: Vote state: {vote_state.dict()}")
        
        result = {
            "vote": vote_state.dict(),
            "prepared_tx": prepared_tx_obj.dict(),
            "checkpoint": "vote_tx_approval",  # ✅ NEW CHECKPOINT
            "messages": [start_message]
        }
        
        print(f"🗳️ VOTE: Full result being returned: {result}")
        return result
        
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
    📊 Tally Vote Agent with Real-time Polling and Timeout Fallback (Phase 5.5.3)
    
    Features:
    - 5-second interval MCP polling of get_vote_status  
    - Real-time SSE updates during polling
    - Timeout fallback: pick index 0 when ends_at expires
    - Call MCP tally_vote for natural completion
    - Emergency fallback for any errors
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
    
    # ✅ PHASE 5.5.3: Real-time MCP Polling with Timeout Fallback
    
    run_id = state.get("run_id")
    vote_id = vote.get("id")
    
    if not vote_id:
        error_message = {
            "agent": "Vote",
            "level": "error", 
            "message": "Vote ID missing from state",
            "ts": str(uuid.uuid4())
        }
        return {
            "error": "Vote ID missing",
            "messages": [error_message]
        }
        
    try:
        mcp_client = get_mcp_client()
        all_messages = []
        
        # Start polling message
        start_message = {
            "agent": "Vote",
            "level": "info",
            "message": f"🕐 Starting vote polling for {vote_id[:16]}... (5s intervals)",
            "ts": str(uuid.uuid4())
        }
        all_messages.append(start_message)
        
        # Update SSE immediately
        if run_id:
            current_messages = simple_state.get_run_state(run_id).get("messages", [])
            current_messages.append(start_message)
            simple_state.update_run_state(run_id, {"messages": current_messages})
        
        poll_count = 0
        max_polls = 30   # 30 polls * 5s = 150 seconds timeout (120s vote + 30s buffer)
        
        while poll_count < max_polls:
            poll_count += 1
            
            # Get current vote status
            try:
                vote_status: VoteStatus = await mcp_client.get_vote_status(vote_id)
                print(f"📊 TALLY: Poll #{poll_count}: open={vote_status.open}, tallies={vote_status.tallies}, ends_at={vote_status.ends_at}")
                
                # Check if vote has ended naturally
                if not vote_status.open:
                    print(f"📊 TALLY: Vote {vote_id} has ended naturally")
                    break
                
                # Check timeout - parse ends_at timestamp (handle both int and ISO string)
                try:
                    if isinstance(vote_status.ends_at, str):
                        # Handle ISO 8601 format: "2025-08-24T18:00:58.000Z"
                        from datetime import datetime
                        if vote_status.ends_at.endswith('Z'):
                            # Remove 'Z' and parse
                            ends_at_dt = datetime.fromisoformat(vote_status.ends_at.replace('Z', '+00:00'))
                        else:
                            ends_at_dt = datetime.fromisoformat(vote_status.ends_at)
                        ends_at_timestamp = int(ends_at_dt.timestamp())
                    else:
                        # Handle integer timestamp
                        ends_at_timestamp = int(vote_status.ends_at)
                        
                    current_timestamp = int(datetime.now().timestamp())
                    
                    if current_timestamp >= ends_at_timestamp:
                        print(f"📊 TALLY: Vote {vote_id} has expired (timeout)")
                        break
                        
                except (ValueError, TypeError) as e:
                    print(f"📊 TALLY: Warning - could not parse ends_at timestamp: {e}")
                    # Continue polling if timestamp parsing fails
                
                # Send progress update every 6 polls (30s intervals)
                if poll_count % 6 == 0:
                    progress_message = {
                        "agent": "Vote",
                        "level": "info",
                        "message": f"📊 Vote in progress... ({poll_count}/{max_polls} polls, tallies: {vote_status.tallies})",
                        "ts": str(uuid.uuid4())
                    }
                    all_messages.append(progress_message)
                    
                    # Update SSE
                    if run_id:
                        current_messages = simple_state.get_run_state(run_id).get("messages", [])
                        current_messages.append(progress_message)
                        simple_state.update_run_state(run_id, {"messages": current_messages})
                
                # Wait 5 seconds before next poll
                await asyncio.sleep(5.0)
                
            except Exception as poll_error:
                print(f"📊 TALLY: Polling error on attempt {poll_count}: {poll_error}")
                
                # If polling fails, wait and try again (don't break immediately)
                if poll_count < max_polls:
                    await asyncio.sleep(5.0)
                    continue
                else:
                    print(f"📊 TALLY: Max polling errors reached, triggering fallback")
                    break
        
        # Determine completion type
        vote_ended_naturally = False
        has_votes = False
        
        try:
            final_status: VoteStatus = await mcp_client.get_vote_status(vote_id)
            vote_ended_naturally = not final_status.open
            
            # Check if there are any votes cast (even if vote is still open)
            has_votes = final_status.tallies and any(count > 0 for count in final_status.tallies)
            
            # Smart completion: if votes exist and we've polled enough, treat as naturally ready
            if not vote_ended_naturally and has_votes and poll_count >= 12:  # At least 60 seconds of polling
                print(f"📊 TALLY: Smart completion - votes exist {final_status.tallies}, treating as ready")
                vote_ended_naturally = True
                
        except:
            print("📊 TALLY: Could not get final status, assuming timeout")
        
        if vote_ended_naturally:
            # Vote completed naturally - get official results via tally_vote
            print(f"📊 TALLY: Getting official results via MCP tally_vote")
            
            try:
                tally_result: TallyResult = await mcp_client.tally_vote(vote_id)
                
                # Create VoteResult from MCP response
                vote_result = VoteResult(
                    winner_cid=tally_result.winner_cid,
                    tally=tally_result.tally,
                    participation=sum(tally_result.tally.values()) if tally_result.tally else 0
                )
                
                completion_message = {
                    "agent": "Vote",
                    "level": "success",
                    "message": f"🎉 Vote completed! Winner: {tally_result.winner_cid[:16]}... (natural completion)",
                    "ts": str(uuid.uuid4()),
                    "links": [{"label": "Winner Art", "href": tally_result.winner_cid}]
                }
                
            except Exception as tally_error:
                print(f"📊 TALLY: MCP tally_vote failed: {tally_error}, using fallback")
                
                # Fallback even for natural completion
                winner_cid = art["cids"][0]
                vote_result = VoteResult(
                    winner_cid=winner_cid,
                    tally={"0": 1},  # Fallback tally
                    participation=1
                )
                
                completion_message = {
                    "agent": "Vote", 
                    "level": "warning",
                    "message": f"🎉 Vote completed with fallback! Winner: {winner_cid[:16]}... (MCP tally failed)",
                    "ts": str(uuid.uuid4()),
                    "links": [{"label": "Winner Art", "href": winner_cid}]
                }
                
        else:
            # Vote timed out - use fallback logic
            print(f"📊 TALLY: Vote timed out after {poll_count} polls, using fallback (index 0)")
            
            winner_cid = art["cids"][0]  # Pick index 0 as per requirements
            vote_result = VoteResult(
                winner_cid=winner_cid,
                tally={"0": 1},  # Minimal tally for timeout
                participation=1
            )
            
            completion_message = {
                "agent": "Vote",
                "level": "warning", 
                "message": f"⏱️ Vote timed out! Winner by fallback: {winner_cid[:16]}... (picked index 0)",
                "ts": str(uuid.uuid4()),
                "links": [{"label": "Winner Art", "href": winner_cid}]
            }
        
        all_messages.append(completion_message)
        
        # Update vote state with results
        updated_vote = vote.copy()
        updated_vote["result"] = vote_result.dict()
        if not vote_ended_naturally:
            updated_vote["fallback"] = True  # Mark fallback completion
        
        print(f"📊 TALLY: Completed vote {vote_id} - winner: {vote_result.winner_cid}")
        
        return {
            "vote": updated_vote,
            "messages": all_messages
        }
        
    except Exception as e:
        print(f"📊 TALLY: Fatal error in tally_vote_agent: {e}")
        
        # Emergency fallback
        winner_cid = art["cids"][0] if art.get("cids") else "unknown"
        
        error_message = {
                "agent": "Vote",
                "level": "error", 
            "message": f"❌ Vote tally failed: {str(e)}. Emergency fallback: {winner_cid[:16]}...",
                "ts": str(uuid.uuid4())
        }
        
        # Create minimal vote result
        emergency_vote_result = VoteResult(
            winner_cid=winner_cid,
            tally={"0": 1},
            participation=1
        )
        
        updated_vote = vote.copy() if vote else {}
        updated_vote["result"] = emergency_vote_result.dict()
        updated_vote["fallback"] = True
        updated_vote["error"] = str(e)
        
        return {
            "vote": updated_vote,
            "messages": [error_message]
        }
