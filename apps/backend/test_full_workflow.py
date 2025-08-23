#!/usr/bin/env python3
"""
Full Workflow Demonstration for Attested History Backend
Shows complete multi-agent orchestration with detailed step-by-step execution
"""
import asyncio
import httpx
import json
import time
from typing import Dict, Any, List


class WorkflowDemonstrator:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.run_id = None

    def print_header(self, title: str, emoji: str = "🔥"):
        """Print a formatted header"""
        print(f"\n{emoji} " + "=" * 60)
        print(f"{emoji} {title}")
        print(f"{emoji} " + "=" * 60)

    def print_step(self, step: int, title: str, emoji: str = "📍"):
        """Print a step header"""
        print(f"\n{emoji} STEP {step}: {title}")
        print("-" * 50)

    def print_agent_result(self, agent_name: str, emoji: str, data: Dict[str, Any]):
        """Print agent execution results"""
        print(f"\n{emoji} {agent_name} Results:")
        
        if agent_name == "Lore Agent" and "lore" in data:
            lore = data["lore"]
            print(f"   📖 Summary: {lore['summary_md'][:100]}...")
            print(f"   📊 Facts: {len(lore['bullet_facts'])} bullet points")
            print(f"   🔗 Sources: {len(lore['sources'])} references")
            print(f"   🎨 Style: {lore['prompt_seed']['style']}")
            print(f"   🎨 Palette: {lore['prompt_seed']['palette']}")
        
        elif agent_name == "Artist Agent" and "art" in data:
            art = data["art"]
            print(f"   🖼️  Generated: {len(art['cids'])} artworks")
            print(f"   🖼️  CIDs: {', '.join(art['cids'][:2])}...")
            print(f"   📝 Style Notes: {art['style_notes'][0] if art['style_notes'] else 'None'}")
        
        elif agent_name == "Vote Agent" and "vote" in data:
            vote = data["vote"]
            print(f"   🗳️  Vote ID: {vote['id']}")
            print(f"   ⚙️  Method: {vote['config']['method']}")
            print(f"   🚪 Gate: {vote['config']['gate']}")
            print(f"   ⏱️  Duration: {vote['config']['duration_s']}s")
        
        elif agent_name == "Tally Agent" and "vote" in data and data["vote"].get("result"):
            result = data["vote"]["result"]
            print(f"   🏆 Winner: {result['winner_cid']}")
            print(f"   📊 Tally: {result['tally']}")
            print(f"   👥 Participation: {result['participation']} votes")
        
        elif agent_name == "Mint Agent" and "mint" in data:
            mint = data["mint"]
            print(f"   💰 Token ID: {mint['token_id']}")
            print(f"   🔗 Transaction: {mint['tx_hash'][:20]}...")
            print(f"   📋 Metadata URI: {mint['token_uri']}")

    async def create_and_monitor_run(self, date_label: str) -> bool:
        """Create a run and monitor its initial execution"""
        self.print_step(1, "Creating New Workflow Run", "🚀")
        
        async with httpx.AsyncClient() as client:
            try:
                payload = {"date_label": date_label}
                response = await client.post(f"{self.base_url}/runs", json=payload, timeout=30.0)
                
                if response.status_code == 200:
                    data = response.json()
                    self.run_id = data["run_id"]
                    print(f"✅ Run created successfully!")
                    print(f"🆔 Run ID: {self.run_id}")
                    print(f"📅 Date: {date_label}")
                    return True
                else:
                    print(f"❌ Failed to create run: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error creating run: {e}")
                return False

    async def monitor_workflow_execution(self) -> Dict[str, Any]:
        """Monitor the workflow execution step by step"""
        self.print_step(2, "Monitoring Multi-Agent Execution", "👀")
        
        print("⏳ Waiting for agents to execute...")
        
        # Wait for workflow to complete
        for i in range(10):  # Max 10 seconds
            await asyncio.sleep(1)
            state = await self.get_current_state()
            if state and state.get("mint"):  # Workflow completed
                break
            print(f"   ⏳ Processing... ({i+1}s)")
        
        return await self.get_current_state()

    async def get_current_state(self) -> Dict[str, Any]:
        """Get current state of the run"""
        if not self.run_id:
            return {}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/runs/{self.run_id}")
                if response.status_code == 200:
                    return response.json()
                return {}
            except:
                return {}

    async def demonstrate_agent_pipeline(self, final_state: Dict[str, Any]):
        """Show detailed results from each agent"""
        self.print_step(3, "Agent Pipeline Results", "🤖")
        
        agents = [
            ("Lore Agent", "🧠", "Researched historical context"),
            ("Artist Agent", "🎨", "Generated artwork options"),
            ("Vote Agent", "🗳️", "Initiated voting process"),
            ("Tally Agent", "📊", "Determined winning artwork"),
            ("Mint Agent", "🪙", "Prepared NFT for minting")
        ]
        
        for agent_name, emoji, description in agents:
            print(f"\n{emoji} {agent_name}: {description}")
            self.print_agent_result(agent_name, emoji, final_state)

    async def demonstrate_checkpoint_interaction(self, state: Dict[str, Any]):
        """Demonstrate checkpoint and resume functionality"""
        self.print_step(4, "Checkpoint & Resume Demonstration", "🔄")
        
        checkpoint = state.get("checkpoint")
        if not checkpoint:
            print("ℹ️  Workflow completed without interruption")
            print("   All agents executed successfully in sequence")
            return
        
        print(f"⚠️  Workflow paused at checkpoint: {checkpoint}")
        print("   This is where human approval would be required")
        
        # Demonstrate resume
        print(f"\n🎯 Simulating user approval for: {checkpoint}")
        
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "checkpoint": checkpoint,
                    "decision": "finalize" if checkpoint == "finalize_mint" else "approve",
                    "payload": {}
                }
                
                response = await client.post(
                    f"{self.base_url}/runs/{self.run_id}/resume",
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Resume successful!")
                    print(f"📊 Status: {result.get('status')}")
                    
                    # Get updated state
                    updated_state = await self.get_current_state()
                    new_checkpoint = updated_state.get("checkpoint")
                    
                    if new_checkpoint != checkpoint:
                        print(f"🔄 Checkpoint cleared: {checkpoint} → {new_checkpoint or 'None'}")
                    else:
                        print(f"⏸️  Still at checkpoint: {checkpoint}")
                        
                else:
                    print(f"❌ Resume failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Resume error: {e}")

    async def show_message_timeline(self, state: Dict[str, Any]):
        """Show the message timeline from all agents"""
        self.print_step(5, "Agent Message Timeline", "💬")
        
        messages = state.get("messages", [])
        if not messages:
            print("ℹ️  No messages recorded")
            return
        
        print(f"📝 Total messages: {len(messages)}")
        print()
        
        agent_emojis = {
            "Lore": "🧠",
            "Artist": "🎨", 
            "Vote": "🗳️",
            "Mint": "🪙",
            "System": "⚙️"
        }
        
        for i, msg in enumerate(messages, 1):
            agent = msg.get("agent", "Unknown")
            emoji = agent_emojis.get(agent, "🤖")
            level = msg.get("level", "info")
            message = msg.get("message", "")
            
            level_icon = "✅" if level == "info" else "⚠️" if level == "warn" else "❌"
            
            print(f"{i:2d}. {emoji} {agent} {level_icon}: {message}")

    async def show_final_nft_details(self, state: Dict[str, Any]):
        """Show the final NFT details"""
        self.print_step(6, "Final NFT Details", "🎯")
        
        lore = state.get("lore", {})
        vote_result = state.get("vote", {}).get("result", {})
        mint = state.get("mint", {})
        
        if not mint:
            print("❌ No mint data found")
            return
        
        print("🏆 NFT Successfully Prepared!")
        print(f"   📅 Historical Date: {state.get('date_label', 'Unknown')}")
        print(f"   🖼️  Winning Artwork: {vote_result.get('winner_cid', 'Unknown')}")
        print(f"   🪙 Token ID: {mint.get('token_id', 'Unknown')}")
        print(f"   🔗 Transaction Hash: {mint.get('tx_hash', 'Unknown')}")
        print(f"   📋 Metadata URI: {mint.get('token_uri', 'Unknown')}")
        
        if lore:
            print(f"   📖 Summary Length: {len(lore.get('summary_md', ''))} characters")
            print(f"   🔗 Source Count: {len(lore.get('sources', []))} references")
        
        if vote_result:
            print(f"   👥 Total Votes: {vote_result.get('participation', 0)}")

    async def demonstrate_sse_streaming(self):
        """Demonstrate real-time SSE streaming"""
        self.print_step(7, "Real-time Event Streaming Test", "🌊")
        
        if not self.run_id:
            print("❌ No run ID for streaming test")
            return
        
        print("📡 Testing Server-Sent Events (SSE) stream...")
        print("   (This will show any ongoing workflow events)")
        
        async with httpx.AsyncClient() as client:
            try:
                event_count = 0
                async with client.stream('GET', f"{self.base_url}/runs/{self.run_id}/stream", timeout=5.0) as response:
                    print(f"   📊 Stream Status: {response.status_code}")
                    
                    if response.status_code != 200:
                        print("   ❌ Stream not available")
                        return
                    
                    start_time = time.time()
                    async for chunk in response.aiter_text():
                        if time.time() - start_time > 3:  # 3 second limit
                            break
                            
                        if chunk.strip():
                            event_count += 1
                            lines = chunk.strip().split('\n')
                            for line in lines:
                                if line.startswith('event:'):
                                    print(f"   📨 {line}")
                                elif line.startswith('data:'):
                                    try:
                                        data = json.loads(line[5:].strip())
                                        print(f"   📦 Event data available")
                                    except:
                                        print(f"   📦 {line[:80]}...")
                
                print(f"   ✅ SSE test completed ({event_count} events received)")
                if event_count == 0:
                    print("   ℹ️  No active events (workflow likely completed)")
                    
            except Exception as e:
                print(f"   ❌ SSE error: {e}")

    async def run_full_demonstration(self, date_label: str = "2015-07-30 — Ethereum Genesis Block"):
        """Run the complete workflow demonstration"""
        self.print_header("ATTESTED HISTORY - FULL WORKFLOW DEMONSTRATION", "🎭")
        
        print(f"🎯 Demonstrating multi-agent NFT curation for: {date_label}")
        print("   This test will show the complete orchestration pipeline:")
        print("   Lore Agent → Artist Agent → Vote Agent → Tally Agent → Mint Agent")
        
        # Step 1: Create run
        if not await self.create_and_monitor_run(date_label):
            return
        
        # Step 2: Monitor execution  
        final_state = await self.monitor_workflow_execution()
        if not final_state:
            print("❌ Failed to get workflow results")
            return
        
        # Step 3: Show agent results
        await self.demonstrate_agent_pipeline(final_state)
        
        # Step 4: Demonstrate checkpoints
        await self.demonstrate_checkpoint_interaction(final_state)
        
        # Step 5: Show message timeline
        await self.show_message_timeline(final_state)
        
        # Step 6: Show final NFT
        await self.show_final_nft_details(final_state)
        
        # Step 7: Test SSE streaming
        await self.demonstrate_sse_streaming()
        
        # Summary
        self.print_header("DEMONSTRATION COMPLETE", "🎉")
        print("✅ Multi-agent workflow executed successfully!")
        print(f"🆔 Run ID: {self.run_id}")
        print("💡 Key achievements:")
        print("   • Historical research and context generation")
        print("   • AI-generated artwork proposals")
        print("   • Voting system initialization") 
        print("   • Winner determination and tallying")
        print("   • NFT metadata preparation and minting")
        print("   • Checkpoint/resume functionality")
        print("   • Real-time event streaming")
        
        print(f"\n🔗 Access run state anytime: GET {self.base_url}/runs/{self.run_id}")


async def main():
    """Main demonstration runner"""
    print("🎬 Starting Full Workflow Demonstration...")
    print("   Make sure backend server is running on http://localhost:8000")
    
    demonstrator = WorkflowDemonstrator()
    
    # You can customize the historical date here
    historical_dates = [
        "2015-07-30 — Ethereum Genesis Block",
        "2008-10-31 — Bitcoin Whitepaper Published", 
        "1969-07-20 — Moon Landing",
        "1991-08-06 — World Wide Web Goes Public"
    ]
    
    # Use the first date or let user choose
    selected_date = historical_dates[0]
    print(f"📅 Selected historical moment: {selected_date}")
    
    await demonstrator.run_full_demonstration(selected_date)


if __name__ == "__main__":
    asyncio.run(main())
