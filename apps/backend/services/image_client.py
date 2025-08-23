"""
Image Client - Image generation client supporting multiple providers
Handles prompt-based generation with style parameters and validation
"""
import os
import logging
import tempfile
import hashlib
from typing import Dict, Any, List, Optional, Union, Literal
from dataclasses import dataclass
from pathlib import Path
import httpx
import asyncio
from PIL import Image
import io

logger = logging.getLogger(__name__)


ImageProvider = Literal["openai", "stability", "midjourney", "mock"]


@dataclass
class ImageGenerationRequest:
    """Image generation request parameters"""
    prompt: str
    style: Optional[str] = None
    negative_prompt: Optional[str] = None
    width: int = 1024
    height: int = 1024
    num_images: int = 1
    quality: str = "standard"  # "standard" or "hd" for DALL-E
    model: Optional[str] = None


@dataclass
class GeneratedImage:
    """Generated image result"""
    image_data: bytes
    width: int
    height: int
    size_bytes: int
    format: str
    prompt: str
    model: str
    provider: str


@dataclass
class ImageGenerationResult:
    """Complete image generation result"""
    images: List[GeneratedImage]
    provider: str
    model: str
    generation_time: float
    total_cost: Optional[float] = None


class ImageClientError(Exception):
    """Base exception for image client errors"""
    pass


class ImageConfigError(ImageClientError):
    """Configuration-related image client errors"""
    pass


class ImageGenerationError(ImageClientError):
    """Image generation errors"""
    pass


class ImageValidationError(ImageClientError):
    """Image validation errors"""
    pass


class ImageClient:
    """
    Multi-provider image generation client
    Supports OpenAI DALL-E, Stability AI, Midjourney, and mock generation
    """
    
    def __init__(
        self,
        provider: ImageProvider = "mock",
        api_key: Optional[str] = None,
        timeout: float = 120.0,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        supported_formats: List[str] = None
    ):
        """
        Initialize image generation client
        
        Args:
            provider: Image generation provider to use
            api_key: API key for the provider (if required)
            timeout: Request timeout in seconds
            max_file_size: Maximum file size in bytes
            supported_formats: Supported image formats
        """
        self.provider = provider
        self.timeout = timeout
        self.max_file_size = max_file_size
        self.supported_formats = supported_formats or ["PNG", "JPEG", "WEBP"]
        
        # Set up provider-specific configuration
        if provider == "openai":
            from openai import AsyncOpenAI
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ImageConfigError("OpenAI API key required for DALL-E generation")
            self.client = AsyncOpenAI(api_key=self.api_key, timeout=timeout)
            
        elif provider == "stability":
            self.api_key = api_key or os.getenv("STABILITY_API_KEY")
            if not self.api_key:
                raise ImageConfigError("Stability AI API key required")
            self.base_url = "https://api.stability.ai"
            
        elif provider == "midjourney":
            self.api_key = api_key or os.getenv("MIDJOURNEY_API_KEY")
            if not self.api_key:
                raise ImageConfigError("Midjourney API key required")
            # Note: Midjourney doesn't have official API, would need unofficial service
            
        elif provider == "mock":
            # Mock provider for testing
            pass
        else:
            raise ImageConfigError(f"Unsupported provider: {provider}")
        
        logger.info(f"Initialized image client with provider: {provider}")
    
    def _validate_image(self, image_data: bytes, max_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Validate image data and extract metadata
        
        Args:
            image_data: Raw image bytes
            max_size: Maximum file size (defaults to client max_file_size)
            
        Returns:
            Dictionary with image metadata
            
        Raises:
            ImageValidationError: If image is invalid or too large
        """
        max_size = max_size or self.max_file_size
        
        # Check file size
        if len(image_data) > max_size:
            raise ImageValidationError(f"Image too large: {len(image_data)} bytes (max: {max_size})")
        
        # Validate image format and extract metadata
        try:
            with Image.open(io.BytesIO(image_data)) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                    "size_bytes": len(image_data)
                }
        except Exception as e:
            raise ImageValidationError(f"Invalid image data: {e}")
    
    def _create_generated_image(
        self,
        image_data: bytes,
        prompt: str,
        model: str
    ) -> GeneratedImage:
        """
        Create GeneratedImage object with validation
        
        Args:
            image_data: Raw image bytes
            prompt: Generation prompt
            model: Model used for generation
            
        Returns:
            GeneratedImage object
        """
        metadata = self._validate_image(image_data)
        
        return GeneratedImage(
            image_data=image_data,
            width=metadata["width"],
            height=metadata["height"],
            size_bytes=metadata["size_bytes"],
            format=metadata["format"],
            prompt=prompt,
            model=model,
            provider=self.provider
        )
    
    async def _generate_openai_dalle(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """
        Generate images using OpenAI DALL-E
        
        Args:
            request: Image generation request
            
        Returns:
            ImageGenerationResult with generated images
        """
        import time
        start_time = time.time()
        
        try:
            # Prepare DALL-E request
            dalle_model = request.model or "dall-e-3"
            size = f"{request.width}x{request.height}"
            
            # DALL-E 3 only supports specific sizes
            if dalle_model == "dall-e-3":
                if size not in ["1024x1024", "1024x1792", "1792x1024"]:
                    logger.warning(f"Adjusting size from {size} to 1024x1024 for DALL-E 3")
                    size = "1024x1024"
                    request.width = request.height = 1024
            
            # Build full prompt with style
            full_prompt = request.prompt
            if request.style:
                full_prompt += f", {request.style}"
            
            logger.info(f"Generating {request.num_images} image(s) with DALL-E {dalle_model}")
            
            response = await self.client.images.generate(
                model=dalle_model,
                prompt=full_prompt,
                size=size,
                quality=request.quality,
                n=request.num_images,
                response_format="b64_json"
            )
            
            # Process generated images
            images = []
            for img_data in response.data:
                if img_data.b64_json:
                    import base64
                    image_bytes = base64.b64decode(img_data.b64_json)
                    generated_img = self._create_generated_image(
                        image_bytes, full_prompt, dalle_model
                    )
                    images.append(generated_img)
            
            generation_time = time.time() - start_time
            logger.info(f"Generated {len(images)} images in {generation_time:.2f} seconds")
            
            return ImageGenerationResult(
                images=images,
                provider="openai",
                model=dalle_model,
                generation_time=generation_time
            )
            
        except Exception as e:
            logger.error(f"DALL-E generation error: {e}")
            raise ImageGenerationError(f"DALL-E generation failed: {e}")
    
    async def _generate_stability_ai(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """
        Generate images using Stability AI
        
        Args:
            request: Image generation request
            
        Returns:
            ImageGenerationResult with generated images
        """
        import time
        start_time = time.time()
        
        try:
            model = request.model or "stable-diffusion-xl-1024-v1-0"
            
            # Prepare Stability AI request
            payload = {
                "text_prompts": [{"text": request.prompt}],
                "cfg_scale": 7,
                "height": request.height,
                "width": request.width,
                "samples": request.num_images,
                "steps": 30,
            }
            
            if request.negative_prompt:
                payload["text_prompts"].append({
                    "text": request.negative_prompt,
                    "weight": -1
                })
            
            if request.style:
                payload["style_preset"] = request.style
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"Generating {request.num_images} image(s) with Stability AI {model}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/v1/generation/{model}/text-to-image",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code != 200:
                    raise ImageGenerationError(f"Stability AI API error: {response.status_code} - {response.text}")
                
                result = response.json()
                
                # Process generated images
                images = []
                for artifact in result.get("artifacts", []):
                    if artifact.get("base64"):
                        import base64
                        image_bytes = base64.b64decode(artifact["base64"])
                        generated_img = self._create_generated_image(
                            image_bytes, request.prompt, model
                        )
                        images.append(generated_img)
                
                generation_time = time.time() - start_time
                logger.info(f"Generated {len(images)} images in {generation_time:.2f} seconds")
                
                return ImageGenerationResult(
                    images=images,
                    provider="stability",
                    model=model,
                    generation_time=generation_time
                )
            
        except Exception as e:
            logger.error(f"Stability AI generation error: {e}")
            raise ImageGenerationError(f"Stability AI generation failed: {e}")
    
    async def _generate_mock(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """
        Generate mock images for testing
        
        Args:
            request: Image generation request
            
        Returns:
            ImageGenerationResult with mock generated images
        """
        import time
        start_time = time.time()
        
        # Simulate generation time
        await asyncio.sleep(0.5)
        
        logger.info(f"Generating {request.num_images} mock image(s)")
        
        images = []
        for i in range(request.num_images):
            # Create a simple colored image
            img = Image.new('RGB', (request.width, request.height), color=(100 + i * 30, 150, 200 + i * 20))
            
            # Save to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            image_data = img_bytes.getvalue()
            
            generated_img = self._create_generated_image(
                image_data, request.prompt, "mock-model"
            )
            images.append(generated_img)
        
        generation_time = time.time() - start_time
        logger.info(f"Generated {len(images)} mock images in {generation_time:.2f} seconds")
        
        return ImageGenerationResult(
            images=images,
            provider="mock",
            model="mock-model",
            generation_time=generation_time
        )
    
    async def generate_images(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """
        Generate images using the configured provider
        
        Args:
            request: Image generation request
            
        Returns:
            ImageGenerationResult with generated images
        """
        logger.info(f"Starting image generation with provider: {self.provider}")
        
        if self.provider == "openai":
            return await self._generate_openai_dalle(request)
        elif self.provider == "stability":
            return await self._generate_stability_ai(request)
        elif self.provider == "midjourney":
            raise ImageGenerationError("Midjourney provider not yet implemented")
        elif self.provider == "mock":
            return await self._generate_mock(request)
        else:
            raise ImageConfigError(f"Unknown provider: {self.provider}")
    
    async def generate_art_variations(
        self,
        prompt: str,
        style_notes: str,
        palette: str,
        num_variations: int = 4
    ) -> ImageGenerationResult:
        """
        Generate art variations with consistent style (specialized method for Artist Agent)
        
        Args:
            prompt: Base art prompt
            style_notes: Style guidance
            palette: Color palette description
            num_variations: Number of variations to generate
            
        Returns:
            ImageGenerationResult with art variations
        """
        # Build enhanced prompt
        full_prompt = f"{prompt}. Style: {style_notes}. Color palette: {palette}."
        
        request = ImageGenerationRequest(
            prompt=full_prompt,
            style=style_notes,
            num_images=num_variations,
            width=1024,
            height=1024
        )
        
        return await self.generate_images(request)
    
    def save_image_to_file(self, image: GeneratedImage, file_path: Union[str, Path]) -> Path:
        """
        Save generated image to file
        
        Args:
            image: Generated image
            file_path: Path to save to
            
        Returns:
            Path where image was saved
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'wb') as f:
            f.write(image.image_data)
        
        logger.info(f"Saved image to {path} ({image.size_bytes} bytes)")
        return path
    
    def save_images_to_temp_files(self, images: List[GeneratedImage]) -> List[Path]:
        """
        Save generated images to temporary files
        
        Args:
            images: List of generated images
            
        Returns:
            List of temporary file paths
        """
        temp_files = []
        for i, image in enumerate(images):
            # Create unique filename based on prompt hash
            prompt_hash = hashlib.md5(image.prompt.encode()).hexdigest()[:8]
            extension = image.format.lower()
            filename = f"generated_{prompt_hash}_{i}.{extension}"
            
            temp_file = Path(tempfile.gettempdir()) / filename
            self.save_image_to_file(image, temp_file)
            temp_files.append(temp_file)
        
        return temp_files


# Global image client instance
_image_client: Optional[ImageClient] = None


def get_image_client() -> ImageClient:
    """
    Get global image client instance (singleton pattern)
    
    Returns:
        ImageClient instance
    """
    global _image_client
    if _image_client is None:
        provider = os.getenv("IMAGE_GEN_PROVIDER", "mock")
        timeout = float(os.getenv("IMAGE_GEN_TIMEOUT", "120.0"))
        max_file_size = int(os.getenv("IMAGE_MAX_FILE_SIZE", str(10 * 1024 * 1024)))
        
        _image_client = ImageClient(
            provider=provider,
            timeout=timeout,
            max_file_size=max_file_size
        )
    return _image_client
