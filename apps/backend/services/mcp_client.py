"""
MCP Client - HTTP client for communicating with the MCP server
Provides methods for all MCP endpoints with error handling and retries
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import httpx
import asyncio
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


@dataclass
class ChainInfo:
    """Chain information response"""
    chain_id: int
    name: str


@dataclass
class GasbackInfo:
    """Gasback information response"""
    accrued: str
    claimable: str


@dataclass
class Medal:
    """Medal information"""
    id: str
    balance: str


@dataclass
class MedalsResponse:
    """User medals response"""
    medals: List[Medal]


@dataclass
class PinResult:
    """IPFS pin result"""
    cid: str


@dataclass
class VoteConfig:
    """Vote configuration"""
    method: str
    gate: str
    duration_s: int


@dataclass
class PreparedTx:
    """Prepared transaction for signing"""
    to: str
    data: str
    value: Optional[str] = None
    gas: Optional[int] = None


@dataclass
class VoteStatus:
    """Vote status information"""
    open: bool
    tallies: List[int]
    ends_at: str


@dataclass
class TallyResult:
    """Vote tally result"""
    winner_cid: str
    tally: Dict[str, int]


class MCPClientError(Exception):
    """Base exception for MCP client errors"""
    pass


class MCPNetworkError(MCPClientError):
    """Network-related MCP errors"""
    pass


class MCPServerError(MCPClientError):
    """Server-side MCP errors"""
    pass


class MCPClient:
    """
    HTTP client for MCP server communication
    Handles all MCP endpoints with proper error handling and retries
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize MCP client
        
        Args:
            base_url: MCP server base URL (defaults to MCP_URL env var)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.base_url = base_url or os.getenv("MCP_URL", "http://localhost:3001")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Remove trailing slash for consistent URL joining
        self.base_url = self.base_url.rstrip("/")
        
        logger.info(f"Initialized MCP client with base URL: {self.base_url}")
    
    async def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[bytes] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic and error handling
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            params: Query parameters
            json_data: JSON request body
            data: Raw request body bytes
            headers: Request headers
            
        Returns:
            Response JSON data
            
        Raises:
            MCPNetworkError: For network/connection issues
            MCPServerError: For server-side errors
        """
        url = urljoin(self.base_url + "/", path.lstrip("/"))
        
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    logger.debug(f"Making {method} request to {url} (attempt {attempt + 1})")
                    
                    response = await client.request(
                        method=method,
                        url=url,
                        params=params,
                        json=json_data,
                        content=data,
                        headers=headers
                    )
                    
                    # Check for HTTP errors
                    if response.status_code >= 500:
                        raise MCPServerError(
                            f"Server error {response.status_code}: {response.text}"
                        )
                    elif response.status_code >= 400:
                        raise MCPClientError(
                            f"Client error {response.status_code}: {response.text}"
                        )
                    
                    # Parse JSON response
                    try:
                        return response.json()
                    except json.JSONDecodeError as e:
                        raise MCPServerError(f"Invalid JSON response: {e}")
                        
            except httpx.RequestError as e:
                logger.warning(f"Request error on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries:
                    raise MCPNetworkError(f"Network error after {self.max_retries + 1} attempts: {e}")
                
                # Wait before retry
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
            
            except (MCPClientError, MCPServerError):
                # Don't retry client/server errors
                raise
    
    async def get_chain_info(self) -> ChainInfo:
        """
        Get blockchain chain information
        
        Returns:
            ChainInfo object with chain ID and name
        """
        response = await self._make_request("GET", "/mcp/chain_info")
        return ChainInfo(
            chain_id=response["chainId"],
            name=response["name"]
        )
    
    async def get_gasback_info(self, contract: str) -> GasbackInfo:
        """
        Get gasback information for a contract
        
        Args:
            contract: Contract address
            
        Returns:
            GasbackInfo object with accrued and claimable amounts
        """
        params = {"contract": contract}
        response = await self._make_request("GET", "/mcp/gasback_info", params=params)
        return GasbackInfo(
            accrued=response["accrued"],
            claimable=response["claimable"]
        )
    
    async def get_user_medals(self, address: str) -> MedalsResponse:
        """
        Get medals owned by an address
        
        Args:
            address: Wallet address
            
        Returns:
            MedalsResponse object with user's medals
        """
        params = {"address": address}
        response = await self._make_request("GET", "/mcp/medal_of", params=params)
        medals = [
            Medal(id=medal["id"], balance=medal["balance"])
            for medal in response["medals"]
        ]
        return MedalsResponse(medals=medals)
    
    async def pin_cid(self, data: bytes, content_type: str = "application/octet-stream") -> PinResult:
        """
        Pin file data to IPFS
        
        Args:
            data: File bytes to pin
            content_type: MIME type of the data
            
        Returns:
            PinResult with IPFS CID
        """
        headers = {"content-type": content_type}
        response = await self._make_request(
            "POST", "/mcp/pin_cid", data=data, headers=headers
        )
        return PinResult(cid=response["cid"])
    
    async def pin_cid_from_url(self, url: str) -> PinResult:
        """
        Pin content from URL to IPFS
        
        Args:
            url: URL to pin
            
        Returns:
            PinResult with IPFS CID
        """
        json_data = {"url": url}
        headers = {"content-type": "application/json"}
        response = await self._make_request(
            "POST", "/mcp/pin_cid", json_data=json_data, headers=headers
        )
        return PinResult(cid=response["cid"])
    
    async def pin_metadata(self, metadata: Dict[str, Any]) -> PinResult:
        """
        Pin JSON metadata to IPFS
        
        Args:
            metadata: JSON metadata to pin
            
        Returns:
            PinResult with IPFS CID
        """
        response = await self._make_request("POST", "/mcp/pin_metadata", json_data=metadata)
        return PinResult(cid=response["cid"])
    
    async def start_vote(self, art_cids: List[str], config: VoteConfig) -> tuple[str, PreparedTx]:
        """
        Create a transaction to start a vote
        
        Args:
            art_cids: List of art CIDs to vote on
            config: Vote configuration
            
        Returns:
            Tuple of (vote_id, prepared_transaction)
        """
        json_data = {
            "artCids": art_cids,
            "cfg": {
                "method": config.method,
                "gate": config.gate,
                "duration_s": config.duration_s
            }
        }
        response = await self._make_request("POST", "/mcp/start_vote", json_data=json_data)
        
        tx_data = response["tx"]
        prepared_tx = PreparedTx(
            to=tx_data["to"],
            data=tx_data["data"],
            value=tx_data.get("value"),
            gas=tx_data.get("gas")
        )
        
        return response["vote_id"], prepared_tx
    
    async def get_vote_status(self, vote_id: str) -> VoteStatus:
        """
        Get the status of a vote
        
        Args:
            vote_id: Vote ID to check
            
        Returns:
            VoteStatus object with vote information
        """
        params = {"vote_id": vote_id}
        response = await self._make_request("GET", "/mcp/vote_status", params=params)
        return VoteStatus(
            open=response["open"],
            tallies=response["tallies"],
            ends_at=response["endsAt"]
        )
    
    async def tally_vote(self, vote_id: str) -> TallyResult:
        """
        Get vote tallies and determine winner
        
        Args:
            vote_id: Vote ID to tally
            
        Returns:
            TallyResult with winner CID and tallies
        """
        json_data = {"vote_id": vote_id}
        response = await self._make_request("POST", "/mcp/tally_vote", json_data=json_data)
        return TallyResult(
            winner_cid=response["winner_cid"],
            tally=response["tally"]
        )
    
    async def create_close_vote_transaction(self, vote_id: str):
        """
        Create a transaction to close a vote, or get skip instruction if vote already closed
        
        Args:
            vote_id: The vote ID to close
            
        Returns:
            PreparedTx for closing the vote, or dict with skip_close=True if vote already closed
        """
        json_data = {"vote_id": vote_id}
        response = await self._make_request("POST", "/mcp/close_vote", json_data=json_data)
        
        # Check if MCP server says to skip close vote
        if response.get("skip_close"):
            return {"skip_close": True, "message": response.get("message", "Vote already closed")}
        
        # Normal case: return PreparedTx
        tx_data = response["tx"]
        return PreparedTx(
            to=tx_data["to"],
            data=tx_data["data"],
            value=tx_data.get("value"),
            gas=tx_data.get("gas")
        )
    
    async def create_mint_transaction(self, vote_id: str, winner_cid: str, metadata_cid: str) -> PreparedTx:
        """
        Create a transaction to finalize an NFT mint
        
        Args:
            vote_id: The vote ID to finalize
            winner_cid: CID of the winning art
            metadata_cid: CID of the metadata
            
        Returns:
            PreparedTx for minting the NFT
        """
        json_data = {
            "vote_id": vote_id,
            "winner_cid": winner_cid,
            "metadataCid": metadata_cid
        }
        response = await self._make_request("POST", "/mcp/mint_final", json_data=json_data)
        
        tx_data = response["tx"]
        return PreparedTx(
            to=tx_data["to"],
            data=tx_data["data"],
            value=tx_data.get("value"),
            gas=tx_data.get("gas")
        )
    
    async def create_medal_transaction(self, to_address: str, medal_id: int) -> PreparedTx:
        """
        Create a transaction to issue a medal
        
        Args:
            to_address: Address to issue medal to
            medal_id: Medal ID to issue
            
        Returns:
            PreparedTx for issuing the medal
        """
        json_data = {
            "toAddress": to_address,
            "id": medal_id
        }
        response = await self._make_request("POST", "/mcp/issue_medal", json_data=json_data)
        
        tx_data = response["tx"]
        return PreparedTx(
            to=tx_data["to"],
            data=tx_data["data"],
            value=tx_data.get("value"),
            gas=tx_data.get("gas")
        )


# Global MCP client instance
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """
    Get global MCP client instance (singleton pattern)
    
    Returns:
        MCPClient instance
    """
    global _mcp_client
    if _mcp_client is None:
        timeout = float(os.getenv("MCP_TIMEOUT", "30.0"))
        _mcp_client = MCPClient(timeout=timeout)
    return _mcp_client
