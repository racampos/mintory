#!/usr/bin/env python3
"""
Script to verify NFT metadata for minted tokens
"""
import requests
from web3 import Web3
from dotenv import load_dotenv
import os
import json

load_dotenv()

# Shape Testnet Configuration  
CHAIN_ID = 11011
RPC_URL = "https://shape-sepolia.g.alchemy.com/v2/lFQY2zhDOR9h_q3Z0CNTWMdLy7q8n692"
HISTORIAN_MEDALS_ADDRESS = "0x02dAD25503dF77e2fb987906f4EB0F60535ede05"

# HistorianMedals ABI - just the functions we need
HISTORIAN_MEDALS_ABI = [
    {
        "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
        "name": "tokenURI",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
        "name": "ownerOf", 
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

def verify_nft_metadata(token_id: int = 1):
    """Verify the metadata for a specific NFT token ID"""
    
    print(f"🔍 Verifying NFT metadata for Token ID {token_id}")
    print(f"📍 Contract: {HISTORIAN_MEDALS_ADDRESS}")
    print(f"🌐 Network: Shape Testnet ({CHAIN_ID})")
    print()
    
    # Connect to blockchain
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("❌ Failed to connect to blockchain")
        return
    
    print(f"✅ Connected to blockchain (block: {w3.eth.block_number})")
    
    # Create contract instance
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(HISTORIAN_MEDALS_ADDRESS),
        abi=HISTORIAN_MEDALS_ABI
    )
    
    try:
        # Get total supply first
        total_supply = contract.functions.totalSupply().call()
        print(f"📊 Total NFTs minted: {total_supply}")
        
        if token_id > total_supply:
            print(f"❌ Token ID {token_id} doesn't exist (only {total_supply} tokens minted)")
            return
            
        # Get owner
        owner = contract.functions.ownerOf(token_id).call()
        print(f"👤 Token #{token_id} owner: {owner}")
        
        # Get tokenURI  
        token_uri = contract.functions.tokenURI(token_id).call()
        print(f"🔗 Token URI: {token_uri}")
        
        # Fetch metadata from IPFS
        if token_uri.startswith('ipfs://'):
            # Convert to HTTP gateway URL
            ipfs_hash = token_uri[7:]  # Remove 'ipfs://' prefix
            gateway_url = f"https://ipfs.io/ipfs/{ipfs_hash}"
            print(f"🌐 Gateway URL: {gateway_url}")
            
            try:
                print("📥 Fetching metadata from IPFS...")
                response = requests.get(gateway_url, timeout=10)
                
                if response.status_code == 200:
                    metadata = response.json()
                    print("✅ Metadata retrieved successfully!")
                    print()
                    print("📋 NFT METADATA:")
                    print("=" * 50)
                    print(f"Name: {metadata.get('name', 'N/A')}")
                    print(f"Description: {metadata.get('description', 'N/A')}")
                    print(f"Image: {metadata.get('image', 'N/A')}")
                    
                    if 'attributes' in metadata:
                        print(f"Attributes: {len(metadata['attributes'])} traits")
                        for attr in metadata['attributes']:
                            print(f"  - {attr.get('trait_type')}: {attr.get('value')}")
                    
                    if 'properties' in metadata:
                        props = metadata['properties']
                        print("Properties:")
                        print(f"  - Sources: {len(props.get('sources', []))}")
                        print(f"  - Art Options: {len(props.get('art_options', []))}")
                        if 'vote_result' in props:
                            vote = props['vote_result'] 
                            print(f"  - Vote Winner: {vote.get('winner_cid', 'N/A')}")
                            print(f"  - Total Votes: {sum(vote.get('tally', {}).values())}")
                    
                    print("=" * 50)
                    
                    # Test if image URL is accessible
                    image_url = metadata.get('image')
                    if image_url:
                        print(f"🖼️  Testing image URL: {image_url}")
                        try:
                            img_response = requests.head(image_url, timeout=5)
                            if img_response.status_code == 200:
                                print("✅ Image is accessible!")
                            else:
                                print(f"⚠️  Image returned status: {img_response.status_code}")
                        except Exception as img_e:
                            print(f"❌ Image not accessible: {img_e}")
                    
                else:
                    print(f"❌ Failed to fetch metadata: HTTP {response.status_code}")
                    print(f"Response: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"❌ Error fetching metadata: {e}")
        
        else:
            print(f"⚠️  Token URI doesn't use IPFS format: {token_uri}")
            
    except Exception as e:
        print(f"❌ Error querying contract: {e}")

if __name__ == "__main__":
    # First check how many NFTs exist
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if w3.is_connected():
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(HISTORIAN_MEDALS_ADDRESS),
            abi=HISTORIAN_MEDALS_ABI
        )
        total_supply = contract.functions.totalSupply().call()
        print(f"🔢 Total NFTs in collection: {total_supply}")
        print()
        
        # Check the latest minted NFT
        latest_token_id = total_supply
        print(f"🔍 Checking latest NFT (Token #{latest_token_id}):")
        verify_nft_metadata(latest_token_id)
        
        # If there are multiple NFTs, also check the previous one for comparison
        if total_supply > 1:
            print("\n" + "="*60)
            print(f"🔍 For comparison, checking Token #1:")
            verify_nft_metadata(1)
    else:
        print("❌ Failed to connect to blockchain")
        verify_nft_metadata(1)
