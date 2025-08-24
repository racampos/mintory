"""
RunState and related type definitions for the LangGraph orchestrator.
"""
from typing import Dict, Any, Optional, List, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel
import operator


# Core types based on the project specification
class LorePack(BaseModel):
    summary_md: str  # <= 200 words
    bullet_facts: List[str]  # 5-10 crisp facts
    sources: List[str]  # URLs, 5+ preferred
    prompt_seed: Dict[str, Any]  # style, palette, motifs, negative


class ArtSet(BaseModel):
    cids: List[str]  # IPFS CIDs for full images
    thumbnails: List[str]  # IPFS or data URLs (<=200KB each)
    style_notes: List[str]  # one per image
    reject_reasons: Optional[List[str]] = None  # if any candidates filtered


class VoteConfig(BaseModel):
    method: str = "simple"
    gate: str  # "allowlist" | "open" | "passport_stub"
    duration_s: int


class VoteResult(BaseModel):
    winner_cid: str
    tally: Dict[str, int]
    participation: int


class VoteState(BaseModel):
    id: str
    config: VoteConfig
    result: Optional[VoteResult] = None


class MintReceipt(BaseModel):
    tx_hash: str
    token_id: str
    token_uri: str


class AttestationReceipt(BaseModel):
    id: str
    uri: str


class PreparedTx(BaseModel):
    to: str
    data: str
    value: Optional[str] = None
    gas: Optional[int] = None


# Main orchestrator state - using TypedDict for LangGraph compatibility
class RunState(TypedDict):
    run_id: str
    date_label: str
    lore: Optional[LorePack]
    art: Optional[ArtSet]
    vote: Optional[VoteState]
    prepared_tx: Optional[PreparedTx]
    mint_tx: Optional[Dict[str, Any]]  # Second transaction for mint after close vote
    mint: Optional[MintReceipt]
    attest: Optional[AttestationReceipt]
    checkpoint: Optional[str]
    error: Optional[str]
    # Messages for streaming updates
    messages: Annotated[List[Dict[str, Any]], operator.add]
