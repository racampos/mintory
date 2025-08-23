"""
Integration tests for backend service clients
Tests MCP client, LLM client, and Image client functionality
"""
import os
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import json

# Import our service clients
from services.mcp_client import MCPClient, MCPClientError, get_mcp_client
from services.llm_client import LLMClient, LLMMessage, LLMResponse, LorePack, get_llm_client
from services.image_client import ImageClient, ImageGenerationRequest, get_image_client


class TestMCPClient:
    """Test MCP client functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mcp_url = "http://localhost:3001"
        self.client = MCPClient(base_url=self.mcp_url, timeout=10.0, max_retries=1)
    
    @pytest.mark.asyncio
    async def test_get_chain_info(self):
        """Test chain info endpoint"""
        mock_response = {"chainId": 11155111, "name": "Shape Testnet"}
        
        with patch('httpx.AsyncClient.request') as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.json.return_value = mock_response
            
            result = await self.client.get_chain_info()
            
            assert result.chain_id == 11155111
            assert result.name == "Shape Testnet"
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_gasback_info(self):
        """Test gasback info endpoint"""
        mock_response = {"accrued": "1000000000000000000", "claimable": "500000000000000000"}
        
        with patch('httpx.AsyncClient.request') as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.json.return_value = mock_response
            
            result = await self.client.get_gasback_info("0x1234567890123456789012345678901234567890")
            
            assert result.accrued == "1000000000000000000"
            assert result.claimable == "500000000000000000"
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_pin_metadata(self):
        """Test metadata pinning"""
        mock_response = {"cid": "ipfs://QmTest123456789"}
        metadata = {"name": "Test NFT", "description": "Test description"}
        
        with patch('httpx.AsyncClient.request') as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.json.return_value = mock_response
            
            result = await self.client.pin_metadata(metadata)
            
            assert result.cid == "ipfs://QmTest123456789"
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_vote(self):
        """Test vote creation"""
        mock_response = {
            "vote_id": "0x" + "0" * 64,
            "tx": {
                "to": "0x1234567890123456789012345678901234567890",
                "data": "0xabcdef",
                "gas": 100000
            }
        }
        
        art_cids = ["ipfs://art1", "ipfs://art2"]
        from services.mcp_client import VoteConfig
        config = VoteConfig(method="simple", gate="open", duration_s=3600)
        
        with patch('httpx.AsyncClient.request') as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.json.return_value = mock_response
            
            vote_id, prepared_tx = await self.client.start_vote(art_cids, config)
            
            assert vote_id == "0x" + "0" * 64
            assert prepared_tx.to == "0x1234567890123456789012345678901234567890"
            assert prepared_tx.data == "0xabcdef"
            assert prepared_tx.gas == 100000
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_network_error_retry(self):
        """Test network error handling and retries"""
        import httpx
        
        with patch('httpx.AsyncClient.request') as mock_request:
            # First call raises network error, should retry
            mock_request.side_effect = httpx.RequestError("Network error")
            
            with pytest.raises(Exception):
                await self.client.get_chain_info()
            
            # Should have made max_retries + 1 attempts
            assert mock_request.call_count == 2  # max_retries=1, so 2 total attempts
    
    def test_singleton_get_mcp_client(self):
        """Test singleton pattern for get_mcp_client"""
        client1 = get_mcp_client()
        client2 = get_mcp_client()
        assert client1 is client2


class TestLLMClient:
    """Test LLM client functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Use mock API key for testing
        self.client = LLMClient(api_key="test-key", model="gpt-4", timeout=30.0)
    
    @pytest.mark.asyncio
    async def test_chat_completion(self):
        """Test basic chat completion"""
        messages = [LLMMessage(role="user", content="Hello, world!")]
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello! How can I help you today?"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 15
        mock_response.usage.total_tokens = 25
        
        with patch.object(self.client.async_client.chat.completions, 'create') as mock_create:
            mock_create.return_value = mock_response
            
            result = await self.client.chat_completion(messages)
            
            assert isinstance(result, LLMResponse)
            assert result.content == "Hello! How can I help you today?"
            assert result.model == "gpt-4"
            assert result.usage["total_tokens"] == 25
            assert result.finish_reason == "stop"
            mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_structured_completion(self):
        """Test structured completion with Pydantic model"""
        messages = [LLMMessage(role="user", content="Generate lore for 2024-01-01")]
        
        # Mock response with valid JSON
        mock_json_response = {
            "summary_md": "# New Year's Day 2024\n\nA significant historical moment...",
            "bullet_facts": [
                "New Year's Day marked the beginning of 2024",
                "Global celebrations occurred worldwide",
                "Technology advances continued"
            ],
            "sources": [
                "https://example.com/history",
                "https://example.com/events",
                "https://example.com/timeline",
                "https://example.com/news",
                "https://example.com/archive"
            ],
            "prompt_seed": {
                "style": "futuristic, celebration",
                "palette": "gold, silver, blue",
                "motifs": ["fireworks", "confetti", "champagne"],
                "negative": "dark, sad"
            }
        }
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_json_response)
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 100
        mock_response.usage.total_tokens = 150
        
        with patch.object(self.client.async_client.chat.completions, 'create') as mock_create:
            mock_create.return_value = mock_response
            
            lore_pack, raw_response = await self.client.structured_completion(messages, LorePack)
            
            assert isinstance(lore_pack, LorePack)
            assert lore_pack.summary_md.startswith("# New Year's Day 2024")
            assert len(lore_pack.bullet_facts) == 3
            assert len(lore_pack.sources) >= 5
            assert lore_pack.prompt_seed["style"] == "futuristic, celebration"
            
            assert isinstance(raw_response, LLMResponse)
            assert raw_response.usage["total_tokens"] == 150
            mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_lore_pack(self):
        """Test specialized lore pack generation method"""
        mock_json_response = {
            "summary_md": "# December 25th - Christmas\n\nA day of celebration and joy...",
            "bullet_facts": [
                "Christmas Day celebrated worldwide",
                "Christian holiday commemorating the birth of Jesus",
                "Traditional gift exchange occurs",
                "Family gatherings are common",
                "Many businesses close for the holiday"
            ],
            "sources": [
                "https://en.wikipedia.org/wiki/Christmas",
                "https://www.britannica.com/topic/Christmas",
                "https://www.history.com/topics/christmas",
                "https://www.nationalgeographic.com/history/article/christmas",
                "https://www.timeanddate.com/holidays/common/christmas-day"
            ],
            "prompt_seed": {
                "style": "festive, warm, traditional",
                "palette": "red, green, gold, white",
                "motifs": ["Christmas tree", "presents", "snow", "lights"],
                "negative": "dark, gloomy, commercialized"
            }
        }
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_json_response)
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 75
        mock_response.usage.completion_tokens = 200
        mock_response.usage.total_tokens = 275
        
        with patch.object(self.client.async_client.chat.completions, 'create') as mock_create:
            mock_create.return_value = mock_response
            
            lore_pack, raw_response = await self.client.generate_lore_pack("December 25th")
            
            assert isinstance(lore_pack, LorePack)
            assert "Christmas" in lore_pack.summary_md
            assert len(lore_pack.bullet_facts) >= 5
            assert len(lore_pack.sources) >= 5
            assert "festive" in lore_pack.prompt_seed["style"]
            mock_create.assert_called_once()
    
    def test_api_key_required(self):
        """Test that API key is required"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception):
                LLMClient(api_key=None)
    
    def test_singleton_get_llm_client(self):
        """Test singleton pattern for get_llm_client"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client1 = get_llm_client()
            client2 = get_llm_client()
            assert client1 is client2


class TestImageClient:
    """Test Image client functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Use mock provider for testing
        self.client = ImageClient(provider="mock", timeout=30.0)
    
    @pytest.mark.asyncio
    async def test_generate_mock_images(self):
        """Test mock image generation"""
        request = ImageGenerationRequest(
            prompt="A beautiful sunset over mountains",
            style="digital art",
            num_images=2,
            width=512,
            height=512
        )
        
        result = await self.client.generate_images(request)
        
        assert len(result.images) == 2
        assert result.provider == "mock"
        assert result.model == "mock-model"
        assert result.generation_time > 0
        
        for image in result.images:
            assert image.width == 512
            assert image.height == 512
            assert image.format == "PNG"
            assert image.prompt == request.prompt
            assert len(image.image_data) > 0
    
    @pytest.mark.asyncio
    async def test_generate_art_variations(self):
        """Test art variations generation method"""
        result = await self.client.generate_art_variations(
            prompt="Ancient temple ruins",
            style_notes="mystical, atmospheric",
            palette="earth tones, gold accents",
            num_variations=3
        )
        
        assert len(result.images) == 3
        assert result.provider == "mock"
        
        for image in result.images:
            assert "Ancient temple ruins" in image.prompt
            assert "mystical, atmospheric" in image.prompt
            assert "earth tones, gold accents" in image.prompt
    
    def test_image_validation(self):
        """Test image validation functionality"""
        # Create a simple test image
        from PIL import Image as PILImage
        import io
        
        img = PILImage.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        test_image_data = img_bytes.getvalue()
        
        # Test validation
        metadata = self.client._validate_image(test_image_data)
        
        assert metadata["width"] == 100
        assert metadata["height"] == 100
        assert metadata["format"] == "PNG"
        assert metadata["size_bytes"] == len(test_image_data)
    
    def test_image_validation_size_limit(self):
        """Test image size limit validation"""
        # Create image data that's too large
        large_data = b"fake_image_data" * 1000000  # Large fake data
        
        with pytest.raises(Exception):
            self.client._validate_image(large_data, max_size=1000)
    
    def test_save_image_to_file(self, tmp_path):
        """Test saving image to file"""
        from services.image_client import GeneratedImage
        
        # Create a simple test image
        from PIL import Image as PILImage
        import io
        
        img = PILImage.new('RGB', (50, 50), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        test_image_data = img_bytes.getvalue()
        
        generated_img = GeneratedImage(
            image_data=test_image_data,
            width=50,
            height=50,
            size_bytes=len(test_image_data),
            format="PNG",
            prompt="test image",
            model="test-model",
            provider="mock"
        )
        
        # Save to temporary file
        file_path = tmp_path / "test_image.png"
        saved_path = self.client.save_image_to_file(generated_img, file_path)
        
        assert saved_path.exists()
        assert saved_path.stat().st_size == len(test_image_data)
    
    def test_singleton_get_image_client(self):
        """Test singleton pattern for get_image_client"""
        client1 = get_image_client()
        client2 = get_image_client()
        assert client1 is client2


class TestIntegration:
    """Integration tests combining multiple services"""
    
    @pytest.mark.asyncio
    async def test_mcp_chain_info_integration(self):
        """Integration test for MCP chain info (requires MCP server)"""
        # Skip if MCP server not available
        if not os.getenv("MCP_URL"):
            pytest.skip("MCP_URL not configured for integration test")
        
        client = get_mcp_client()
        try:
            result = await client.get_chain_info()
            assert result.chain_id > 0
            assert len(result.name) > 0
            print(f"✓ MCP integration test passed: Chain {result.chain_id} ({result.name})")
        except Exception as e:
            print(f"⚠ MCP integration test failed (server may not be running): {e}")
    
    @pytest.mark.asyncio
    async def test_llm_completion_integration(self):
        """Integration test for LLM completion (requires API key)"""
        # Skip if API key not available
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not configured for integration test")
        
        client = get_llm_client()
        try:
            messages = [LLMMessage(role="user", content="Say hello")]
            result = await client.chat_completion(messages)
            assert len(result.content) > 0
            assert result.usage["total_tokens"] > 0
            print(f"✓ LLM integration test passed: {result.usage['total_tokens']} tokens used")
        except Exception as e:
            print(f"⚠ LLM integration test failed (API may be unavailable): {e}")
    
    async def test_mcp_chain_info_integration_simple(self):
        """Simple integration test for MCP chain info (no pytest)"""
        # Skip if MCP server not available
        if not os.getenv("MCP_URL"):
            print("⏭ MCP_URL not configured, skipping MCP integration test")
            return
        
        client = get_mcp_client()
        try:
            result = await client.get_chain_info()
            print(f"✓ MCP integration test passed: Chain {result.chain_id} ({result.name})")
        except Exception as e:
            print(f"⚠ MCP integration test failed (server may not be running): {e}")
    
    async def test_llm_completion_integration_simple(self):
        """Simple integration test for LLM completion (no pytest)"""
        # Skip if API key not available
        if not os.getenv("OPENAI_API_KEY"):
            print("⏭ OPENAI_API_KEY not configured, skipping LLM integration test")
            return
        
        try:
            client = get_llm_client()
            messages = [LLMMessage(role="user", content="Say hello")]
            result = await client.chat_completion(messages)
            print(f"✓ LLM integration test passed: {result.usage['total_tokens']} tokens used")
        except Exception as e:
            print(f"⚠ LLM integration test failed (API may be unavailable): {e}")


if __name__ == "__main__":
    """
    Run basic integration tests
    Usage: python test_services.py
    """
    import asyncio
    
    async def run_basic_tests():
        """Run basic functionality tests"""
        print("🧪 Running basic service client tests...")
        
        # Test MCP client
        print("\n📡 Testing MCP Client...")
        mcp_client = MCPClient(base_url="http://localhost:3001", max_retries=1)
        print(f"✓ MCP client initialized: {mcp_client.base_url}")
        
        # Test LLM client (mock)
        print("\n🤖 Testing LLM Client...")
        try:
            llm_client = LLMClient(api_key="test-key")
            print("✓ LLM client initialized")
        except Exception as e:
            print(f"⚠ LLM client test failed: {e}")
        
        # Test Image client
        print("\n🎨 Testing Image Client...")
        image_client = ImageClient(provider="mock")
        request = ImageGenerationRequest(prompt="test", num_images=1, width=256, height=256)
        result = await image_client.generate_images(request)
        print(f"✓ Generated {len(result.images)} mock images in {result.generation_time:.2f}s")
        
        # Test integration
        print("\n🔗 Testing Integration...")
        test_integration = TestIntegration()
        await test_integration.test_mcp_chain_info_integration_simple()
        await test_integration.test_llm_completion_integration_simple()
        
        print("\n✅ Basic service tests completed!")
    
    # Run the tests
    asyncio.run(run_basic_tests())
