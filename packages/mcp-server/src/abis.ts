// Local ABI definitions for MCP server
// Imported from contracts package to avoid TypeScript rootDir issues

export const DropManagerAbi = [
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "voteId",
        "type": "bytes32"
      },
      {
        "internalType": "uint256",
        "name": "index",
        "type": "uint256"
      }
    ],
    "name": "castVote",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "voteId",
        "type": "bytes32"
      }
    ],
    "name": "closeVote",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "voteId",
        "type": "bytes32"
      },
      {
        "internalType": "string",
        "name": "winnerCid",
        "type": "string"
      },
      {
        "internalType": "string",
        "name": "tokenURI",
        "type": "string"
      }
    ],
    "name": "finalizeMint",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "tokenId",
        "type": "uint256"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "voteId",
        "type": "bytes32"
      }
    ],
    "name": "getVote",
    "outputs": [
      {
        "internalType": "string[]",
        "name": "cids",
        "type": "string[]"
      },
      {
        "components": [
          {
            "internalType": "enum DropManager.VoteMethod",
            "name": "method",
            "type": "uint8"
          },
          {
            "internalType": "enum DropManager.VoteGate",
            "name": "gate",
            "type": "uint8"
          },
          {
            "internalType": "uint256",
            "name": "duration",
            "type": "uint256"
          },
          {
            "internalType": "uint256",
            "name": "startTime",
            "type": "uint256"
          },
          {
            "internalType": "bool",
            "name": "isOpen",
            "type": "bool"
          }
        ],
        "internalType": "struct DropManager.VoteConfig",
        "name": "config",
        "type": "tuple"
      },
      {
        "internalType": "uint256[]",
        "name": "voteCounts",
        "type": "uint256[]"
      },
      {
        "internalType": "uint256",
        "name": "totalVotes",
        "type": "uint256"
      },
      {
        "internalType": "string",
        "name": "winnerCid",
        "type": "string"
      },
      {
        "internalType": "bool",
        "name": "finalized",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "string[]",
        "name": "cids",
        "type": "string[]"
      },
      {
        "components": [
          {
            "internalType": "enum DropManager.VoteMethod",
            "name": "method",
            "type": "uint8"
          },
          {
            "internalType": "enum DropManager.VoteGate",
            "name": "gate",
            "type": "uint8"
          },
          {
            "internalType": "uint256",
            "name": "duration",
            "type": "uint256"
          },
          {
            "internalType": "uint256",
            "name": "startTime",
            "type": "uint256"
          },
          {
            "internalType": "bool",
            "name": "isOpen",
            "type": "bool"
          }
        ],
        "internalType": "struct DropManager.VoteConfig",
        "name": "config",
        "type": "tuple"
      }
    ],
    "name": "openVote",
    "outputs": [
      {
        "internalType": "bytes32",
        "name": "voteId",
        "type": "bytes32"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  }
] as const;

export const HistorianMedalsAbi = [
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "internalType": "string",
        "name": "uri",
        "type": "string"
      }
    ],
    "name": "mint",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "owner",
        "type": "address"
      }
    ],
    "name": "tokensOfOwner",
    "outputs": [
      {
        "internalType": "uint256[]",
        "name": "",
        "type": "uint256[]"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  }
] as const;
