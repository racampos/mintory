"""
Lore Agent - Research and context generation using real LLM integration
"""
import uuid
import logging
from typing import Dict, Any
from state import RunState, LorePack
from services import get_llm_client

logger = logging.getLogger(__name__)


def validate_lore_pack(lore_pack_dict: Dict[str, Any], date_label: str) -> None:
    """
    Validate LorePack meets agents_spec.md requirements
    
    Args:
        lore_pack_dict: Dictionary representation of LorePack
        date_label: Original date for error context
        
    Raises:
        ValueError: If validation fails
    """
    # Check summary_md word count (≤200 words)
    summary = lore_pack_dict.get("summary_md", "")
    if not summary:
        raise ValueError(f"summary_md is empty for date: {date_label}")
    
    word_count = len(summary.split())
    if word_count > 200:
        raise ValueError(f"summary_md has {word_count} words, must be ≤200 for date: {date_label}")
    
    # Check bullet_facts count (5-10)
    bullet_facts = lore_pack_dict.get("bullet_facts", [])
    if len(bullet_facts) < 5:
        raise ValueError(f"bullet_facts has {len(bullet_facts)} items, must be ≥5 for date: {date_label}")
    if len(bullet_facts) > 10:
        raise ValueError(f"bullet_facts has {len(bullet_facts)} items, must be ≤10 for date: {date_label}")
    
    # Check sources count (≥5)
    sources = lore_pack_dict.get("sources", [])
    if len(sources) < 5:
        raise ValueError(f"sources has {len(sources)} items, must be ≥5 for date: {date_label}")
    
    # Check all sources are HTTP(S) URLs
    for i, source in enumerate(sources):
        if not source.startswith(("http://", "https://")):
            raise ValueError(f"sources[{i}] '{source}' must be HTTP/HTTPS URL for date: {date_label}")
    
    # Check prompt_seed has required fields
    prompt_seed = lore_pack_dict.get("prompt_seed", {})
    if not prompt_seed.get("style"):
        raise ValueError(f"prompt_seed.style is empty for date: {date_label}")
    if not prompt_seed.get("palette"):
        raise ValueError(f"prompt_seed.palette is empty for date: {date_label}")


async def lore_agent(state: RunState) -> Dict[str, Any]:
    """
    Lore Agent: Generate historical context and research summary using real LLM
    
    Input: date_label
    Output: LorePack with summary, facts, sources, prompt_seed
    
    Uses OpenAI/LLM to research the historical date and generate:
    - summary_md: ≤200 words of historical context
    - bullet_facts: 5-10 key historical points  
    - sources: ≥5 HTTP/HTTPS URLs for reference
    - prompt_seed: Art generation guidance (style, palette, motifs, negative)
    """
    date_label = state["date_label"]
    run_id = state.get("run_id")
    
    # Check if this is a regeneration with user feedback
    edit_instructions = state.get("edit_instructions")
    is_regenerating = state.get("regenerating", False)
    
    # Create progress message for LLM research and emit it immediately
    if is_regenerating and edit_instructions:
        research_message = {
            "agent": "Lore",
            "level": "info", 
            "message": f"Regenerating lore for {date_label} based on your feedback...",
            "ts": str(uuid.uuid4())
        }
    else:
        research_message = {
            "agent": "Lore",
            "level": "info", 
            "message": f"Researching historical significance of {date_label}...",
            "ts": str(uuid.uuid4())
        }
    
    # Emit the "researching" message immediately for real-time UX
    print(f"🧠 LORE: Starting research for {run_id} - {date_label}")
    if run_id:
        import simple_state
        current_state = simple_state.get_run_state(run_id) or {}
        current_messages = current_state.get("messages", [])
        current_messages.append(research_message)
        simple_state.update_run_state(run_id, {"messages": current_messages})
        print(f"🧠 LORE: Immediately emitted research message, state now has {len(current_messages)} messages")
    
    try:
        # Get LLM client and generate real historical research
        llm_client = get_llm_client()
        logger.info(f"Starting LLM research for date: {date_label}")
        
        # Use the specialized generate_lore_pack method with optional edit instructions
        lore_pack_model, llm_response = await llm_client.generate_lore_pack(date_label, edit_instructions)
        
        # Convert Pydantic model to dict for state compatibility
        lore_pack_dict = lore_pack_model.model_dump()
        
        # Validate the generated content meets spec requirements
        validate_lore_pack(lore_pack_dict, date_label)
        
        logger.info(f"LLM research completed for {date_label}: {llm_response.usage['total_tokens']} tokens used")
        
        # Create success message with source links
        if is_regenerating and edit_instructions:
            success_message = {
                "agent": "Lore", 
                "level": "success",
                "message": f"Regenerated historical research for {date_label} based on your feedback ({len(lore_pack_dict['summary_md'].split())} words, {len(lore_pack_dict['bullet_facts'])} facts, {len(lore_pack_dict['sources'])} sources)",
                "ts": str(uuid.uuid4()),
                "links": [
                    {"label": f"Source {i+1}", "href": url} 
                    for i, url in enumerate(lore_pack_dict["sources"][:3])
                ]
            }
        else:
            success_message = {
                "agent": "Lore", 
                "level": "success",
                "message": f"Generated historical research for {date_label} ({len(lore_pack_dict['summary_md'].split())} words, {len(lore_pack_dict['bullet_facts'])} facts, {len(lore_pack_dict['sources'])} sources)",
                "ts": str(uuid.uuid4()),
                "links": [
                    {"label": f"Source {i+1}", "href": url} 
                    for i, url in enumerate(lore_pack_dict["sources"][:3])
                ]
            }
        
        print(f"🧠 LORE: Research completed for {run_id} - {len(lore_pack_dict['summary_md'].split())} words")
        
        # Create a formatted lore content message for user review
        lore_content_message = {
            "agent": "Lore",
            "level": "info",
            "message": f"""📜 Generated Lore for {date_label}

{lore_pack_dict['summary_md']}

🔑 Key Facts:
{chr(10).join(f"• {fact}" for fact in lore_pack_dict['bullet_facts'])}

🎨 Art Generation Style:
• Style: {lore_pack_dict['prompt_seed']['style']}
• Palette: {lore_pack_dict['prompt_seed']['palette']}  
• Motifs: {', '.join(lore_pack_dict['prompt_seed']['motifs'])}""",
            "ts": str(uuid.uuid4())
        }
        
        # Only return the success message since research message was already emitted immediately
        result = {
            "lore": lore_pack_dict,
            "messages": [success_message, lore_content_message]  # Show completion + content
        }
        
        # Only set checkpoint if this is initial generation, not regeneration
        if not is_regenerating:
            result["checkpoint"] = "lore_approval"
        print(f"🧠 LORE: Returning {len(result['messages'])} messages: {[msg['agent'] for msg in result['messages']]}")
        return result
        
    except Exception as e:
        logger.error(f"Lore agent failed for date {date_label}: {e}")
        
        # Create fallback lore pack for demo reliability
        fallback_lore_pack = {
            "summary_md": f"""
# {date_label}

This historical date represents an important moment in time. While our research systems encountered an issue, {date_label} likely marks significant developments in technology, culture, or society. Historical events on this date may have influenced digital innovation, community development, or technological progress.

The significance of this date extends to broader themes of human progress, technological advancement, and social change that continue to shape our modern world.
            """.strip(),
            
            "bullet_facts": [
                f"Historical date: {date_label}",
                "Significant moment in historical timeline",
                "Potential technological or cultural milestone",
                "Impact on societal development",
                "Foundation for future innovations",
                "Influence on modern digital culture"
            ],
            
            "sources": [
                "https://en.wikipedia.org/wiki/Timeline_of_computing",
                "https://www.britannica.com/technology/history-of-technology", 
                "https://www.computerhistory.org/timeline/",
                "https://timeline.web.cern.ch/",
                "https://www.historyoftechnology.org/"
            ],
            
            "prompt_seed": {
                "style": "historical, documentary, classical art style",
                "palette": "warm browns, gold, sepia tones, classic colors",
                "motifs": ["vintage elements", "historical artifacts", "traditional patterns", "timeless designs"],
                "negative": "modern, futuristic, digital"
            }
        }
        
        # Validate fallback meets requirements
        validate_lore_pack(fallback_lore_pack, date_label)
        
        error_message = {
            "agent": "Lore",
            "level": "warning",
            "message": f"Research error for {date_label}, using fallback content: {str(e)[:100]}...",
            "ts": str(uuid.uuid4()),
            "links": [{"label": f"Source {i+1}", "href": url} for i, url in enumerate(fallback_lore_pack["sources"][:3])]
        }
        
        print(f"🧠 LORE: Using fallback content for {run_id} due to error")
        
        # Only return the error message since research message was already emitted immediately above
        return {
            "lore": fallback_lore_pack, 

            "messages": [error_message]  # research_message already emitted above
        }
