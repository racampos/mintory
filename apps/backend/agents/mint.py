"""
Mint Agent - Handle NFT minting via MCP tools
"""
import uuid
import httpx
from typing import Dict, Any
from state import RunState, MintReceipt


async def mint_agent(state: RunState) -> Dict[str, Any]:
    """
    Mint Agent: Finalize NFT mint
    
    Input: LorePack, winner_cid from vote
    Output: MintReceipt with tx_hash, token_id, token_uri
    """
    lore = state.get("lore")
    vote = state.get("vote")
    
    if not lore or not vote or not vote.get("result"):
        return {
            "error": "Missing lore or vote result for mint",
            "messages": [{
                "agent": "Mint",
                "level": "error",
                "message": "Missing required data for mint",
                "ts": str(uuid.uuid4())
            }]
        }
    
    winner_cid = vote["result"]["winner_cid"]
    
    try:
        # Small delay to allow SSE polling to detect intermediate state changes
        import asyncio
        await asyncio.sleep(0.05)  # 50ms delay for real-time streaming
        
        # Step 1: Create and pin metadata to IPFS
        metadata = {
            "name": f"{state['date_label']} — Historical NFT",
            "description": lore["summary_md"],
            "image": winner_cid,
            "attributes": [
                {"trait_type": "Date", "value": state["date_label"]},
                {"trait_type": "WinnerCID", "value": winner_cid},
                {"trait_type": "Sources", "value": len(lore["sources"])}
            ],
            "properties": {
                "summary_md": lore["summary_md"],
                "sources": lore["sources"],
                "prompt_seed": lore["prompt_seed"]
            }
        }
        
        # In production, pin metadata via MCP server
        # For demo, simulate metadata CID
        metadata_cid = f"ipfs://QmMetadata{uuid.uuid4().hex[:16]}"
        
        # Step 2: Call MCP server to prepare mint transaction
        # For demo, simulate mint result
        mint_receipt = MintReceipt(
            tx_hash=f"0x{uuid.uuid4().hex}",
            token_id="1",
            token_uri=metadata_cid
        )
        
        message = {
            "agent": "Mint",
            "level": "info",
            "message": f"Successfully minted NFT with token ID {mint_receipt.token_id}",
            "ts": str(uuid.uuid4()),
            "links": [
                {"label": "Transaction", "href": f"https://explorer.shape.network/tx/{mint_receipt.tx_hash}"},
                {"label": "Metadata", "href": metadata_cid},
                {"label": "Winner Art", "href": winner_cid}
            ]
        }
        
        return {
            "mint": mint_receipt.dict(),
            "messages": [message]
        }
        
    except Exception as e:
        return {
            "error": f"Mint failed: {str(e)}",
            "messages": [{
                "agent": "Mint",
                "level": "error",
                "message": f"Mint failed: {str(e)}",
                "ts": str(uuid.uuid4())
            }]
        }
