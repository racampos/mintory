#!/usr/bin/env python3
"""
Comprehensive API test script for the Attested History backend
Tests all endpoints and demonstrates the full workflow
"""
import asyncio
import httpx
import json
import time
from typing import Dict, Any


class BackendTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.run_id = None

    async def test_health_check(self) -> bool:
        """Test the health endpoint"""
        print("🔍 Testing Health Check...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/health")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Health check passed")
                    print(f"   📊 Status: {data.get('status')}")
                    print(f"   🏷️  Service: {data.get('service')}")
                    return True
                else:
                    print(f"   ❌ Health check failed: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Health check error: {e}")
                return False

    async def test_create_run(self) -> bool:
        """Test creating a new run"""
        print("\n🚀 Testing Create Run...")
        
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "date_label": "2015-07-30 — Ethereum Genesis Block"
                }
                
                response = await client.post(
                    f"{self.base_url}/runs",
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.run_id = data["run_id"]
                    print(f"   ✅ Run created successfully")
                    print(f"   🆔 Run ID: {self.run_id}")
                    return True
                else:
                    print(f"   ❌ Create run failed: {response.status_code}")
                    print(f"   📄 Response: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Create run error: {e}")
                return False

    async def test_get_run_state(self) -> Dict[str, Any]:
        """Test getting run state"""
        print("\n📊 Testing Get Run State...")
        
        if not self.run_id:
            print("   ❌ No run ID available")
            return {}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/runs/{self.run_id}")
                
                if response.status_code == 200:
                    state = response.json()
                    print(f"   ✅ Run state retrieved")
                    print(f"   🏷️  Date Label: {state.get('date_label')}")
                    print(f"   🔒 Checkpoint: {state.get('checkpoint')}")
                    print(f"   📚 Has Lore: {'lore' in state and state['lore'] is not None}")
                    print(f"   🎨 Has Art: {'art' in state and state['art'] is not None}")
                    print(f"   🗳️  Has Vote: {'vote' in state and state['vote'] is not None}")
                    print(f"   🪙 Has Mint: {'mint' in state and state['mint'] is not None}")
                    print(f"   💬 Messages: {len(state.get('messages', []))}")
                    return state
                elif response.status_code == 404:
                    print(f"   ❌ Run not found: {self.run_id}")
                    return {}
                else:
                    print(f"   ❌ Get run state failed: {response.status_code}")
                    print(f"   📄 Response: {response.text}")
                    return {}
                    
            except Exception as e:
                print(f"   ❌ Get run state error: {e}")
                return {}

    async def test_sse_stream(self, duration: int = 10) -> bool:
        """Test SSE streaming"""
        print(f"\n🌊 Testing SSE Stream (for {duration} seconds)...")
        
        if not self.run_id:
            print("   ❌ No run ID available")
            return False
        
        async with httpx.AsyncClient() as client:
            try:
                event_count = 0
                start_time = time.time()
                
                async with client.stream('GET', f"{self.base_url}/runs/{self.run_id}/stream") as response:
                    print(f"   📡 Stream Status: {response.status_code}")
                    
                    if response.status_code != 200:
                        print(f"   ❌ Stream failed to start")
                        return False
                    
                    async for chunk in response.aiter_text():
                        if time.time() - start_time > duration:
                            break
                            
                        if chunk.strip():
                            event_count += 1
                            lines = chunk.strip().split('\n')
                            for line in lines:
                                if line.startswith('event:'):
                                    print(f"   📨 {line}")
                                elif line.startswith('data:') and len(line) < 200:
                                    print(f"   📦 {line[:100]}...")
                            
                            if event_count >= 5:  # Limit output
                                break
                
                print(f"   ✅ SSE stream test completed ({event_count} events)")
                return event_count > 0
                
            except Exception as e:
                print(f"   ❌ SSE stream error: {e}")
                return False

    async def test_resume_run(self, state: Dict[str, Any]) -> bool:
        """Test resuming a run at checkpoints"""
        print("\n▶️  Testing Resume Run...")
        
        if not self.run_id:
            print("   ❌ No run ID available")
            return False
        
        checkpoint = state.get('checkpoint')
        if not checkpoint:
            print("   ℹ️  No checkpoint found - run may have completed")
            return True
        
        async with httpx.AsyncClient() as client:
            try:
                # Test resume based on checkpoint type
                payload = {
                    "checkpoint": checkpoint,
                    "decision": "approve" if checkpoint == "lore_approval" else "finalize",
                    "payload": {}
                }
                
                print(f"   🔄 Attempting to resume at checkpoint: {checkpoint}")
                
                response = await client.post(
                    f"{self.base_url}/runs/{self.run_id}/resume",
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Resume successful")
                    print(f"   📊 Status: {data.get('status')}")
                    return True
                else:
                    print(f"   ❌ Resume failed: {response.status_code}")
                    print(f"   📄 Response: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Resume error: {e}")
                return False

    async def run_full_test(self):
        """Run the complete test suite"""
        print("🧪 Starting Comprehensive Backend API Test")
        print("=" * 50)
        
        results = []
        
        # Test 1: Health Check
        health_ok = await self.test_health_check()
        results.append(("Health Check", health_ok))
        
        if not health_ok:
            print("\n❌ Health check failed - aborting tests")
            return
        
        # Test 2: Create Run
        create_ok = await self.test_create_run()
        results.append(("Create Run", create_ok))
        
        if not create_ok:
            print("\n❌ Create run failed - aborting tests")
            return
        
        # Wait for initial processing
        print("\n⏳ Waiting 3 seconds for initial processing...")
        await asyncio.sleep(3)
        
        # Test 3: Get Run State
        state = await self.test_get_run_state()
        state_ok = bool(state)
        results.append(("Get Run State", state_ok))
        
        # Test 4: SSE Stream
        stream_ok = await self.test_sse_stream(duration=8)
        results.append(("SSE Stream", stream_ok))
        
        # Get updated state
        if state_ok:
            print("\n🔄 Getting updated state...")
            await asyncio.sleep(2)
            state = await self.test_get_run_state()
        
        # Test 5: Resume Run (if there's a checkpoint)
        resume_ok = await self.test_resume_run(state)
        results.append(("Resume Run", resume_ok))
        
        # Final Results
        print("\n" + "=" * 50)
        print("📋 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{test_name:.<20} {status}")
            if success:
                passed += 1
        
        print("-" * 50)
        print(f"Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Backend is fully functional.")
        else:
            print("⚠️  Some tests failed. Check the logs above.")
        
        # Final state check
        if self.run_id and state_ok:
            print(f"\n📊 Final Run State for {self.run_id}:")
            final_state = await self.test_get_run_state()


async def main():
    """Main test runner"""
    print("🔧 Attested History Backend API Tester")
    print("Make sure the backend server is running on http://localhost:8000\n")
    
    tester = BackendTester()
    await tester.run_full_test()


if __name__ == "__main__":
    asyncio.run(main())
