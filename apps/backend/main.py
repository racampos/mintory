"""
FastAPI + LangGraph Backend Orchestrator

Implements REST endpoints and SSE streaming for the Attested History project.
"""
import asyncio
import json
import uuid
from typing import AsyncGenerator, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

from langgraph.graph import StateGraph, END

from state import RunState
from agents.lore import lore_agent
from agents.artist import artist_agent
from agents.vote import vote_agent, tally_vote_agent
from agents.mint import mint_agent
import simple_state


# Request/Response models
class CreateRunRequest(BaseModel):
    date_label: str


class CreateRunResponse(BaseModel):
    run_id: str


class ResumeRunRequest(BaseModel):
    checkpoint: str  # "lore_approval" | "art_sanity" | "finalize_mint"
    decision: str    # "approve" | "edit" | "proceed" | "regen" | "finalize"
    payload: Dict[str, Any] = {}


# Global state
workflows: Dict[str, StateGraph] = {}
checkpointer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize LangGraph workflow"""
    global workflows
    
    # Initialize the workflow graph
    workflow = create_workflow()
    workflows["main"] = workflow
    
    yield


app = FastAPI(
    title="Attested History Backend",
    description="LangGraph orchestrator for multi-agent NFT curation",
    version="1.0.0",
    lifespan=lifespan
)


def create_workflow() -> StateGraph:
    """Create the LangGraph workflow with agents and checkpoints"""
    
    workflow = StateGraph(RunState)
    
    # Add agent nodes
    workflow.add_node("lore", lore_agent)
    workflow.add_node("artist", artist_agent) 
    workflow.add_node("vote", vote_agent)
    workflow.add_node("tally", tally_vote_agent)
    workflow.add_node("mint", mint_agent)
    
    # Define the flow
    workflow.set_entry_point("lore")
    
    # Simple linear flow for now
    workflow.add_edge("lore", "artist")
    workflow.add_edge("artist", "vote")
    workflow.add_edge("vote", "tally")
    workflow.add_edge("tally", "mint")
    workflow.add_edge("mint", END)
    
    # Compile without checkpointer first to test basic functionality
    return workflow.compile()


@app.post("/runs", response_model=CreateRunResponse)
async def create_run(request: CreateRunRequest, background_tasks: BackgroundTasks):
    """Start a new orchestration run"""
    
    run_id = str(uuid.uuid4())
    
    # Initial state
    initial_state = RunState(
        run_id=run_id,
        date_label=request.date_label,
        lore=None,
        art=None,
        vote=None,
        mint=None,
        attest=None,
        checkpoint=None,
        error=None,
        messages=[]
    )
    
    # Start the workflow in background
    background_tasks.add_task(start_workflow, run_id, initial_state)
    
    return CreateRunResponse(run_id=run_id)


async def start_workflow(run_id: str, initial_state: RunState):
    """Start workflow execution"""
    try:
        workflow = workflows["main"]
        
        # Store initial state
        simple_state.store_run_state(run_id, initial_state)
        
        # Run workflow synchronously for now
        result = await workflow.ainvoke(initial_state)
        
        # Store final result
        simple_state.update_run_state(run_id, result)
        
        print(f"Workflow {run_id} completed: {result}")
        
    except Exception as e:
        print(f"Workflow {run_id} error: {e}")
        simple_state.update_run_state(run_id, {"error": str(e)})


@app.get("/runs/{run_id}")
async def get_run(run_id: str) -> Dict[str, Any]:
    """Get current state of a run"""
    try:
        state = simple_state.get_run_state(run_id)
        
        if not state:
            raise HTTPException(status_code=404, detail="Run not found")
            
        return state
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/runs/{run_id}/stream")
async def stream_run(run_id: str):
    """Stream run updates via SSE"""
    
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            workflow = workflows["main"]
            config = {"configurable": {"thread_id": run_id}}
            
            # Stream updates directly - let the workflow handle state management
            async for event in workflow.astream(None, config, stream_mode="updates"):
                # Format SSE event
                event_data = {
                    "run_id": run_id,
                    "event": event,
                    "timestamp": str(uuid.uuid4())  # Use UUID as timestamp
                }
                
                yield f"event: update\n"
                yield f"data: {json.dumps(event_data)}\n\n"
                
                # Small delay to allow client to process
                await asyncio.sleep(0.1)
                
        except Exception as e:
            yield f"event: error\n"
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable Nginx buffering
        }
    )


@app.post("/runs/{run_id}/resume")
async def resume_run(run_id: str, request: ResumeRunRequest):
    """Resume a run after checkpoint approval"""
    try:
        # Get current state from simple storage
        current_state = simple_state.get_run_state(run_id)
        
        if not current_state:
            raise HTTPException(status_code=404, detail="Run not found")
        
        checkpoint = current_state.get("checkpoint")
        if not checkpoint:
            return {"status": "already_completed", "state": current_state}
        
        # Handle different resume decisions
        if request.checkpoint == "lore_approval":
            if request.decision == "approve":
                # Clear checkpoint to proceed
                current_state["checkpoint"] = None
            elif request.decision == "edit":
                # Apply edits from payload
                if "lore" in request.payload:
                    current_state["lore"] = request.payload["lore"]
                current_state["checkpoint"] = None
        
        elif request.checkpoint == "finalize_mint":
            if request.decision == "finalize":
                current_state["checkpoint"] = None
                # Add a completion message
                current_state.setdefault("messages", []).append({
                    "agent": "System",
                    "level": "info", 
                    "message": "Mint finalized by user approval",
                    "ts": str(uuid.uuid4())
                })
            else:
                raise HTTPException(status_code=400, detail="Invalid decision for finalize_mint")
        
        # Update state in storage
        simple_state.update_run_state(run_id, current_state)
        
        return {"status": "resumed", "state": current_state}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "attested-history-backend"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
