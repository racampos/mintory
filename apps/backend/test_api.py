#!/usr/bin/env python3
"""
Simple API test script for the backend
"""
import asyncio
import httpx
import json


async def test_backend():
    """Test the backend API endpoints"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🔍 Testing backend API...")
        
        # Test health check
        print("\n1. Health Check:")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test create run
        print("\n2. Create Run:")
        try:
            response = await client.post(
                f"{base_url}/runs",
                json={"date_label": "2015-07-30 — Ethereum Genesis Block"}
            )
            print(f"   Status: {response.status_code}")
            run_data = response.json()
            print(f"   Response: {run_data}")
            
            if response.status_code == 200:
                run_id = run_data["run_id"]
                
                # Wait a moment for the workflow to start
                await asyncio.sleep(2)
                
                # Test get run state
                print(f"\n3. Get Run State (ID: {run_id}):")
                try:
                    response = await client.get(f"{base_url}/runs/{run_id}")
                    print(f"   Status: {response.status_code}")
                    if response.status_code == 200:
                        state = response.json()
                        print(f"   Checkpoint: {state.get('checkpoint')}")
                        print(f"   Has Lore: {'lore' in state and state['lore'] is not None}")
                        print(f"   Messages: {len(state.get('messages', []))}")
                except Exception as e:
                    print(f"   Error: {e}")
                
                # Test SSE stream (brief)
                print(f"\n4. SSE Stream Test (5 seconds):")
                try:
                    timeout = 5.0
                    async with client.stream('GET', f"{base_url}/runs/{run_id}/stream") as response:
                        print(f"   Status: {response.status_code}")
                        if response.status_code == 200:
                            count = 0
                            async for chunk in response.aiter_text():
                                if chunk.strip():
                                    print(f"   Event {count}: {chunk.strip()[:100]}...")
                                    count += 1
                                    if count >= 3:  # Limit output
                                        break
                        else:
                            print(f"   Error: {response.status_code}")
                            
                except Exception as e:
                    print(f"   Error: {e}")
                    
        except Exception as e:
            print(f"   Error: {e}")
        
        print("\n✅ API test completed!")


if __name__ == "__main__":
    asyncio.run(test_backend())
