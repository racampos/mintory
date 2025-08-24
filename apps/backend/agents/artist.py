"""
Artist Agent - Image generation using OpenAI gpt-image-1 with IPFS integration
"""
import os
import time
import uuid
import base64
import pathlib
import asyncio
from typing import Dict, Any, List, Optional
from openai import OpenAI
from PIL import Image
from io import BytesIO
from state import RunState, ArtSet
from services.mcp_client import get_mcp_client
import requests


def write_b64_image(path: pathlib.Path, b64: str) -> None:
    """Write base64 image data to file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as f:
        f.write(base64.b64decode(b64))


def validate_image_size(filepath: pathlib.Path, max_size_mb: float = 2.0) -> bool:
    """Validate that image file is under size limit."""
    if not filepath.exists():
        return False
    size_mb = filepath.stat().st_size / (1024 * 1024)
    return size_mb <= max_size_mb


def create_thumbnail(image_path: pathlib.Path, max_size_kb: float = 200.0) -> Optional[bytes]:
    """
    Create thumbnail from image file with size validation.
    
    Args:
        image_path: Path to source image
        max_size_kb: Maximum thumbnail size in KB
        
    Returns:
        Thumbnail bytes or None if creation fails
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (for PNG with transparency, etc.)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Start with reasonable thumbnail size
            thumbnail_size = (400, 400)
            img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
            
            # Try different quality settings to get under size limit
            for quality in [85, 70, 55, 40, 25]:
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=quality, optimize=True)
                buffer_size_kb = len(buffer.getvalue()) / 1024
                
                if buffer_size_kb <= max_size_kb:
                    return buffer.getvalue()
            
            # If still too large, try smaller dimensions
            for size in [(300, 300), (200, 200), (150, 150)]:
                img_copy = img.copy()
                img_copy.thumbnail(size, Image.Resampling.LANCZOS)
                buffer = BytesIO()
                img_copy.save(buffer, format='JPEG', quality=40, optimize=True)
                buffer_size_kb = len(buffer.getvalue()) / 1024
                
                if buffer_size_kb <= max_size_kb:
                    return buffer.getvalue()
                    
            print(f"    ⚠️ Could not create thumbnail under {max_size_kb}KB for {image_path}")
            return None
            
    except Exception as e:
        print(f"    ⚠️ Thumbnail creation failed for {image_path}: {e}")
        return None


def compress_image_for_ipfs(image_path: pathlib.Path, max_size_mb: float = 2.0) -> Optional[bytes]:
    """
    Compress image to meet IPFS size requirements.
    
    Args:
        image_path: Path to source image
        max_size_mb: Maximum size in MB
        
    Returns:
        Compressed image bytes or None if compression fails
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            max_size_bytes = max_size_mb * 1024 * 1024
            
            # Try different compression strategies
            strategies = [
                # First try: reduce quality but keep size
                {'format': 'JPEG', 'quality': 85, 'optimize': True},
                {'format': 'JPEG', 'quality': 70, 'optimize': True},
                {'format': 'JPEG', 'quality': 55, 'optimize': True},
                
                # Then try: resize image dimensions
                {'format': 'JPEG', 'quality': 85, 'optimize': True, 'resize': (1200, 800)},
                {'format': 'JPEG', 'quality': 70, 'optimize': True, 'resize': (1000, 667)},
                {'format': 'JPEG', 'quality': 55, 'optimize': True, 'resize': (800, 533)},
            ]
            
            for strategy in strategies:
                img_copy = img.copy()
                
                # Apply resizing if specified
                if 'resize' in strategy:
                    img_copy.thumbnail(strategy['resize'], Image.Resampling.LANCZOS)
                
                buffer = BytesIO()
                img_copy.save(
                    buffer, 
                    format=strategy['format'],
                    quality=strategy['quality'],
                    optimize=strategy.get('optimize', False)
                )
                
                compressed_data = buffer.getvalue()
                size_mb = len(compressed_data) / (1024 * 1024)
                
                if len(compressed_data) <= max_size_bytes:
                    print(f"    ✅ Compressed {image_path.name}: {size_mb:.2f}MB (quality={strategy['quality']})")
                    return compressed_data
            
            print(f"    ⚠️ Could not compress {image_path.name} under {max_size_mb}MB")
            return None
            
    except Exception as e:
        print(f"    ⚠️ Image compression failed for {image_path}: {e}")
        return None


async def pin_image_to_ipfs_direct(image_path: pathlib.Path, run_id: str) -> Optional[str]:
    """
    Pin image file to IPFS using direct Pinata API (bypasses MCP server FormData issue).
    
    Args:
        image_path: Path to image file
        run_id: Run ID for logging
        
    Returns:
        IPFS CID or None if pinning fails
    """
    try:
        # Check if image needs compression
        size_mb = image_path.stat().st_size / (1024 * 1024)
        
        if size_mb <= 2.0:
            # Image is already under limit, use original file
            print(f"    📎 Using original image ({size_mb:.2f}MB)")
            file_data = None  # Will read from file directly
        else:
            # Image is too large, compress it
            print(f"    🗜️ Compressing large image ({size_mb:.1f}MB > 2MB)")
            file_data = compress_image_for_ipfs(image_path, max_size_mb=2.0)
            if not file_data:
                print(f"    ⚠️ Image compression failed: {image_path}")
                return None
        
        # Pin directly to Pinata API (workaround for MCP server FormData issue)
        pinata_jwt = os.getenv("PINATA_JWT")
        if not pinata_jwt:
            print(f"    ⚠️ PINATA_JWT not configured - falling back to MCP server")
            return await pin_image_to_ipfs_mcp(image_path, run_id, file_data)
        
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        headers = {"Authorization": f"Bearer {pinata_jwt}"}
        
        print(f"    📎 Pinning {image_path.name} directly to Pinata...")
        
        if file_data:
            # Use compressed data
            files = {"file": (image_path.name, BytesIO(file_data), "image/jpeg")}
            print(f"    📦 Uploading compressed data ({len(file_data)/1024:.0f}KB)")
            response = requests.post(url, files=files, headers=headers)
        else:
            # Use original file
            with open(image_path, 'rb') as f:
                files = {"file": (image_path.name, f, "image/png")}
                response = requests.post(url, files=files, headers=headers)
        
        if response.status_code != 200:
            print(f"    ⚠️ Pinata API error {response.status_code}: {response.text}")
            return None
        
        ipfs_hash = response.json()['IpfsHash']
        print(f"    ✅ Pinned directly to IPFS: ipfs://{ipfs_hash}")
        return ipfs_hash
        
    except Exception as e:
        print(f"    ⚠️ Direct IPFS pinning failed for {image_path}: {e}")
        # Fallback to MCP server attempt
        return await pin_image_to_ipfs_mcp(image_path, run_id, None)


async def pin_image_to_ipfs_mcp(image_path: pathlib.Path, run_id: str, compressed_data: Optional[bytes] = None) -> Optional[str]:
    """
    Pin image file to IPFS using MCP client (fallback method).
    
    Args:
        image_path: Path to image file  
        run_id: Run ID for logging
        compressed_data: Pre-compressed image data, or None to use file
        
    Returns:
        IPFS CID or None if pinning fails
    """
    try:
        if compressed_data:
            image_data = compressed_data
        else:
            with open(image_path, 'rb') as f:
                image_data = f.read()
        
        # Pin to IPFS via MCP
        mcp_client = get_mcp_client()
        print(f"    📎 Pinning {image_path.name} to IPFS via MCP ({len(image_data)/1024:.0f}KB)...")
        result = await mcp_client.pin_cid(image_data, content_type="image/jpeg")
        
        print(f"    ✅ Pinned to IPFS via MCP: ipfs://{result.cid}")
        return result.cid
        
    except Exception as e:
        print(f"    ⚠️ MCP IPFS pinning failed for {image_path}: {e}")
        return None


async def pin_thumbnail_to_ipfs_direct(thumbnail_data: bytes, filename: str, run_id: str) -> Optional[str]:
    """
    Pin thumbnail data to IPFS using direct Pinata API (preferred method).
    
    Args:
        thumbnail_data: Thumbnail image bytes
        filename: Original filename for logging
        run_id: Run ID for logging
        
    Returns:
        IPFS CID or None if pinning fails
    """
    try:
        # Validate thumbnail size
        size_kb = len(thumbnail_data) / 1024
        if size_kb > 200:
            print(f"    ⚠️ Thumbnail too large ({size_kb:.1f}KB > 200KB): {filename}")
            return None
        
        # Try direct Pinata API first
        pinata_jwt = os.getenv("PINATA_JWT")
        if pinata_jwt:
            url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
            headers = {"Authorization": f"Bearer {pinata_jwt}"}
            
            thumbnail_filename = f"thumb_{filename.replace('.png', '.jpg')}"
            files = {"file": (thumbnail_filename, BytesIO(thumbnail_data), "image/jpeg")}
            
            print(f"    📎 Pinning thumbnail {thumbnail_filename} directly to Pinata ({size_kb:.0f}KB)...")
            response = requests.post(url, files=files, headers=headers)
            
            if response.status_code == 200:
                ipfs_hash = response.json()['IpfsHash']
                print(f"    ✅ Thumbnail pinned directly to IPFS: ipfs://{ipfs_hash}")
                return ipfs_hash
            else:
                print(f"    ⚠️ Pinata thumbnail API error {response.status_code}: {response.text}")
        
        # Fallback to MCP server
        print(f"    🔄 Falling back to MCP server for thumbnail...")
        return await pin_thumbnail_to_ipfs_mcp(thumbnail_data, filename, run_id)
        
    except Exception as e:
        print(f"    ⚠️ Direct thumbnail IPFS pinning failed for {filename}: {e}")
        # Fallback to MCP server
        return await pin_thumbnail_to_ipfs_mcp(thumbnail_data, filename, run_id)


async def pin_thumbnail_to_ipfs_mcp(thumbnail_data: bytes, filename: str, run_id: str) -> Optional[str]:
    """
    Pin thumbnail data to IPFS using MCP client (fallback method).
    
    Args:
        thumbnail_data: Thumbnail image bytes
        filename: Original filename for logging
        run_id: Run ID for logging
        
    Returns:
        IPFS CID or None if pinning fails
    """
    try:
        # Pin to IPFS via MCP
        mcp_client = get_mcp_client()
        print(f"    📎 Pinning thumbnail {filename} to IPFS via MCP ({len(thumbnail_data)/1024:.0f}KB)...")
        result = await mcp_client.pin_cid(thumbnail_data, content_type="image/jpeg")
        
        print(f"    ✅ Thumbnail pinned to IPFS via MCP: ipfs://{result.cid}")
        return result.cid
        
    except Exception as e:
        print(f"    ⚠️ MCP thumbnail IPFS pinning failed for {filename}: {e}")
        return None


def pin_image_to_ipfs_sync(image_path: pathlib.Path, run_id: str) -> Optional[str]:
    """
    Pin image file to IPFS using synchronous requests (no asyncio).
    
    Args:
        image_path: Path to image file
        run_id: Run ID for logging
        
    Returns:
        IPFS CID or None if pinning fails
    """
    try:
        # Check if image needs compression
        size_mb = image_path.stat().st_size / (1024 * 1024)
        
        if size_mb <= 2.0:
            # Image is already under limit, use original file
            print(f"    📎 Using original image ({size_mb:.2f}MB)")
            with open(image_path, 'rb') as f:
                file_data = f.read()
            content_type = "image/png"
        else:
            # Image is too large, compress it
            print(f"    🗜️ Compressing large image ({size_mb:.1f}MB > 2MB)")
            file_data = compress_image_for_ipfs(image_path, max_size_mb=2.0)
            if not file_data:
                print(f"    ⚠️ Image compression failed: {image_path}")
                return None
            content_type = "image/jpeg"
        
        # Try direct Pinata API first
        pinata_jwt = os.getenv("PINATA_JWT")
        if pinata_jwt:
            url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
            headers = {"Authorization": f"Bearer {pinata_jwt}"}
            files = {"file": (image_path.name, file_data, content_type)}
            
            print(f"    📎 Pinning {image_path.name} directly to Pinata ({len(file_data)/1024:.0f}KB)...")
            response = requests.post(url, files=files, headers=headers, timeout=30)
            
            if response.status_code == 200:
                ipfs_hash = response.json()['IpfsHash']
                print(f"    ✅ Pinned directly to IPFS: ipfs://{ipfs_hash}")
                return ipfs_hash
            else:
                print(f"    ⚠️ Pinata API error {response.status_code}: {response.text}")
        
        # Fallback: return None for now (MCP server sync would need more work)
        print(f"    ⚠️ No PINATA_JWT configured, skipping IPFS pinning")
        return None
        
    except Exception as e:
        print(f"    ⚠️ Sync IPFS pinning failed for {image_path}: {e}")
        return None


def pin_thumbnail_to_ipfs_sync(thumbnail_data: bytes, filename: str, run_id: str) -> Optional[str]:
    """
    Pin thumbnail data to IPFS using synchronous requests (no asyncio).
    
    Args:
        thumbnail_data: Thumbnail image bytes
        filename: Original filename for logging
        run_id: Run ID for logging
        
    Returns:
        IPFS CID or None if pinning fails
    """
    try:
        # Validate thumbnail size
        size_kb = len(thumbnail_data) / 1024
        if size_kb > 200:
            print(f"    ⚠️ Thumbnail too large ({size_kb:.1f}KB > 200KB): {filename}")
            return None
        
        # Try direct Pinata API first
        pinata_jwt = os.getenv("PINATA_JWT")
        if pinata_jwt:
            url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
            headers = {"Authorization": f"Bearer {pinata_jwt}"}
            
            thumbnail_filename = f"thumb_{filename.replace('.png', '.jpg')}"
            files = {"file": (thumbnail_filename, BytesIO(thumbnail_data), "image/jpeg")}
            
            print(f"    📎 Pinning thumbnail {thumbnail_filename} directly to Pinata ({size_kb:.0f}KB)...")
            response = requests.post(url, files=files, headers=headers, timeout=30)
            
            if response.status_code == 200:
                ipfs_hash = response.json()['IpfsHash']
                print(f"    ✅ Thumbnail pinned directly to IPFS: ipfs://{ipfs_hash}")
                return ipfs_hash
            else:
                print(f"    ⚠️ Pinata thumbnail API error {response.status_code}: {response.text}")
        
        # Fallback: return None for now
        print(f"    ⚠️ No PINATA_JWT configured, skipping thumbnail IPFS pinning")
        return None
        
    except Exception as e:
        print(f"    ⚠️ Sync thumbnail IPFS pinning failed for {filename}: {e}")
        return None


def generate_image_openai_real(prompt: str, filename: str, size: str = "1536x1024") -> str:
    """Generate image using OpenAI gpt-image-1 model."""
    oa = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    print(f"    🎨 Calling OpenAI Image Generation... ({time.strftime('%H:%M:%S')})")
    start_time = time.time()
    
    try:
        r = oa.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size=size,
            n=1,
            timeout=180
        )
        elapsed = time.time() - start_time
        print(f"    ✅ OpenAI image generated in {elapsed:.1f}s")
        
        b64 = r.data[0].b64_json
        filepath = pathlib.Path(filename)
        write_b64_image(path=filepath, b64=b64)
        
        return str(filepath.absolute())
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"    ⚠️ OpenAI generation failed after {elapsed:.1f}s: {e}")
        raise


def generate_image_openai(prompt: str, filename: str, size: str = "1536x1024") -> str:
    """🎭 MOCK: Generate a fake image for testing without OpenAI API calls."""
    from PIL import Image, ImageDraw, ImageFont
    import hashlib
    
    print(f"    🎭 MOCK: Creating test image... ({time.strftime('%H:%M:%S')})")
    start_time = time.time()
    
    try:
        # Parse size (e.g., "1536x1024")
        width, height = map(int, size.split('x'))
        
        # Create a colorful gradient based on prompt hash
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        color_r = int(prompt_hash[:2], 16)
        color_g = int(prompt_hash[2:4], 16) 
        color_b = int(prompt_hash[4:6], 16)
        
        # Create gradient image
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        # Create a gradient background
        for y in range(height):
            intensity = y / height
            r = int(color_r * (1 - intensity) + 255 * intensity)
            g = int(color_g * (1 - intensity) + 255 * intensity)
            b = int(color_b * (1 - intensity) + 255 * intensity)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add some geometric shapes for visual interest
        draw.ellipse([width//4, height//4, 3*width//4, 3*height//4], 
                    outline=(255-color_r, 255-color_g, 255-color_b), width=8)
        draw.rectangle([width//8, height//8, width//2, height//2], 
                      outline=(color_b, color_r, color_g), width=4)
        
        # Add text overlay
        try:
            # Try to use a default font, fallback to built-in if not available
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 40)
        except:
            font = ImageFont.load_default()
            
        text = "MOCK IMAGE"
        prompt_preview = prompt[:30] + "..." if len(prompt) > 30 else prompt
        
        # Add text with background
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        text_x = (width - text_width) // 2
        text_y = height // 2 - 60
        
        # Background rectangle for text
        draw.rectangle([text_x - 10, text_y - 10, text_x + text_width + 10, text_y + text_height + 10], 
                      fill=(0, 0, 0, 128))
        draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)
        
        # Add prompt preview
        draw.text((width//20, height - 100), f"Prompt: {prompt_preview}", 
                 fill=(255, 255, 255), font=font)
        
        # Save image
        filepath = pathlib.Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        image.save(filepath, 'PNG', quality=95)
        
        elapsed = time.time() - start_time
        print(f"    ✅ Mock image generated in {elapsed:.3f}s")
        
        return str(filepath.absolute())
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"    ⚠️ Mock generation failed after {elapsed:.1f}s: {e}")
        raise


def create_image_prompts(prompt_seed: Dict[str, Any], date_label: str) -> List[str]:
    """Create varied image prompts based on the prompt_seed motifs."""
    style = prompt_seed.get("style", "historical, documentary")
    palette = prompt_seed.get("palette", "warm, classic colors")
    motifs = prompt_seed.get("motifs", ["vintage elements", "historical artifacts", "timeless designs", "classical composition"])
    negative = prompt_seed.get("negative", "modern, futuristic")
    
    # Create prompts based on the number of motifs provided
    base_prompt = f"Historical artwork depicting {date_label}, {style}, {palette}"
    
    prompts = []
    for i, motif in enumerate(motifs):
        variation_words = ["featuring", "with", "incorporating", "showcasing"]
        avoid_words = ["avoid", "not", "without", "no"]
        
        variation_word = variation_words[i % len(variation_words)]
        avoid_word = avoid_words[i % len(avoid_words)]
        
        prompt = f"{base_prompt}, {variation_word} {motif}, {avoid_word} {negative}"
        prompts.append(prompt)
    
    # Ensure we have at least one prompt even if no motifs provided
    if not prompts:
        prompts = [f"{base_prompt}, featuring historical elements, avoid {negative}"]
    
    return prompts


def artist_agent(state: RunState) -> Dict[str, Any]:
    """
    Artist Agent: Generate art based on LorePack using OpenAI gpt-image-1 with IPFS integration
    
    Input: LorePack with prompt_seed
    Output: ArtSet with IPFS CIDs for images and thumbnails
    
    Process:
    1. Generate images using OpenAI gpt-image-1
    2. Create thumbnails with PIL/Pillow (<200KB)
    3. Pin images and thumbnails to IPFS via MCP
    4. Return ArtSet with ipfs:// CIDs
    """
    run_id = state.get("run_id", "unknown")
    date_label = state.get("date_label", "Unknown Event")
    lore = state.get("lore")
    
    # Collect all messages to return to workflow (initialize early)
    all_messages = []
    
    if not lore:
        error_message = {
            "agent": "Artist",
            "level": "error", 
            "message": "Missing lore data",
            "ts": str(uuid.uuid4())
        }
        all_messages.append(error_message)
        return {
            "error": "No lore data available for art generation",
            "messages": all_messages
        }
    
    # Small delay to allow SSE polling to detect intermediate state changes
    time.sleep(0.05)  # 50ms delay for real-time streaming
    
    prompt_seed = lore.get("prompt_seed", {})
    print(f"🎨 ARTIST: Starting image generation for {run_id} - {date_label}")
    print(f"🎨 ARTIST: Using prompt_seed: {prompt_seed}")
    
    # Emit initial Artist message
    start_message = {
        "agent": "Artist",
        "level": "info",
        "message": f"🎨 Artist agent activated - preparing to generate artworks for {date_label}",
        "ts": str(uuid.uuid4())
    }
    all_messages.append(start_message)
    print(f"🎨 ARTIST: Created start message")
    
    # Emit start message immediately to simple_state for real-time SSE streaming
    if run_id:
        import simple_state
        current_state = simple_state.get_run_state(run_id) or {}
        current_messages = current_state.get("messages", [])
        current_messages.append(start_message)
        simple_state.update_run_state(run_id, {"messages": current_messages})
        print(f"🎨 ARTIST: Added start message to state, total messages: {len(current_messages)}")
    
    # Create temp directory for generated images
    temp_dir = pathlib.Path("temp_images") / run_id
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Generate image prompts based on lore pack
        prompts = create_image_prompts(prompt_seed, date_label)
        print(f"🎨 ARTIST: Generated {len(prompts)} image prompts")
        
        # Generate images using OpenAI gpt-image-1 with IPFS integration
        generated_cids = []
        thumbnail_cids = []
        style_notes = []
        
        # Temporary: Only generate one image for faster testing
        for i, prompt in enumerate(prompts[:1]):
            filename = temp_dir / f"art_{i+1}.png"
            print(f"🎨 ARTIST: Generating image {i+1}/4: {prompt[:100]}...")
            
            # Create progress message
            progress_message = {
                "agent": "Artist",
                "level": "info", 
                "message": f"Generating image {i+1}/{len(prompts)} using OpenAI gpt-image-1...",
                "ts": str(uuid.uuid4())
            }
            all_messages.append(progress_message)
            print(f"🎨 ARTIST: Added progress message {i+1}/{len(prompts)}")
            
            # Emit progress message immediately to simple_state for real-time SSE streaming
            if run_id:
                current_state = simple_state.get_run_state(run_id) or {}
                current_messages = current_state.get("messages", [])
                current_messages.append(progress_message)
                simple_state.update_run_state(run_id, {"messages": current_messages})
                print(f"🎨 ARTIST: Added progress message {i+1}/{len(prompts)} to state, total messages: {len(current_messages)}")
            
            try:
                # Generate image
                filepath = generate_image_openai(prompt, str(filename))
                filepath_obj = pathlib.Path(filepath)
                
                # Validate image was created successfully
                if not filepath_obj.exists():
                    raise Exception(f"Image file not created: {filepath}")
                
                # Create thumbnail
                thumbnail_data = create_thumbnail(filepath_obj, max_size_kb=200.0)
                if not thumbnail_data:
                    raise Exception("Thumbnail creation failed")
                
                # Pin image to IPFS (using synchronous Pinata API)
                image_cid = pin_image_to_ipfs_sync(filepath_obj, run_id)
                if not image_cid:
                    raise Exception("Image IPFS pinning failed")
                
                # Pin thumbnail to IPFS (using synchronous Pinata API)
                thumbnail_cid = pin_thumbnail_to_ipfs_sync(thumbnail_data, f"art_{i+1}.png", run_id)
                if not thumbnail_cid:
                    raise Exception("Thumbnail IPFS pinning failed")
                
                # Store IPFS CIDs
                generated_cids.append(f"ipfs://{image_cid}")
                thumbnail_cids.append(f"ipfs://{thumbnail_cid}")
                
                # Create style note based on the prompt variation
                motifs = prompt_seed.get("motifs", ["historical elements"])
                motif = motifs[i] if i < len(motifs) else f"variation {i+1}"
                style_notes.append(f"Historical artwork featuring {motif} in {prompt_seed.get('style', 'classic')} style")
                
                # Create completion message
                completion_message = {
                    "agent": "Artist",
                    "level": "success",
                    "message": f"Image {i+1}/{len(prompts)} generated and pinned to IPFS ({os.path.getsize(filepath)/1024/1024:.1f}MB → ipfs://{image_cid})",
                    "ts": str(uuid.uuid4())
                }
                all_messages.append(completion_message)
                print(f"🎨 ARTIST: Added completion message {i+1}/{len(prompts)}")
                
                # Emit completion message immediately to simple_state for real-time SSE streaming
                if run_id:
                    current_state = simple_state.get_run_state(run_id) or {}
                    current_messages = current_state.get("messages", [])
                    current_messages.append(completion_message)
                    simple_state.update_run_state(run_id, {"messages": current_messages})
                    print(f"🎨 ARTIST: Added completion message {i+1}/{len(prompts)} to state, total messages: {len(current_messages)}")
                
            except Exception as e:
                print(f"🎨 ARTIST: Failed to generate or pin image {i+1}: {e}")
                # Use placeholder CIDs for failed generation
                generated_cids.append(f"ipfs://placeholder_art_{i+1}")
                thumbnail_cids.append(f"ipfs://placeholder_thumb_{i+1}")
                style_notes.append(f"Image generation or IPFS pinning failed for variation {i+1}")
                
                # Create error message
                error_message = {
                    "agent": "Artist",
                    "level": "warning",
                    "message": f"Image {i+1}/{len(prompts)} generation/pinning failed: {str(e)[:50]}",
                    "ts": str(uuid.uuid4())
                }
                all_messages.append(error_message)
                print(f"🎨 ARTIST: Added error message {i+1}/{len(prompts)}")
                
                # Emit error message immediately to simple_state for real-time SSE streaming
                if run_id:
                    current_state = simple_state.get_run_state(run_id) or {}
                    current_messages = current_state.get("messages", [])
                    current_messages.append(error_message)
                    simple_state.update_run_state(run_id, {"messages": current_messages})
                    print(f"🎨 ARTIST: Added error message {i+1}/{len(prompts)} to state, total messages: {len(current_messages)}")
        
        # Create art set with IPFS CIDs
        art_set = {
            "cids": generated_cids,  # Now using ipfs:// CIDs
            "thumbnails": thumbnail_cids,  # Real thumbnail CIDs from IPFS
            "style_notes": style_notes
        }
        
        # Count successful generations
        successful_gens = len([cid for cid in generated_cids if not cid.startswith("ipfs://placeholder")])
        
        # Final summary message
        final_message = {
            "agent": "Artist",
            "level": "success",
            "message": f"🎨 All images complete! Generated {successful_gens}/{len(prompts)} artworks ready for voting",
            "ts": str(uuid.uuid4()),
            "links": [
                {"label": f"Art #{i+1}", "href": cid} 
                for i, cid in enumerate(generated_cids)
            ]
        }
        all_messages.append(final_message)
        
        # Emit final message immediately to simple_state for real-time SSE streaming
        if run_id:
            current_state = simple_state.get_run_state(run_id) or {}
            current_messages = current_state.get("messages", [])
            current_messages.append(final_message)
            
            # Update state with final message and art set
            simple_state.update_run_state(run_id, {
                "messages": current_messages,
                "art": art_set  # Include the art set in the state update
            })
            print(f"🎨 ARTIST: Added final message to state, total messages: {len(current_messages)}")
        
        print(f"🎨 ARTIST: Successfully generated {successful_gens}/{len(prompts)} images")
        
    except Exception as e:
        print(f"🎨 ARTIST: Image generation completely failed: {e}")
        
        # Fallback to placeholder art set  
        art_set = {
            "cids": [
                "ipfs://fallback_placeholder_1",
                "ipfs://fallback_placeholder_2", 
                "ipfs://fallback_placeholder_3",
                "ipfs://fallback_placeholder_4"
            ],
            "thumbnails": [
                "ipfs://fallback_thumb_1",
                "ipfs://fallback_thumb_2",
                "ipfs://fallback_thumb_3",
                "ipfs://fallback_thumb_4"
            ],
            "style_notes": [
                "Image generation failed - using fallback placeholder",
                "Image generation failed - using fallback placeholder",
                "Image generation failed - using fallback placeholder", 
                "Image generation failed - using fallback placeholder"
            ]
        }
        
        error_message = {
            "agent": "Artist",
            "level": "warning",
            "message": f"Image generation failed, using fallback placeholders: {str(e)[:100]}",
            "ts": str(uuid.uuid4()),
            "links": []
        }
        all_messages.append(error_message)
        
        # Emit fallback error message immediately to simple_state for real-time SSE streaming
        if run_id:
            current_state = simple_state.get_run_state(run_id) or {}
            current_messages = current_state.get("messages", [])
            current_messages.append(error_message)
            
            # Update state with error message and fallback art set
            simple_state.update_run_state(run_id, {
                "messages": current_messages,
                "art": art_set  # Include the fallback art set in the state update
            })
            print(f"🎨 ARTIST: Added fallback error message to state, total messages: {len(current_messages)}")
    
    result = {
        "art": art_set,
        "messages": all_messages  # Return ALL collected messages to workflow
    }
    print(f"🎨 ARTIST: Returning {len(result['messages'])} messages: {[msg['agent'] for msg in result['messages']]}")
    return result
