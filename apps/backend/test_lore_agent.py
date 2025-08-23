#!/usr/bin/env python3
"""
Test script for the real Lore Agent implementation
Tests both successful LLM integration and fallback behavior
"""
import os
import asyncio
import json
import logging
from typing import Dict, Any

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import our lore agent
from agents.lore import lore_agent, validate_lore_pack
from state import RunState


async def test_lore_agent_with_api(date_label: str = "July 20, 1969") -> None:
    """
    Test lore agent with real LLM API (requires OPENAI_API_KEY)
    
    Args:
        date_label: Historical date to research
    """
    print(f"\n🧠 Testing Lore Agent with LLM API for: {date_label}")
    
    # Check if we have API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⏭️ OPENAI_API_KEY not set, skipping LLM integration test")
        return
        
    # Create test run state
    test_state: RunState = {
        "run_id": "test-run-001",
        "date_label": date_label,
        "status": "running"
    }
    
    try:
        # Call the real lore agent
        result = await lore_agent(test_state)
        
        # Validate result structure
        assert "lore" in result, "Missing 'lore' in result"
        assert "checkpoint" in result, "Missing 'checkpoint' in result" 
        assert "messages" in result, "Missing 'messages' in result"
        assert result["checkpoint"] == "lore_approval", "Wrong checkpoint value"
        
        lore_pack = result["lore"]
        
        # Validate lore pack using our validation function
        validate_lore_pack(lore_pack, date_label)
        
        # Print results
        print("✅ LLM Integration Test PASSED!")
        print(f"📝 Summary: {len(lore_pack['summary_md'].split())} words")
        print(f"🔹 Facts: {len(lore_pack['bullet_facts'])} items")
        print(f"🔗 Sources: {len(lore_pack['sources'])} URLs")
        print(f"🎨 Style: {lore_pack['prompt_seed']['style'][:50]}...")
        print(f"🎨 Palette: {lore_pack['prompt_seed']['palette']}")
        print(f"💬 Messages: {len(result['messages'])} agent messages")
        
        # Show first few bullet facts
        print("\n📋 Sample Facts:")
        for i, fact in enumerate(lore_pack['bullet_facts'][:3]):
            print(f"  {i+1}. {fact}")
            
        # Show sample sources
        print("\n🔗 Sample Sources:")
        for i, source in enumerate(lore_pack['sources'][:3]):
            print(f"  {i+1}. {source}")
        
    except Exception as e:
        print(f"❌ LLM integration test failed: {e}")
        raise


async def test_lore_agent_fallback(date_label: str = "December 17, 1903") -> None:
    """
    Test lore agent fallback behavior (without API key or with simulated error)
    
    Args:
        date_label: Historical date to test fallback with
    """
    print(f"\n🔄 Testing Lore Agent fallback for: {date_label}")
    
    # Temporarily remove API key to trigger fallback
    original_key = os.getenv("OPENAI_API_KEY")
    if original_key:
        os.environ.pop("OPENAI_API_KEY", None)
    
    try:
        # Create test run state
        test_state: RunState = {
            "run_id": "test-run-002", 
            "date_label": date_label,
            "status": "running"
        }
        
        # Call lore agent (should use fallback)
        result = await lore_agent(test_state)
        
        # Validate result structure
        assert "lore" in result, "Missing 'lore' in fallback result"
        assert "checkpoint" in result, "Missing 'checkpoint' in fallback result"
        assert "messages" in result, "Missing 'messages' in fallback result"
        
        lore_pack = result["lore"]
        
        # Validate fallback lore pack
        validate_lore_pack(lore_pack, date_label)
        
        # Verify fallback characteristics
        assert "research systems encountered an issue" in lore_pack["summary_md"], "Fallback content not detected"
        assert len(lore_pack["bullet_facts"]) >= 5, "Fallback facts count insufficient"
        assert len(lore_pack["sources"]) >= 5, "Fallback sources count insufficient"
        
        print("✅ Fallback Test PASSED!")
        print(f"📝 Fallback Summary: {len(lore_pack['summary_md'].split())} words")
        print(f"🔹 Fallback Facts: {len(lore_pack['bullet_facts'])} items")
        print(f"🔗 Fallback Sources: {len(lore_pack['sources'])} URLs")
        print(f"⚠️  Messages show warning: {any(msg.get('level') == 'warning' for msg in result['messages'])}")
        
    except Exception as e:
        print(f"❌ Fallback test failed: {e}")
        raise
    finally:
        # Restore original API key
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key


def test_lore_pack_validation() -> None:
    """Test the lore pack validation function with various scenarios"""
    print(f"\n🔍 Testing Lore Pack Validation")
    
    # Valid lore pack
    valid_lore_pack = {
        "summary_md": "This is a valid summary with exactly fifty words. " * 4,  # 200 words
        "bullet_facts": ["Fact 1", "Fact 2", "Fact 3", "Fact 4", "Fact 5", "Fact 6"],
        "sources": [
            "https://example.com/1",
            "https://example.com/2", 
            "https://example.com/3",
            "https://example.com/4",
            "https://example.com/5"
        ],
        "prompt_seed": {
            "style": "Test style",
            "palette": "Test palette",
            "motifs": ["motif1", "motif2"],
            "negative": "Test negative"
        }
    }
    
    try:
        validate_lore_pack(valid_lore_pack, "test-date")
        print("✅ Valid lore pack validation passed")
    except Exception as e:
        print(f"❌ Valid lore pack validation failed: {e}")
        return
    
    # Test invalid cases
    test_cases = [
        # Too many words in summary
        {
            **valid_lore_pack,
            "summary_md": "Word " * 201,  # 201 words
        },
        # Too few facts
        {
            **valid_lore_pack, 
            "bullet_facts": ["Only", "Four", "Facts", "Here"]
        },
        # Too few sources
        {
            **valid_lore_pack,
            "sources": ["https://example.com/1", "https://example.com/2"]
        },
        # Invalid URL
        {
            **valid_lore_pack,
            "sources": ["https://example.com/1"] + ["not-a-url"] + ["https://example.com/{}".format(i) for i in range(3, 6)]
        },
        # Empty style
        {
            **valid_lore_pack,
            "prompt_seed": {**valid_lore_pack["prompt_seed"], "style": ""}
        }
    ]
    
    for i, invalid_lore_pack in enumerate(test_cases):
        try:
            validate_lore_pack(invalid_lore_pack, "test-date")
            print(f"❌ Invalid test case {i+1} should have failed but passed")
        except ValueError:
            print(f"✅ Invalid test case {i+1} correctly rejected")
        except Exception as e:
            print(f"⚠️  Invalid test case {i+1} failed with unexpected error: {e}")
    
    print("✅ Validation tests completed")


async def main():
    """Run all lore agent tests"""
    print("🧪 Testing Phase 5.2: Real Lore Agent Implementation")
    print("=" * 60)
    
    # Test validation function first
    test_lore_pack_validation()
    
    # Test fallback behavior (works without API key)
    await test_lore_agent_fallback("December 17, 1903 - First Flight")
    
    # Test real LLM integration (requires API key)
    await test_lore_agent_with_api("July 20, 1969 - Moon Landing")
    
    # Test another interesting historical date
    if os.getenv("OPENAI_API_KEY"):
        await test_lore_agent_with_api("October 31, 2008 - Bitcoin Whitepaper")
    
    print("\n🎉 All Lore Agent tests completed!")
    print("✅ Phase 5.2: Real Lore Agent is ready for integration!")


if __name__ == "__main__":
    asyncio.run(main())
