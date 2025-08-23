"""
LLM Client - OpenAI client for language model interactions
Supports chat completions and structured outputs for Lore Agent research
"""
import os
import logging
from typing import Dict, Any, List, Optional, Union, Type
from dataclasses import dataclass, asdict
import json
from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)


@dataclass
class LLMMessage:
    """Message in LLM conversation"""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """LLM response with metadata"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str


class LorePack(BaseModel):
    """Structured output for Lore Agent research"""
    summary_md: str
    bullet_facts: List[str]
    sources: List[str]
    prompt_seed: Dict[str, Any]


class LLMClientError(Exception):
    """Base exception for LLM client errors"""
    pass


class LLMConfigError(LLMClientError):
    """Configuration-related LLM errors"""
    pass


class LLMAPIError(LLMClientError):
    """API-related LLM errors"""
    pass


class LLMClient:
    """
    OpenAI client for language model interactions
    Supports both chat completions and structured outputs
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        timeout: float = 60.0
    ):
        """
        Initialize LLM client
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use for completions
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 to 1.0)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise LLMConfigError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
        
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout
        
        # Initialize OpenAI clients
        self.client = OpenAI(api_key=self.api_key, timeout=timeout)
        self.async_client = AsyncOpenAI(api_key=self.api_key, timeout=timeout)
        
        logger.info(f"Initialized LLM client with model: {self.model}")
    
    def _format_messages(self, messages: List[Union[LLMMessage, Dict[str, str]]]) -> List[Dict[str, str]]:
        """
        Format messages for OpenAI API
        
        Args:
            messages: List of messages
            
        Returns:
            Formatted messages for API
        """
        formatted = []
        for msg in messages:
            if isinstance(msg, LLMMessage):
                formatted.append({"role": msg.role, "content": msg.content})
            elif isinstance(msg, dict):
                formatted.append(msg)
            else:
                raise LLMClientError(f"Invalid message type: {type(msg)}")
        return formatted
    
    async def chat_completion(
        self,
        messages: List[Union[LLMMessage, Dict[str, str]]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """
        Generate chat completion
        
        Args:
            messages: Conversation messages
            model: Model to use (overrides default)
            max_tokens: Max tokens (overrides default)
            temperature: Temperature (overrides default)
            system_prompt: System prompt to prepend
            
        Returns:
            LLMResponse with completion and metadata
        """
        # Format messages
        formatted_messages = self._format_messages(messages)
        
        # Add system prompt if provided
        if system_prompt:
            formatted_messages.insert(0, {"role": "system", "content": system_prompt})
        
        # Use provided parameters or defaults
        call_model = model or self.model
        call_max_tokens = max_tokens or self.max_tokens
        call_temperature = temperature or self.temperature
        
        try:
            logger.debug(f"Making chat completion request with {len(formatted_messages)} messages")
            
            response = await self.async_client.chat.completions.create(
                model=call_model,
                messages=formatted_messages,
                max_tokens=call_max_tokens,
                temperature=call_temperature
            )
            
            # Extract response data
            choice = response.choices[0]
            content = choice.message.content or ""
            
            usage = {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            }
            
            logger.info(f"Chat completion successful: {usage['total_tokens']} tokens used")
            
            return LLMResponse(
                content=content,
                model=call_model,
                usage=usage,
                finish_reason=choice.finish_reason or "unknown"
            )
            
        except Exception as e:
            logger.error(f"Chat completion error: {e}")
            raise LLMAPIError(f"Chat completion failed: {e}")
    
    async def structured_completion(
        self,
        messages: List[Union[LLMMessage, Dict[str, str]]],
        response_model: Type[BaseModel],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None
    ) -> tuple[BaseModel, LLMResponse]:
        """
        Generate structured completion with Pydantic model validation
        
        Args:
            messages: Conversation messages
            response_model: Pydantic model for structured output
            model: Model to use (overrides default)
            max_tokens: Max tokens (overrides default)
            temperature: Temperature (overrides default)
            system_prompt: System prompt to prepend
            
        Returns:
            Tuple of (parsed_model, raw_response)
        """
        # Add JSON schema instructions to system prompt
        schema = response_model.model_json_schema()
        json_instructions = f"""
You must respond with valid JSON that matches this exact schema:

{json.dumps(schema, indent=2)}

Respond only with the JSON object, no additional text or explanation.
"""
        
        full_system_prompt = system_prompt + "\n\n" + json_instructions if system_prompt else json_instructions
        
        # Get completion
        response = await self.chat_completion(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system_prompt=full_system_prompt
        )
        
        # Parse structured output
        try:
            # Try to extract JSON from response
            content = response.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            
            # Try to extract JSON object from potentially verbose response
            # Look for the first { and last } to extract just the JSON part
            start_idx = content.find('{')
            end_idx = content.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                raise json.JSONDecodeError("No JSON object found in response", content, 0)
            
            json_content = content[start_idx:end_idx + 1]
            
            # Parse JSON
            parsed_json = json.loads(json_content)
            
            # Validate with Pydantic model
            structured_data = response_model.model_validate(parsed_json)
            
            logger.info(f"Structured completion successful for {response_model.__name__}")
            return structured_data, response
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.debug(f"Raw content: {response.content}")
            raise LLMAPIError(f"Failed to parse JSON response: {e}")
        except Exception as e:
            logger.error(f"Model validation error: {e}")
            raise LLMAPIError(f"Failed to validate structured output: {e}")
    
    async def generate_lore_pack(self, date_label: str) -> tuple[LorePack, LLMResponse]:
        """
        Generate a LorePack for historical research (specialized method for Lore Agent)
        
        Args:
            date_label: Historical date to research
            
        Returns:
            Tuple of (LorePack, raw_response)
        """
        system_prompt = """
You are a historical research agent for an NFT creation platform. Research the given historical date and provide detailed historical context.

You MUST respond with a valid JSON object that contains these exact fields:

{
  "summary_md": "A 150-200 word markdown summary of the historical significance",
  "bullet_facts": ["5-10 interesting bullet points about events/people/developments"],
  "sources": ["5+ real HTTP/HTTPS URLs related to the historical events"],
  "prompt_seed": {
    "style": "artistic style description for image generation",
    "palette": "color palette description",
    "motifs": ["visual elements and themes"],
    "negative": "things to avoid in the art"
  }
}

Requirements:
- summary_md: Write in markdown format, exactly 150-200 words about the historical significance
- bullet_facts: Provide 5-10 concise, interesting facts as an array of strings
- sources: Include 5+ real, working HTTP/HTTPS URLs (Wikipedia, .edu, .gov, major news sites)
- prompt_seed.style: Describe the artistic style that would capture this historical moment
- prompt_seed.palette: Describe colors that represent this period/event
- prompt_seed.motifs: List visual elements that symbolize this historical moment
- prompt_seed.negative: List things to avoid in the artistic representation

Focus on technological, cultural, or socially significant events. Make it inspiring for NFT art creation.
Respond ONLY with the JSON object, no additional text before or after.
"""
        
        messages = [
            LLMMessage(
                role="user",
                content=f"Research and provide historical context for this date: {date_label}. Focus on events that would inspire compelling digital art creation."
            )
        ]
        
        return await self.structured_completion(
            messages=messages,
            response_model=LorePack,
            system_prompt=system_prompt,
            temperature=0.8  # Slightly higher for creative content
        )
    
    def sync_chat_completion(
        self,
        messages: List[Union[LLMMessage, Dict[str, str]]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """
        Synchronous version of chat_completion for non-async contexts
        
        Args:
            messages: Conversation messages
            model: Model to use (overrides default)
            max_tokens: Max tokens (overrides default)
            temperature: Temperature (overrides default)
            system_prompt: System prompt to prepend
            
        Returns:
            LLMResponse with completion and metadata
        """
        # Format messages
        formatted_messages = self._format_messages(messages)
        
        # Add system prompt if provided
        if system_prompt:
            formatted_messages.insert(0, {"role": "system", "content": system_prompt})
        
        # Use provided parameters or defaults
        call_model = model or self.model
        call_max_tokens = max_tokens or self.max_tokens
        call_temperature = temperature or self.temperature
        
        try:
            logger.debug(f"Making sync chat completion request with {len(formatted_messages)} messages")
            
            response = self.client.chat.completions.create(
                model=call_model,
                messages=formatted_messages,
                max_tokens=call_max_tokens,
                temperature=call_temperature
            )
            
            # Extract response data
            choice = response.choices[0]
            content = choice.message.content or ""
            
            usage = {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            }
            
            logger.info(f"Sync chat completion successful: {usage['total_tokens']} tokens used")
            
            return LLMResponse(
                content=content,
                model=call_model,
                usage=usage,
                finish_reason=choice.finish_reason or "unknown"
            )
            
        except Exception as e:
            logger.error(f"Sync chat completion error: {e}")
            raise LLMAPIError(f"Sync chat completion failed: {e}")


# Global LLM client instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    Get global LLM client instance (singleton pattern)
    
    Returns:
        LLMClient instance
    """
    global _llm_client
    if _llm_client is None:
        model = os.getenv("OPENAI_MODEL", "gpt-4")
        max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "4096"))
        temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        timeout = float(os.getenv("OPENAI_TIMEOUT", "60.0"))
        
        _llm_client = LLMClient(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=timeout
        )
    return _llm_client
