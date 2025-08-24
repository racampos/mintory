"""
Artist Agent - Image generation using OpenAI gpt-image-1 and local storage
"""
import os
import time
import uuid
import base64
import pathlib
from typing import Dict, Any, List
from openai import OpenAI
from state import RunState, ArtSet


def write_b64_image(path: pathlib.Path, b64: str) -> None:
    """Write base64 image data to file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as f:
        f.write(base64.b64decode(b64))


def generate_image_openai(prompt: str, filename: str, size: str = "1536x1024") -> str:
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


def create_image_prompts(prompt_seed: Dict[str, Any], date_label: str) -> List[str]:
    """Create varied image prompts based on the prompt_seed."""
    style = prompt_seed.get("style", "historical, documentary")
    palette = prompt_seed.get("palette", "warm, classic colors")
    motifs = prompt_seed.get("motifs", ["vintage elements", "historical artifacts"])
    negative = prompt_seed.get("negative", "modern, futuristic")
    
    # Create 4 varied prompts based on the prompt_seed
    base_prompt = f"Historical artwork depicting {date_label}, {style}, {palette}"
    
    prompts = [
        f"{base_prompt}, featuring {motifs[0] if motifs else 'historical elements'}, avoid {negative}",
        f"{base_prompt}, with {motifs[1] if len(motifs) > 1 else 'traditional patterns'}, not {negative}",
        f"{base_prompt}, incorporating {motifs[2] if len(motifs) > 2 else 'timeless designs'}, without {negative}",
        f"{base_prompt}, showcasing {motifs[3] if len(motifs) > 3 else 'classical composition'}, no {negative}"
    ]
    
    return prompts


def artist_agent(state: RunState) -> Dict[str, Any]:
    """
    Artist Agent: Generate art based on LorePack using OpenAI gpt-image-1
    
    Input: LorePack with prompt_seed
    Output: ArtSet with local file paths (temp storage before IPFS)
    """
    run_id = state.get("run_id", "unknown")
    date_label = state.get("date_label", "Unknown Event")
    lore = state.get("lore")
    
    if not lore:
        return {
            "error": "No lore data available for art generation",
            "messages": [{
                "agent": "Artist",
                "level": "error", 
                "message": "Missing lore data",
                "ts": str(uuid.uuid4())
            }]
        }
    
    # Small delay to allow SSE polling to detect intermediate state changes
    time.sleep(0.05)  # 50ms delay for real-time streaming
    
    prompt_seed = lore.get("prompt_seed", {})
    print(f"🎨 ARTIST: Starting image generation for {run_id} - {date_label}")
    print(f"🎨 ARTIST: Using prompt_seed: {prompt_seed}")
    
    # Emit initial Artist message by adding to existing messages
    start_message = {
        "agent": "Artist",
        "level": "info",
        "message": f"🎨 Artist agent activated - preparing to generate 4 artworks for {date_label}",
        "ts": str(uuid.uuid4())
    }
    
    # Add start message to existing state (not replacing)
    if run_id:
        import simple_state
        current_state = simple_state.get_run_state(run_id) or {}
        current_messages = current_state.get("messages", [])
        current_messages.append(start_message)
        simple_state.update_run_state(run_id, {"messages": current_messages})
        print(f"🎨 ARTIST: Added start message, total messages: {len(current_messages)}")
    
    # Create temp directory for generated images
    temp_dir = pathlib.Path("temp_images") / run_id
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Generate image prompts based on lore pack
        prompts = create_image_prompts(prompt_seed, date_label)
        print(f"🎨 ARTIST: Generated {len(prompts)} image prompts")
        
        # Generate images using OpenAI gpt-image-1
        generated_files = []
        style_notes = []
        
        for i, prompt in enumerate(prompts):
            filename = temp_dir / f"art_{i+1}.png"
            print(f"🎨 ARTIST: Generating image {i+1}/4: {prompt[:100]}...")
            
            # Create and emit progress message individually
            progress_message = {
                "agent": "Artist",
                "level": "info", 
                "message": f"Generating image {i+1}/4 using OpenAI gpt-image-1...",
                "ts": str(uuid.uuid4())
            }
            
            # Emit progress by adding to existing state (not replacing)
            if run_id:
                import simple_state
                current_state = simple_state.get_run_state(run_id) or {}
                current_messages = current_state.get("messages", [])
                current_messages.append(progress_message)
                simple_state.update_run_state(run_id, {"messages": current_messages})
                print(f"🎨 ARTIST: Added progress message {i+1}/4, total messages: {len(current_messages)}")
            
            try:
                filepath = generate_image_openai(prompt, str(filename))
                generated_files.append(f"file://{filepath}")
                
                # Create style note based on the prompt variation
                motifs = prompt_seed.get("motifs", ["historical elements"])
                motif = motifs[i] if i < len(motifs) else f"variation {i+1}"
                style_notes.append(f"Historical artwork featuring {motif} in {prompt_seed.get('style', 'classic')} style")
                
                # Create and emit completion message individually
                completion_message = {
                    "agent": "Artist",
                    "level": "success",
                    "message": f"Image {i+1}/4 generated successfully ({os.path.getsize(filepath)/1024/1024:.1f}MB)",
                    "ts": str(uuid.uuid4())
                }
                
                # Emit completion by adding to existing state (not replacing)
                if run_id:
                    current_state = simple_state.get_run_state(run_id) or {}
                    current_messages = current_state.get("messages", [])
                    current_messages.append(completion_message)
                    simple_state.update_run_state(run_id, {"messages": current_messages})
                    print(f"🎨 ARTIST: Added completion message {i+1}/4, total messages: {len(current_messages)}")
                
            except Exception as e:
                print(f"🎨 ARTIST: Failed to generate image {i+1}: {e}")
                # Use a placeholder for failed generation
                generated_files.append(f"file://placeholder_art_{i+1}.png")
                style_notes.append(f"Image generation failed for variation {i+1}")
                
                # Create and emit error message individually
                error_message = {
                    "agent": "Artist",
                    "level": "warning",
                    "message": f"Image {i+1}/4 generation failed: {str(e)[:50]}",
                    "ts": str(uuid.uuid4())
                }
                
                # Emit error by adding to existing state (not replacing)
                if run_id:
                    current_state = simple_state.get_run_state(run_id) or {}
                    current_messages = current_state.get("messages", [])
                    current_messages.append(error_message)
                    simple_state.update_run_state(run_id, {"messages": current_messages})
                    print(f"🎨 ARTIST: Added error message {i+1}/4, total messages: {len(current_messages)}")
        
        # Create art set with generated files
        art_set = {
            "cids": generated_files,  # Using file:// paths instead of ipfs:// for now
            "thumbnails": [
                # TODO: Generate real thumbnails in Phase 5.4
                "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjNjY2Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNiIgZmlsbD0iI2ZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkFydCAjMTwvdGV4dD48L3N2Zz4=",
                "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjNDQ0Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNiIgZmlsbD0iI2ZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkFydCAjMjwvdGV4dD48L3N2Zz4=",
                "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMjIyIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNiIgZmlsbD0iI2ZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkFydCAjMzwvdGV4dD48L3N2Zz4=",
                "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMDAwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNiIgZmlsbD0iI2ZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkFydCAjNDwvdGV4dD48L3N2Zz4="
            ],
            "style_notes": style_notes
        }
        
        # Count successful generations
        successful_gens = len([f for f in generated_files if not f.startswith("file://placeholder")])
        
        # Final summary message
        final_message = {
            "agent": "Artist",
            "level": "success",
            "message": f"🎨 All images complete! Generated {successful_gens}/{len(prompts)} artworks ready for voting",
            "ts": str(uuid.uuid4()),
            "links": [
                {"label": f"Art #{i+1}", "href": filepath} 
                for i, filepath in enumerate(generated_files)
            ]
        }
        
        # Add final message and art set to existing state (not replacing)
        if run_id:
            current_state = simple_state.get_run_state(run_id) or {}
            current_messages = current_state.get("messages", [])
            current_messages.append(final_message)
            
            # Update state with final message and art set
            simple_state.update_run_state(run_id, {
                "messages": current_messages,
                "art": art_set  # Include the art set in the state update
            })
            print(f"🎨 ARTIST: Added final message + art set, total messages: {len(current_messages)}")
        
        # For backward compatibility, still return the final message
        message = final_message
        
        print(f"🎨 ARTIST: Successfully generated {successful_gens}/{len(prompts)} images")
        
    except Exception as e:
        print(f"🎨 ARTIST: Image generation completely failed: {e}")
        
        # Fallback to placeholder art set
        art_set = {
            "cids": [
                "file://fallback_placeholder_1.png",
                "file://fallback_placeholder_2.png", 
                "file://fallback_placeholder_3.png",
                "file://fallback_placeholder_4.png"
            ],
            "thumbnails": [
                "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjNjY2Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNiIgZmlsbD0iI2ZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkFydCAjMTwvdGV4dD48L3N2Zz4=",
                "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjNDQ0Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNiIgZmlsbD0iI2ZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkFydCAjMjwvdGV4dD48L3N2Zz4=",
                "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMjIyIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNiIgZmlsbD0iI2ZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkFydCAjMzwvdGV4dD48L3N2Zz4=",
                "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMDAwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNiIgZmlsbD0iI2ZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkZhbGxiYWNrIDwvdGV4dD48L3N2Zz4="
            ],
            "style_notes": [
                "Image generation failed - using fallback placeholder",
                "Image generation failed - using fallback placeholder",
                "Image generation failed - using fallback placeholder", 
                "Image generation failed - using fallback placeholder"
            ]
        }
        
        message = {
            "agent": "Artist",
            "level": "warning",
            "message": f"Image generation failed, using fallback placeholders: {str(e)[:100]}",
            "ts": str(uuid.uuid4()),
            "links": []
        }
    
    result = {
        "art": art_set,
        "messages": [message]
    }
    print(f"🎨 ARTIST: Returning {len(result['messages'])} messages: {[msg['agent'] for msg in result['messages']]}")
    return result
