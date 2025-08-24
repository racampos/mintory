"""
FastAPI + LangGraph Backend Orchestrator

Implements REST endpoints and SSE streaming for the Attested History project.
"""
import asyncio
import json
import uuid
from typing import AsyncGenerator, Dict, Any
from contextlib import asynccontextmanager

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

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
    global workflows, checkpointer
    
    # Initialize the checkpointer first
    async with AsyncSqliteSaver.from_conn_string("checkpoints.db") as cp:
        checkpointer = cp
        # Initialize the workflow graph with the checkpointer
        workflow = create_workflow(checkpointer)
        workflows["main"] = workflow
        
        yield


app = FastAPI(
    title="Attested History Backend",
    description="LangGraph orchestrator for multi-agent NFT curation",
    version="1.0.0",
    lifespan=lifespan
)


def create_workflow(checkpointer) -> StateGraph:
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
    
    # Linear flow with checkpoints
    workflow.add_edge("lore", "artist")
    workflow.add_edge("artist", "vote") 
    workflow.add_edge("vote", "tally")
    workflow.add_edge("tally", "mint")
    workflow.add_edge("mint", END)
    
    # Compile with checkpointer and interrupt conditions
    return workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["artist"],  # Interrupt after lore for approval
        interrupt_after=["mint"]      # Interrupt after mint for finalize confirmation
    )


@app.post("/runs", response_model=CreateRunResponse)
async def create_run(request: CreateRunRequest, background_tasks: BackgroundTasks):
    """Start a new orchestration run"""
    
    run_id = str(uuid.uuid4())
    
    # Initial state (create as dict for LangGraph compatibility)
    initial_state: RunState = {
        "run_id": run_id,
        "date_label": request.date_label,
        "lore": None,
        "art": None,
        "vote": None,
        "mint": None,
        "attest": None,
        "checkpoint": None,
        "error": None,
        "messages": []
    }
    
    # Start the workflow in background
    background_tasks.add_task(start_workflow, run_id, initial_state)
    
    return CreateRunResponse(run_id=run_id)


async def start_workflow(run_id: str, initial_state: RunState):
    """Start workflow execution with real-time streaming"""
    try:
        workflow = workflows["main"]
        print(f"Starting workflow {run_id} with state: {initial_state}")
        
        # Store initial state
        simple_state.store_run_state(run_id, initial_state)
        
        # SSE polling is ultra-fast (10ms), no startup delay needed
        print(f"Starting workflow immediately for {run_id}...")
        
        # Run workflow with streaming - use "values" mode to get accumulated state after each node
        print(f"Streaming workflow for {run_id}...")
        
        # Create config for checkpointer with thread_id
        config = {"configurable": {"thread_id": run_id}}
        
        async for chunk in workflow.astream(initial_state, config=config, stream_mode="values"):
            print(f"📡 WORKFLOW: Node completed for {run_id}, accumulated state has {len(chunk.get('messages', []))} messages")
            
            # Debug: show which agents have completed
            completed_agents = []
            for key in ['lore', 'art', 'vote', 'mint']:
                if chunk.get(key) is not None:
                    completed_agents.append(key)
            print(f"📡 WORKFLOW: Completed agents: {completed_agents}")
            
            # Show messages in this accumulated state
            if chunk.get('messages'):
                print(f"📡 WORKFLOW: Messages in accumulated state:")
                for i, msg in enumerate(chunk['messages']):
                    print(f"  Message {i}: {msg.get('agent', '?')} - {msg.get('message', '')[:50]}...")
            
            # Update state immediately with accumulated state for real-time streaming
            simple_state.update_run_state(run_id, chunk)
            print(f"📡 WORKFLOW: Updated state for {run_id} with {len(chunk.get('messages', []))} messages")
        
        print(f"Workflow {run_id} streaming completed successfully")
        
    except Exception as e:
        print(f"Workflow {run_id} error: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        
        # Store error state
        error_state = dict(initial_state)
        error_state["error"] = str(e)
        simple_state.update_run_state(run_id, error_state)


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
async def stream_run(run_id: str, last_message_index: int = 0):
    """Stream run updates via SSE"""
    
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            print(f"Starting SSE stream for run {run_id}")
            
            # Check if run exists
            current_state = simple_state.get_run_state(run_id)
            if not current_state:
                error_data = {"run_id": run_id, "error": f"Run {run_id} not found"}
                yield f"event: error\n"
                yield f"data: {json.dumps(error_data)}\n\n"
                return
            
            # If workflow is already complete, send only unseen messages, then completion
            if current_state.get("mint") and not current_state.get("error"):
                print(f"Run {run_id} already completed, sending messages from index {last_message_index} then completion event")
                
                # Send only unseen agent messages
                messages = current_state.get("messages", [])
                unseen_messages = messages[last_message_index:] if last_message_index < len(messages) else []
                print(f"Sending {len(unseen_messages)} unseen messages out of {len(messages)} total")
                
                for message in unseen_messages:
                    yield f"event: update\n"
                    yield f"data: {json.dumps(message)}\n\n"
                    await asyncio.sleep(0.1)  # Small delay for better UX
                
                # Send final state update
                state_update = {
                    "run_id": run_id,
                    "state_update": {
                        key: current_state.get(key)
                        for key in ["lore", "art", "vote", "mint", "checkpoint"]
                        if current_state.get(key) is not None
                    }
                }
                yield f"event: state\n"
                yield f"data: {json.dumps(state_update)}\n\n"
                await asyncio.sleep(0.1)
                
                # Send completion event
                completion_data = {"run_id": run_id, "status": "completed"}
                yield f"event: complete\n"
                yield f"data: {json.dumps(completion_data)}\n\n"
                return
            
            # If workflow has error, send only unseen messages, then error
            if current_state.get("error"):
                print(f"Run {run_id} has error, sending messages from index {last_message_index} then error event")
                
                # Send only unseen messages that were generated before error
                messages = current_state.get("messages", [])
                unseen_messages = messages[last_message_index:] if last_message_index < len(messages) else []
                print(f"Sending {len(unseen_messages)} unseen messages out of {len(messages)} total before error")
                
                for message in unseen_messages:
                    yield f"event: update\n"
                    yield f"data: {json.dumps(message)}\n\n"
                    await asyncio.sleep(0.1)
                
                # Send error event
                error_data = {"run_id": run_id, "error": current_state["error"]}
                yield f"event: error\n"
                yield f"data: {json.dumps(error_data)}\n\n"
                return
            
            print(f"Starting live stream monitoring for run {run_id}, resuming from message index {last_message_index}")
            last_message_count = last_message_index  # Resume from where client left off
            last_state = {}
            
            # Poll for state changes and stream them
            for poll_count in range(600):  # 10 minutes max (enough for image generation)
                try:
                    current_state = simple_state.get_run_state(run_id)
                    print(f"SSE Poll #{poll_count} for {run_id}: {len(current_state.get('messages', []))} messages, keys: {list(current_state.keys())}")
                    
                    if not current_state:
                        print(f"No state found for {run_id}, ending SSE stream")
                        break
                except Exception as poll_error:
                    print(f"Error during SSE poll #{poll_count} for {run_id}: {poll_error}")
                    raise
                
                # Check for new messages ONLY - this is the most important check
                messages = current_state.get("messages", [])
                current_message_count = len(messages)
                
                if current_message_count > last_message_count:
                    print(f"📡 SSE: New messages detected: {current_message_count} vs {last_message_count}")
                    try:
                        # Only send the NEW messages, not all messages
                        new_messages = messages[last_message_count:]
                        for new_message in new_messages:
                            print(f"📡 SSE: Streaming NEW message: {new_message.get('agent')} - {new_message.get('message', '')[:50]}")
                            yield f"event: update\n"
                            yield f"data: {json.dumps(new_message)}\n\n"
                        
                        last_message_count = current_message_count
                        print(f"📡 SSE: Updated last_message_count to {last_message_count}")
                    except Exception as stream_error:
                        print(f"Error streaming messages for {run_id}: {stream_error}")
                        raise
                
                # Check for ACTUAL state changes in non-message fields
                # Use deep comparison for the important state keys
                state_changed = False
                changed_keys = []
                
                for key in ["lore", "art", "vote", "mint", "error", "checkpoint"]:
                    current_value = current_state.get(key)
                    last_value = last_state.get(key)
                    
                    # Deep comparison for these state keys
                    if json.dumps(current_value, sort_keys=True, default=str) != json.dumps(last_value, sort_keys=True, default=str):
                        state_changed = True
                        changed_keys.append(key)
                
                if state_changed:
                    print(f"📡 SSE: ACTUAL state change detected for {run_id}: {changed_keys}")
                    try:
                        # Send state update
                        state_update = {
                            "run_id": run_id,
                            "state_update": {
                                key: current_state.get(key)
                                for key in ["lore", "art", "vote", "mint", "error", "checkpoint"]
                                if current_state.get(key) is not None
                            }
                        }
                        yield f"event: state\n"
                        yield f"data: {json.dumps(state_update)}\n\n"
                        print(f"📡 SSE: Successfully sent state update for {run_id}")
                        
                        # Update last_state with deep copy of non-message fields
                        last_state = {
                            key: current_state.get(key)
                            for key in ["lore", "art", "vote", "mint", "error", "checkpoint"]
                            if current_state.get(key) is not None
                        }
                        
                    except Exception as state_error:
                        print(f"Error sending state update for {run_id}: {state_error}")
                        raise
                else:
                    if poll_count % 500 == 0:  # Log every 500 polls (~5s) to reduce noise
                        print(f"📡 SSE: No state changes detected for {run_id} (poll #{poll_count})")
                
                # Check if workflow is complete
                if current_state.get("mint") and not current_state.get("error"):
                    print(f"Workflow {run_id} completed, ending SSE stream")
                    try:
                        completion_data = {"run_id": run_id, "status": "completed"}
                        yield f"event: complete\n"
                        yield f"data: {json.dumps(completion_data)}\n\n"
                        print(f"Successfully sent completion event for {run_id}")
                        break
                    except Exception as completion_error:
                        print(f"Error sending completion event for {run_id}: {completion_error}")
                        raise
                
                # Check for errors
                if current_state.get("error"):
                    print(f"Workflow {run_id} has error, ending SSE stream")
                    error_data = {"run_id": run_id, "error": current_state["error"]}
                    yield f"event: error\n"
                    yield f"data: {json.dumps(error_data)}\n\n"
                    break
                
                await asyncio.sleep(1)  # Poll every second
            
            # If we exit the poll loop without completion/error
            print(f"SSE polling loop ended for {run_id} (max iterations reached or other reason)")
                
        except Exception as e:
            print(f"Stream error for {run_id}: {e}")
            error_data = {"run_id": run_id, "error": str(e)}
            yield f"event: error\n"
            yield f"data: {json.dumps(error_data)}\n\n"
    
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
        
        # Handle different resume decisions - just clear checkpoint, don't restart workflow
        if request.checkpoint == "lore_approval":
            if request.decision == "approve":
                # Just approve - no input needed, workflow will continue from checkpoint
                current_state["checkpoint"] = None
            elif request.decision == "edit":
                # Apply edits from payload
                if "lore" in request.payload:
                    current_state["lore"] = request.payload["lore"]
                current_state["checkpoint"] = None
        
        elif request.checkpoint == "finalize_mint":
            if request.decision == "finalize":
                # Add a completion message and clear checkpoint
                completion_message = {
                    "agent": "System",
                    "level": "info", 
                    "message": "Mint finalized by user approval",
                    "ts": str(uuid.uuid4())
                }
                current_state.setdefault("messages", []).append(completion_message)
                current_state["checkpoint"] = None
            else:
                raise HTTPException(status_code=400, detail="Invalid decision for finalize_mint")
        
        # Update state in storage
        simple_state.update_run_state(run_id, current_state)
        
        # Resume the workflow with LangGraph - NO INPUT, just continue from checkpoint
        workflow = workflows["main"]
        config = {"configurable": {"thread_id": run_id}}
        
        # Resume the workflow execution in the background with NO input
        import asyncio
        asyncio.create_task(continue_workflow_after_resume(run_id, config))
        
        return {"status": "resumed", "state": current_state}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def continue_workflow_after_resume(run_id: str, config: Dict[str, Any]):
    """Continue workflow execution after resume - NO input to continue from checkpoint"""
    try:
        workflow = workflows["main"]
        print(f"🔄 Resuming workflow for {run_id} from checkpoint (no input)")
        
        # Continue streaming from checkpoint - NO INPUT so it resumes from where it left off
        async for chunk in workflow.astream(None, config=config, stream_mode="values"):
            print(f"📡 WORKFLOW RESUME: Node completed for {run_id}, accumulated state has {len(chunk.get('messages', []))} messages")
            
            # Update state immediately with accumulated state for real-time streaming
            simple_state.update_run_state(run_id, chunk)
            print(f"📡 WORKFLOW RESUME: Updated state for {run_id} with {len(chunk.get('messages', []))} messages")
        
        print(f"Workflow {run_id} resumed and completed successfully")
        
    except Exception as e:
        print(f"Workflow {run_id} resume error: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        
        # Store error state
        current_state = simple_state.get_run_state(run_id) or {}
        current_state["error"] = str(e)
        simple_state.update_run_state(run_id, current_state)


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
