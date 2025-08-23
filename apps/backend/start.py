#!/usr/bin/env python3
"""
Start script for the Attested History backend server
"""
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn


def main():
    """Start the FastAPI server"""
    port = int(os.getenv("BACKEND_PORT", 8000))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    
    print(f"🚀 Starting Attested History Backend on {host}:{port}")
    print("📊 Health check: http://localhost:8000/health")
    print("📖 API docs: http://localhost:8000/docs")
    print("🔄 SSE stream: http://localhost:8000/runs/{run_id}/stream")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
