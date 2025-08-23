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
    """Update run state with new data"""
    if run_id not in run_states:
        run_states[run_id] = {}
    
    run_states[run_id].update(updates)

def list_runs() -> Dict[str, Dict[str, Any]]:
    """List all runs"""
    return run_states.copy()
