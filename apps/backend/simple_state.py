"""
Simplified state management for testing without checkpointer
"""
from typing import Dict, Any
import json

# In-memory storage for run states
run_states: Dict[str, Dict[str, Any]] = {}

def store_run_state(run_id: str, state: Dict[str, Any]):
    """Store run state in memory"""
    run_states[run_id] = state

def get_run_state(run_id: str) -> Dict[str, Any]:
    """Get run state from memory"""
    return run_states.get(run_id, {})

def update_run_state(run_id: str, updates: Dict[str, Any]):
    """Update run state with new data, properly merging messages"""
    if run_id not in run_states:
        run_states[run_id] = {}
    
    current_state = run_states[run_id]
    
    # Special handling for messages - we want to accumulate them, not replace them
    if "messages" in updates:
        current_messages = current_state.get("messages", [])
        new_messages = updates.get("messages", [])
        
        print(f"📦 STATE: Merging messages for {run_id}: current={len(current_messages)}, new={len(new_messages)}")
        
        # If updates has messages, merge them with existing ones
        if new_messages:
            # Merge messages, avoiding duplicates based on timestamp
            existing_timestamps = {msg.get("ts") for msg in current_messages}
            for new_msg in new_messages:
                if new_msg.get("ts") not in existing_timestamps:
                    current_messages.append(new_msg)
            
            print(f"📦 STATE: After merge: {len(current_messages)} total messages")
        
        # Make a copy of updates to avoid modifying the original
        updates = updates.copy()
        updates["messages"] = current_messages
    
    run_states[run_id].update(updates)

def list_runs() -> Dict[str, Dict[str, Any]]:
    """List all runs"""
    return run_states.copy()
