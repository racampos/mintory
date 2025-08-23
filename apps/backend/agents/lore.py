"""
Lore Agent - Research and context generation
"""
import uuid
from typing import Dict, Any
from state import RunState, LorePack


def lore_agent(state: RunState) -> Dict[str, Any]:
    """
    Lore Agent: Generate historical context and research summary
    
    Input: date_label
    Output: LorePack with summary, facts, sources, prompt_seed
    """
    date_label = state["date_label"]
    
    # For hackathon demo - create a reasonable lore pack
    # In production, this would call LLM APIs for research
    
    lore_pack = {
        "summary_md": f"""
# {date_label}

This historical moment represents a pivotal point in technological and social history. 
The date marks significant developments that shaped our understanding of decentralized systems, 
digital innovation, and community-driven progress. Key stakeholders and technologies converged 
to create lasting impact on how we interact with digital assets and blockchain technology.

The historical significance extends beyond immediate technical achievements to encompass 
broader implications for digital sovereignty, community governance, and decentralized finance.
        """.strip(),
        
        "bullet_facts": [
            f"Historical date: {date_label}",
            "Significant technological milestone achieved",
            "Community-driven development model established",
            "Open-source principles emphasized",
            "Decentralized governance concepts introduced",
            "Impact on digital asset ecosystem",
            "Foundation for future innovations",
            "Global accessibility improvements"
        ],
        
        "sources": [
            "https://ethereum.org/en/history/",
            "https://github.com/ethereum/go-ethereum",
            "https://blog.ethereum.org/",
            "https://etherscan.io/",
            "https://docs.ethereum.org/",
            "https://ethereum.github.io/yellowpaper/paper.pdf"
        ],
        
        "prompt_seed": {
            "style": "digital art, futuristic, blockchain aesthetic",
            "palette": "blue, purple, gold, electric colors",
            "motifs": ["geometric patterns", "network nodes", "flowing data", "crystalline structures"],
            "negative": "dark, dystopian, chaotic"
        }
    }
    
    # Add agent message for streaming
    message = {
        "agent": "Lore",
        "level": "info",
        "message": f"Generated historical context for {date_label}",
        "ts": str(uuid.uuid4()),
        "links": [{"label": f"Source {i+1}", "href": url} for i, url in enumerate(lore_pack["sources"][:3])]
    }
    
    return {
        "lore": lore_pack,
        "checkpoint": "lore_approval",
        "messages": [message]
    }
