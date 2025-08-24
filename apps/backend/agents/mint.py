"""
Mint Agent - Handle NFT minting via MCP tools with real IPFS and blockchain integration
"""
import uuid
from typing import Dict, Any
from state import RunState, MintReceipt, PreparedTx
from services.mcp_client import get_mcp_client
import simple_state


async def mint_agent(state: RunState) -> Dict[str, Any]:
    """
    🪙 Mint Agent: Generate metadata + prepare mint transaction (Phase 5.6)
    
    Step 1: Build complete NFT metadata from workflow state
    Step 2: Pin metadata to IPFS via MCP server  
    Step 3: Prepare mint transaction via MCP server
    Step 4: Set finalize_mint checkpoint for user confirmation
    
    Input: LorePack, ArtSet, VoteResult
    Output: PreparedTx + metadata preview + finalize_mint checkpoint
    """
    run_id = state.get("run_id")
    lore = state.get("lore")
    vote = state.get("vote") 
    art = state.get("art")
    
    # Validate required state
    if not lore:
        return {
            "error": "Missing lore data for mint",
            "messages": [{
                "agent": "Mint",
                "level": "error", 
                "message": "❌ Cannot mint without lore research data",
                "ts": str(uuid.uuid4())
            }]
        }
        
    if not vote or not vote.get("result"):
        return {
            "error": "Missing vote result for mint",
            "messages": [{
                "agent": "Mint",
                "level": "error",
                "message": "❌ Cannot mint without completed vote results", 
                "ts": str(uuid.uuid4())
            }]
        }
        
    if not art or not art.get("cids"):
        return {
            "error": "Missing art data for mint",
            "messages": [{
                "agent": "Mint", 
                "level": "error",
                "message": "❌ Cannot mint without generated art CIDs",
                "ts": str(uuid.uuid4())
            }]
        }
    
    winner_cid = vote["result"]["winner_cid"]
    
    try:
        all_messages = []
        
        # Step 1: Build complete NFT metadata per schema
        start_message = {
            "agent": "Mint",
            "level": "info", 
            "message": "📋 Building NFT metadata from workflow state...",
            "ts": str(uuid.uuid4())
        }
        all_messages.append(start_message)
        
        # Update SSE immediately
        if run_id:
            current_messages = simple_state.get_run_state(run_id).get("messages", [])
            current_messages.append(start_message)
            simple_state.update_run_state(run_id, {"messages": current_messages})
        
        metadata = {
            "name": f"{lore.get('title', state['date_label'])} — {state['date_label']}",
            "description": f"Commemorative NFT capturing the historical significance of {state['date_label']}. {lore['summary_md'][:200]}{'...' if len(lore['summary_md']) > 200 else ''}",
            "image": winner_cid,
            "attributes": [
                {"trait_type": "Date", "value": state["date_label"]},
                {"trait_type": "Winner CID", "value": winner_cid},
                {"trait_type": "Sources", "value": len(lore["sources"])},
                {"trait_type": "Art Style", "value": lore["prompt_seed"].get("style", "Historical")},
                {"trait_type": "Participation", "value": vote["result"].get("participation", 0)},
                {"trait_type": "Voting Method", "value": "Blockchain Democracy"}
            ],
            "properties": {
                "summary_md": lore["summary_md"],
                "sources": lore["sources"], 
                "prompt_seed": lore["prompt_seed"],
                "vote_result": {
                    "winner_cid": winner_cid,
                    "tally": vote["result"].get("tally", {}),
                    "participation": vote["result"].get("participation", 0),
                    "fallback": vote["result"].get("fallback", False)
                },
                "art_options": art["cids"],
                "created_at": state['date_label']
            }
        }
        
        print(f"🪙 MINT: Built metadata - name: '{metadata['name'][:50]}...', attrs: {len(metadata['attributes'])}")
        
        # Step 2: Pin metadata to IPFS via MCP
        pin_message = {
            "agent": "Mint",
            "level": "info",
            "message": "📌 Pinning metadata to IPFS...",
            "ts": str(uuid.uuid4())
        }
        all_messages.append(pin_message)
        
        # Update SSE
        if run_id:
            current_messages = simple_state.get_run_state(run_id).get("messages", [])
            current_messages.append(pin_message)
            simple_state.update_run_state(run_id, {"messages": current_messages})
        
        mcp_client = get_mcp_client()
        pin_result = await mcp_client.pin_metadata(metadata)
        metadata_cid = pin_result.cid
        
        print(f"🪙 MINT: Metadata pinned to {metadata_cid}")
        
        # Step 3: Prepare mint transaction via MCP
        tx_message = {
            "agent": "Mint",
            "level": "info",
            "message": f"⚙️ Preparing mint transaction with metadata {metadata_cid[:20]}...",
            "ts": str(uuid.uuid4())
        }
        all_messages.append(tx_message)
        
        # Update SSE
        if run_id:
            current_messages = simple_state.get_run_state(run_id).get("messages", [])
            current_messages.append(tx_message)
            simple_state.update_run_state(run_id, {"messages": current_messages})
        
        # Get the vote ID from state
        vote_id = vote.get("id")
        print(f"🪙 MINT: Raw vote object from state: {vote}")
        print(f"🪙 MINT: Extracted vote ID: {vote_id}")
        
        if not vote_id:
            raise Exception("Vote ID missing from state - cannot prepare mint transaction")
        
        if vote_id == "0x" + "0" * 64:
            raise Exception(f"Vote ID is still fake/zero: {vote_id} - real vote ID not propagated!")
        
        print(f"🪙 MINT: ✅ Using REAL vote ID: {vote_id}")
        
        # Step 3a: First, check if we need to close the vote
        try:
            close_vote_response = await mcp_client.create_close_vote_transaction(vote_id)
            
            # Check if MCP server says vote is already closed
            if isinstance(close_vote_response, dict) and close_vote_response.get('skip_close'):
                print(f"🪙 MINT: Vote already closed, skipping close vote step")
                # Go directly to mint transaction - no close vote needed
                prepared_tx_obj = await mcp_client.create_mint_transaction(vote_id, winner_cid, metadata_cid)
                prepared_tx_obj.gas = max(prepared_tx_obj.gas or 100000, 200000)
                
                print(f"🪙 MINT: Mint transaction prepared directly - gas: {prepared_tx_obj.gas}")
                
                # Prepare mint receipt with metadata info
                mint_receipt = MintReceipt(
                    tx_hash="", # Will be filled after user confirms transaction
                    token_id="", # Will be extracted from transaction receipt
                    token_uri=metadata_cid
                )
                
                # Go straight to finalize_mint checkpoint
                checkpoint_message = {
                    "agent": "Mint",
                    "level": "info",
                    "message": "🎯 Vote already closed! Ready to mint NFT directly.",
                    "ts": str(uuid.uuid4()),
                    "links": [
                        {"label": "Metadata Preview", "href": metadata_cid},
                        {"label": "Winner Art", "href": winner_cid}
                    ]
                }
                all_messages.append(checkpoint_message)
                
                print(f"🪙 MINT: Set finalize_mint checkpoint (direct) with metadata {metadata_cid}")
                
                return {
                    "mint": mint_receipt.dict(),
                    "prepared_tx": {
                        "to": prepared_tx_obj.to,
                        "data": prepared_tx_obj.data,
                        "value": prepared_tx_obj.value,
                        "gas": prepared_tx_obj.gas
                    },
                    "metadata": metadata, # Include for preview in frontend
                    "checkpoint": "finalize_mint",
                    "messages": all_messages
                }
            
            # Normal case: close vote transaction needed
            close_vote_tx = close_vote_response
            
            # Ensure adequate gas for close vote (needs more due to winner calculation loop)
            if close_vote_tx.gas:
                close_vote_tx.gas = max(close_vote_tx.gas, 300000)
            else:
                close_vote_tx.gas = 300000
                
            print(f"🪙 MINT: Close vote transaction prepared - gas: {close_vote_tx.gas}")
            
        except Exception as close_vote_error:
            print(f"🪙 MINT: Error preparing close vote: {close_vote_error}")
            # Fallback: assume vote is already closed, go directly to mint
            print(f"🪙 MINT: Assuming vote already closed, proceeding to mint")
            prepared_tx_obj = await mcp_client.create_mint_transaction(vote_id, winner_cid, metadata_cid)
            prepared_tx_obj.gas = max(prepared_tx_obj.gas or 100000, 200000)
            
            # Prepare mint receipt with metadata info
            mint_receipt = MintReceipt(
                tx_hash="", # Will be filled after user confirms transaction
                token_id="", # Will be extracted from transaction receipt
                token_uri=metadata_cid
            )
            
            checkpoint_message = {
                "agent": "Mint",
                "level": "info",
                "message": "🎯 Vote appears closed! Ready to mint NFT directly.",
                "ts": str(uuid.uuid4()),
                "links": [
                    {"label": "Metadata Preview", "href": metadata_cid},
                    {"label": "Winner Art", "href": winner_cid}
                ]
            }
            all_messages.append(checkpoint_message)
            
            print(f"🪙 MINT: Set finalize_mint checkpoint (fallback) with metadata {metadata_cid}")
            
            return {
                "mint": mint_receipt.dict(),
                "prepared_tx": {
                    "to": prepared_tx_obj.to,
                    "data": prepared_tx_obj.data,
                    "value": prepared_tx_obj.value,
                    "gas": prepared_tx_obj.gas
                },
                "metadata": metadata, # Include for preview in frontend
                "checkpoint": "finalize_mint",
                "messages": all_messages
            }
        
        # Step 3b: Then, prepare the mint transaction (for after close vote)
        prepared_tx_obj = await mcp_client.create_mint_transaction(vote_id, winner_cid, metadata_cid)
        

        
        print(f"🪙 MINT: Mint transaction prepared - to: {prepared_tx_obj.to}, gas: {prepared_tx_obj.gas or 'auto'}")
        
        # Step 4: Set close_vote checkpoint for user confirmation (first step)
        checkpoint_message = {
            "agent": "Mint",
            "level": "info",
            "message": "🔐 Ready to close vote and mint NFT! First, we need to close the vote on-chain.",
            "ts": str(uuid.uuid4()),
            "links": [
                {"label": "Metadata Preview", "href": metadata_cid},
                {"label": "Winner Art", "href": winner_cid}
            ]
        }
        all_messages.append(checkpoint_message)
        
        # Prepare mint receipt with metadata info
        mint_receipt = MintReceipt(
            tx_hash="", # Will be filled after user confirms transactions
            token_id="", # Will be extracted from mint transaction receipt
            token_uri=metadata_cid
        )
        
        print(f"🪙 MINT: Set close_vote checkpoint with metadata {metadata_cid}")
        
        return {
            "mint": mint_receipt.dict(),
            "prepared_tx": {
                "to": close_vote_tx.to,
                "data": close_vote_tx.data,
                "value": close_vote_tx.value,
                "gas": close_vote_tx.gas
            },
            "mint_tx": {  # Store mint transaction for second step
                "to": prepared_tx_obj.to,
                "data": prepared_tx_obj.data,
                "value": prepared_tx_obj.value,
                "gas": prepared_tx_obj.gas
            },
            "metadata": metadata, # Include for preview in frontend
            "checkpoint": "close_vote",
            "messages": all_messages
        }
        
    except Exception as e:
        error_message = {
            "agent": "Mint",
            "level": "error",
            "message": f"❌ Mint preparation failed: {str(e)}",
            "ts": str(uuid.uuid4())
        }
        
        print(f"🪙 MINT: ERROR - {str(e)}")
        
        return {
            "error": f"Mint preparation failed: {str(e)}",
            "messages": [error_message]
        }