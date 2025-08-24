#!/usr/bin/env python3
"""
Test script to cast a vote on the DropManager contract during live polling.

Usage:
    python test_vote_cast.py <vote_id> <image_index> [private_key]
    
Example:
    python test_vote_cast.py 0x55503594fc686d... 1
    python test_vote_cast.py 0x55503594fc686d... 0 0x1234...abcd
    
Environment:
    VOTER_PRIVATE_KEY=0x... (if not provided as argument)
"""

import sys
import os
from web3 import Web3
from eth_account import Account
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Shape Testnet Configuration
CHAIN_ID = 11011
RPC_URL = "https://shape-sepolia.g.alchemy.com/v2/lFQY2zhDOR9h_q3Z0CNTWMdLy7q8n692"
DROP_MANAGER_ADDRESS = "0x2E5B4dC1DbbD2BE7f8B3f81d91eCaE54D1e75d57"

# DropManager ABI - corrected structure from MCP server
DROP_MANAGER_ABI = [
    {
        "type": "error",
        "name": "VoteNotFound",
        "inputs": [{"internalType": "bytes32", "name": "voteId", "type": "bytes32"}]
    },
    {
        "inputs": [
            {"name": "voteId", "type": "bytes32"},
            {"name": "index", "type": "uint256"}
        ],
        "name": "castVote",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "voteId", "type": "bytes32"}],
        "name": "getVote", 
        "outputs": [
            {"internalType": "string[]", "name": "cids", "type": "string[]"},
            {
                "components": [
                    {"internalType": "uint8", "name": "method", "type": "uint8"},
                    {"internalType": "uint8", "name": "gate", "type": "uint8"},
                    {"internalType": "uint256", "name": "duration", "type": "uint256"},
                    {"internalType": "uint256", "name": "startTime", "type": "uint256"},
                    {"internalType": "bool", "name": "isOpen", "type": "bool"}
                ],
                "internalType": "struct DropManager.VoteConfig",
                "name": "config",
                "type": "tuple"
            },
            {"internalType": "uint256[]", "name": "voteCounts", "type": "uint256[]"},
            {"internalType": "uint256", "name": "totalVotes", "type": "uint256"},
            {"internalType": "string", "name": "winnerCid", "type": "string"},
            {"internalType": "bool", "name": "finalized", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

def cast_vote(vote_id: str, image_index: int, private_key: str):
    """Cast a vote on the DropManager contract"""
    
    print(f"🗳️  CAST VOTE SCRIPT")
    print(f"📊 Vote ID: {vote_id}")
    print(f"🎨 Image Index: {image_index}")
    print(f"⛓️  Chain: Shape Testnet ({CHAIN_ID})")
    print(f"📍 Contract: {DROP_MANAGER_ADDRESS}")
    print()
    
    # Initialize Web3
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    if not w3.is_connected():
        print("❌ Failed to connect to RPC")
        return False
        
    print(f"✅ Connected to Shape Testnet")
    print(f"📡 Block Number: {w3.eth.block_number}")
    
    # Setup account
    account = Account.from_key(private_key)
    voter_address = account.address
    
    print(f"👤 Voter Address: {voter_address}")
    
    # Check balance
    balance = w3.eth.get_balance(voter_address)
    balance_eth = w3.from_wei(balance, 'ether')
    print(f"💰 Balance: {balance_eth:.6f} ETH")
    
    if balance == 0:
        print("❌ No ETH for gas fees!")
        return False
    
    # Setup contract
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(DROP_MANAGER_ADDRESS),
        abi=DROP_MANAGER_ABI
    )
    
    print()
    print(f"🔍 Checking vote status before casting...")
    
    # Check current vote status
    try:
        vote_data = contract.functions.getVote(vote_id).call()
        cids, config, vote_counts, total_votes, winner_cid, finalized = vote_data
        
        print(f"📈 Current tallies: {list(vote_counts)}")
        print(f"🔢 Total votes: {total_votes}")
        print(f"🎯 Available options: {len(cids)} images")
        print(f"📅 Vote open: {config[4]}")  # config.isOpen
        print(f"🏁 Finalized: {finalized}")
        
        if not config[4]:  # config.isOpen
            print("❌ Vote is closed!")
            return False
            
        if finalized:
            print("❌ Vote is already finalized!")
            return False
            
        if image_index >= len(cids):
            print(f"❌ Invalid image index! Must be 0-{len(cids)-1}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to check vote status: {e}")
        return False
    
    print()
    print(f"🚀 Casting vote for image #{image_index}...")
    
    # Prepare transaction
    try:
        # Get current gas price
        gas_price = w3.eth.gas_price
        
        # Build transaction
        transaction = contract.functions.castVote(vote_id, image_index).build_transaction({
            'from': voter_address,
            'gas': 300000,  # Generous gas limit
            'gasPrice': gas_price,
            'nonce': w3.eth.get_transaction_count(voter_address),
            'chainId': CHAIN_ID
        })
        
        print(f"⛽ Gas Price: {w3.from_wei(gas_price, 'gwei'):.2f} gwei")
        print(f"⛽ Gas Limit: {transaction['gas']:,}")
        print(f"💸 Max Fee: {w3.from_wei(gas_price * transaction['gas'], 'ether'):.6f} ETH")
        
        # Sign transaction
        signed_txn = account.sign_transaction(transaction)
        
        # Send transaction
        print(f"📡 Broadcasting transaction...")
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_hash_hex = tx_hash.hex()
        
        print(f"✅ Transaction sent!")
        print(f"🔗 Tx Hash: {tx_hash_hex}")
        print(f"🔍 Explorer: https://explorer.shape.network/tx/{tx_hash_hex}")
        
        # Wait for confirmation
        print(f"⏳ Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt.status == 1:
            print(f"🎉 Vote cast successfully!")
            print(f"📊 Block: {receipt.blockNumber}")
            print(f"⛽ Gas Used: {receipt.gasUsed:,}")
            
            # Check updated vote status
            print()
            print(f"🔍 Checking updated vote tallies...")
            time.sleep(2)  # Give nodes time to sync
            
            vote_data_after = contract.functions.getVote(vote_id).call()
            _, _, vote_counts_after, total_votes_after, _, _ = vote_data_after
            
            print(f"📈 New tallies: {list(vote_counts_after)}")
            print(f"🔢 New total: {total_votes_after}")
            print(f"✅ Vote successfully recorded!")
            
            return True
            
        else:
            print(f"❌ Transaction failed!")
            return False
            
    except Exception as e:
        print(f"❌ Transaction failed: {e}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python test_vote_cast.py <vote_id> <image_index> [private_key]")
        print("Example: python test_vote_cast.py 0x123...abc 1")
        sys.exit(1)
    
    vote_id = sys.argv[1]
    
    try:
        image_index = int(sys.argv[2])
    except ValueError:
        print("❌ Image index must be a number (0, 1, 2, etc.)")
        sys.exit(1)
    
    # Get private key from argument or environment
    if len(sys.argv) >= 4:
        private_key = sys.argv[3]
    else:
        private_key = os.getenv('VOTER_PRIVATE_KEY')
        
    if not private_key:
        print("❌ Private key required!")
        print("Provide via argument: python test_vote_cast.py <vote_id> <index> <private_key>")
        print("Or set environment: VOTER_PRIVATE_KEY=0x...")
        sys.exit(1)
        
    if not private_key.startswith('0x'):
        private_key = '0x' + private_key
        
    # Validate inputs
    if not vote_id.startswith('0x') or len(vote_id) != 66:
        print("❌ Invalid vote_id format! Must be 0x followed by 64 hex characters")
        sys.exit(1)
        
    if image_index < 0:
        print("❌ Image index must be non-negative!")
        sys.exit(1)
    
    # Cast the vote
    success = cast_vote(vote_id, image_index, private_key)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
