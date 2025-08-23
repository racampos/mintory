export declare const DropManagerAbi: readonly [{
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: true;
        readonly internalType: "bytes32";
        readonly name: "voteId";
        readonly type: "bytes32";
    }, {
        readonly indexed: true;
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }, {
        readonly indexed: false;
        readonly internalType: "string";
        readonly name: "tokenURI";
        readonly type: "string";
    }];
    readonly name: "MintFinalized";
    readonly type: "event";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "historianMedals";
        readonly type: "address";
    }, {
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "nftContract";
        readonly type: "address";
    }];
    readonly name: "NFTContractsUpdated";
    readonly type: "event";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: true;
        readonly internalType: "bytes32";
        readonly name: "voteId";
        readonly type: "bytes32";
    }, {
        readonly indexed: false;
        readonly internalType: "string";
        readonly name: "winnerCid";
        readonly type: "string";
    }];
    readonly name: "VoteClosed";
    readonly type: "event";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: true;
        readonly internalType: "bytes32";
        readonly name: "voteId";
        readonly type: "bytes32";
    }, {
        readonly indexed: false;
        readonly internalType: "string[]";
        readonly name: "cids";
        readonly type: "string[]";
    }, {
        readonly components: readonly [{
            readonly internalType: "enum DropManager.VoteMethod";
            readonly name: "method";
            readonly type: "uint8";
        }, {
            readonly internalType: "enum DropManager.VoteGate";
            readonly name: "gate";
            readonly type: "uint8";
        }, {
            readonly internalType: "uint256";
            readonly name: "duration";
            readonly type: "uint256";
        }, {
            readonly internalType: "uint256";
            readonly name: "startTime";
            readonly type: "uint256";
        }, {
            readonly internalType: "bool";
            readonly name: "isOpen";
            readonly type: "bool";
        }];
        readonly indexed: false;
        readonly internalType: "struct DropManager.VoteConfig";
        readonly name: "config";
        readonly type: "tuple";
    }];
    readonly name: "VoteOpened";
    readonly type: "event";
}, {
    readonly inputs: readonly [{
        readonly internalType: "bytes32";
        readonly name: "voteId";
        readonly type: "bytes32";
    }, {
        readonly internalType: "uint256";
        readonly name: "index";
        readonly type: "uint256";
    }];
    readonly name: "castVote";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "bytes32";
        readonly name: "voteId";
        readonly type: "bytes32";
    }];
    readonly name: "closeVote";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "bytes32";
        readonly name: "voteId";
        readonly type: "bytes32";
    }, {
        readonly internalType: "string";
        readonly name: "winnerCid";
        readonly type: "string";
    }, {
        readonly internalType: "string";
        readonly name: "tokenURI";
        readonly type: "string";
    }];
    readonly name: "finalizeMint";
    readonly outputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "bytes32";
        readonly name: "voteId";
        readonly type: "bytes32";
    }];
    readonly name: "getVote";
    readonly outputs: readonly [{
        readonly internalType: "string[]";
        readonly name: "cids";
        readonly type: "string[]";
    }, {
        readonly components: readonly [{
            readonly internalType: "enum DropManager.VoteMethod";
            readonly name: "method";
            readonly type: "uint8";
        }, {
            readonly internalType: "enum DropManager.VoteGate";
            readonly name: "gate";
            readonly type: "uint8";
        }, {
            readonly internalType: "uint256";
            readonly name: "duration";
            readonly type: "uint256";
        }, {
            readonly internalType: "uint256";
            readonly name: "startTime";
            readonly type: "uint256";
        }, {
            readonly internalType: "bool";
            readonly name: "isOpen";
            readonly type: "bool";
        }];
        readonly internalType: "struct DropManager.VoteConfig";
        readonly name: "config";
        readonly type: "tuple";
    }, {
        readonly internalType: "uint256[]";
        readonly name: "voteCounts";
        readonly type: "uint256[]";
    }, {
        readonly internalType: "uint256";
        readonly name: "totalVotes";
        readonly type: "uint256";
    }, {
        readonly internalType: "string";
        readonly name: "winnerCid";
        readonly type: "string";
    }, {
        readonly internalType: "bool";
        readonly name: "finalized";
        readonly type: "bool";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [];
    readonly name: "getVoteIds";
    readonly outputs: readonly [{
        readonly internalType: "bytes32[]";
        readonly name: "";
        readonly type: "bytes32[]";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "bytes32";
        readonly name: "voteId";
        readonly type: "bytes32";
    }, {
        readonly internalType: "address";
        readonly name: "voter";
        readonly type: "address";
    }];
    readonly name: "hasVoted";
    readonly outputs: readonly [{
        readonly internalType: "bool";
        readonly name: "";
        readonly type: "bool";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "string[]";
        readonly name: "cids";
        readonly type: "string[]";
    }, {
        readonly components: readonly [{
            readonly internalType: "enum DropManager.VoteMethod";
            readonly name: "method";
            readonly type: "uint8";
        }, {
            readonly internalType: "enum DropManager.VoteGate";
            readonly name: "gate";
            readonly type: "uint8";
        }, {
            readonly internalType: "uint256";
            readonly name: "duration";
            readonly type: "uint256";
        }, {
            readonly internalType: "uint256";
            readonly name: "startTime";
            readonly type: "uint256";
        }, {
            readonly internalType: "bool";
            readonly name: "isOpen";
            readonly type: "bool";
        }];
        readonly internalType: "struct DropManager.VoteConfig";
        readonly name: "config";
        readonly type: "tuple";
    }];
    readonly name: "openVote";
    readonly outputs: readonly [{
        readonly internalType: "bytes32";
        readonly name: "voteId";
        readonly type: "bytes32";
    }];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [];
    readonly name: "owner";
    readonly outputs: readonly [{
        readonly internalType: "address";
        readonly name: "";
        readonly type: "address";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "_historianMedals";
        readonly type: "address";
    }, {
        readonly internalType: "address";
        readonly name: "_nftContract";
        readonly type: "address";
    }];
    readonly name: "setNFTContracts";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}];
export declare const HistorianMedalsAbi: readonly [{
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "initialOwner";
        readonly type: "address";
    }];
    readonly stateMutability: "nonpayable";
    readonly type: "constructor";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "sender";
        readonly type: "address";
    }, {
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }, {
        readonly internalType: "address";
        readonly name: "owner";
        readonly type: "address";
    }];
    readonly name: "ERC721IncorrectOwner";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "operator";
        readonly type: "address";
    }, {
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "ERC721InsufficientApproval";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "approver";
        readonly type: "address";
    }];
    readonly name: "ERC721InvalidApprover";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "operator";
        readonly type: "address";
    }];
    readonly name: "ERC721InvalidOperator";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "owner";
        readonly type: "address";
    }];
    readonly name: "ERC721InvalidOwner";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "receiver";
        readonly type: "address";
    }];
    readonly name: "ERC721InvalidReceiver";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "sender";
        readonly type: "address";
    }];
    readonly name: "ERC721InvalidSender";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "ERC721NonexistentToken";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "string";
        readonly name: "uri";
        readonly type: "string";
    }];
    readonly name: "InvalidTokenURI";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "owner";
        readonly type: "address";
    }];
    readonly name: "OwnableInvalidOwner";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "account";
        readonly type: "address";
    }];
    readonly name: "OwnableUnauthorizedAccount";
    readonly type: "error";
}, {
    readonly inputs: readonly [];
    readonly name: "ReentrancyGuardReentrantCall";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "TokenAlreadyMinted";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "caller";
        readonly type: "address";
    }];
    readonly name: "UnauthorizedMinter";
    readonly type: "error";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "owner";
        readonly type: "address";
    }, {
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "approved";
        readonly type: "address";
    }, {
        readonly indexed: true;
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "Approval";
    readonly type: "event";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "owner";
        readonly type: "address";
    }, {
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "operator";
        readonly type: "address";
    }, {
        readonly indexed: false;
        readonly internalType: "bool";
        readonly name: "approved";
        readonly type: "bool";
    }];
    readonly name: "ApprovalForAll";
    readonly type: "event";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: false;
        readonly internalType: "uint256";
        readonly name: "_fromTokenId";
        readonly type: "uint256";
    }, {
        readonly indexed: false;
        readonly internalType: "uint256";
        readonly name: "_toTokenId";
        readonly type: "uint256";
    }];
    readonly name: "BatchMetadataUpdate";
    readonly type: "event";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "oldManager";
        readonly type: "address";
    }, {
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "newManager";
        readonly type: "address";
    }];
    readonly name: "DropManagerUpdated";
    readonly type: "event";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: false;
        readonly internalType: "uint256";
        readonly name: "_tokenId";
        readonly type: "uint256";
    }];
    readonly name: "MetadataUpdate";
    readonly type: "event";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "previousOwner";
        readonly type: "address";
    }, {
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "newOwner";
        readonly type: "address";
    }];
    readonly name: "OwnershipTransferred";
    readonly type: "event";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: true;
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }, {
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "to";
        readonly type: "address";
    }, {
        readonly indexed: false;
        readonly internalType: "string";
        readonly name: "tokenURI";
        readonly type: "string";
    }];
    readonly name: "TokenMinted";
    readonly type: "event";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "from";
        readonly type: "address";
    }, {
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "to";
        readonly type: "address";
    }, {
        readonly indexed: true;
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "Transfer";
    readonly type: "event";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "to";
        readonly type: "address";
    }, {
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "approve";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "owner";
        readonly type: "address";
    }];
    readonly name: "balanceOf";
    readonly outputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "";
        readonly type: "uint256";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address[]";
        readonly name: "recipients";
        readonly type: "address[]";
    }, {
        readonly internalType: "string[]";
        readonly name: "uris";
        readonly type: "string[]";
    }];
    readonly name: "batchMint";
    readonly outputs: readonly [{
        readonly internalType: "uint256[]";
        readonly name: "";
        readonly type: "uint256[]";
    }];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [];
    readonly name: "contractURI";
    readonly outputs: readonly [{
        readonly internalType: "string";
        readonly name: "";
        readonly type: "string";
    }];
    readonly stateMutability: "pure";
    readonly type: "function";
}, {
    readonly inputs: readonly [];
    readonly name: "dropManager";
    readonly outputs: readonly [{
        readonly internalType: "address";
        readonly name: "";
        readonly type: "address";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "exists";
    readonly outputs: readonly [{
        readonly internalType: "bool";
        readonly name: "";
        readonly type: "bool";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "getApproved";
    readonly outputs: readonly [{
        readonly internalType: "address";
        readonly name: "";
        readonly type: "address";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "getTokenMetadata";
    readonly outputs: readonly [{
        readonly internalType: "address";
        readonly name: "owner";
        readonly type: "address";
    }, {
        readonly internalType: "string";
        readonly name: "uri";
        readonly type: "string";
    }, {
        readonly internalType: "bool";
        readonly name: "tokenExists";
        readonly type: "bool";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "owner";
        readonly type: "address";
    }, {
        readonly internalType: "address";
        readonly name: "operator";
        readonly type: "address";
    }];
    readonly name: "isApprovedForAll";
    readonly outputs: readonly [{
        readonly internalType: "bool";
        readonly name: "";
        readonly type: "bool";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "to";
        readonly type: "address";
    }, {
        readonly internalType: "string";
        readonly name: "uri";
        readonly type: "string";
    }];
    readonly name: "mint";
    readonly outputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "";
        readonly type: "uint256";
    }];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [];
    readonly name: "name";
    readonly outputs: readonly [{
        readonly internalType: "string";
        readonly name: "";
        readonly type: "string";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [];
    readonly name: "owner";
    readonly outputs: readonly [{
        readonly internalType: "address";
        readonly name: "";
        readonly type: "address";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "ownerOf";
    readonly outputs: readonly [{
        readonly internalType: "address";
        readonly name: "";
        readonly type: "address";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [];
    readonly name: "renounceOwnership";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "from";
        readonly type: "address";
    }, {
        readonly internalType: "address";
        readonly name: "to";
        readonly type: "address";
    }, {
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "safeTransferFrom";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "from";
        readonly type: "address";
    }, {
        readonly internalType: "address";
        readonly name: "to";
        readonly type: "address";
    }, {
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }, {
        readonly internalType: "bytes";
        readonly name: "data";
        readonly type: "bytes";
    }];
    readonly name: "safeTransferFrom";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "operator";
        readonly type: "address";
    }, {
        readonly internalType: "bool";
        readonly name: "approved";
        readonly type: "bool";
    }];
    readonly name: "setApprovalForAll";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "_dropManager";
        readonly type: "address";
    }];
    readonly name: "setDropManager";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "bytes4";
        readonly name: "interfaceId";
        readonly type: "bytes4";
    }];
    readonly name: "supportsInterface";
    readonly outputs: readonly [{
        readonly internalType: "bool";
        readonly name: "";
        readonly type: "bool";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [];
    readonly name: "symbol";
    readonly outputs: readonly [{
        readonly internalType: "string";
        readonly name: "";
        readonly type: "string";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "tokenURI";
    readonly outputs: readonly [{
        readonly internalType: "string";
        readonly name: "";
        readonly type: "string";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "owner";
        readonly type: "address";
    }];
    readonly name: "tokensOfOwner";
    readonly outputs: readonly [{
        readonly internalType: "uint256[]";
        readonly name: "";
        readonly type: "uint256[]";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [];
    readonly name: "totalSupply";
    readonly outputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "";
        readonly type: "uint256";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "from";
        readonly type: "address";
    }, {
        readonly internalType: "address";
        readonly name: "to";
        readonly type: "address";
    }, {
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "transferFrom";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "newOwner";
        readonly type: "address";
    }];
    readonly name: "transferOwnership";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}];
export declare const CombinedAbi: readonly [{
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: true;
        readonly internalType: "bytes32";
        readonly name: "voteId";
        readonly type: "bytes32";
    }, {
        readonly indexed: true;
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }, {
        readonly indexed: false;
        readonly internalType: "string";
        readonly name: "tokenURI";
        readonly type: "string";
    }];
    readonly name: "MintFinalized";
    readonly type: "event";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "historianMedals";
        readonly type: "address";
    }, {
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "nftContract";
        readonly type: "address";
    }];
    readonly name: "NFTContractsUpdated";
    readonly type: "event";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: true;
        readonly internalType: "bytes32";
        readonly name: "voteId";
        readonly type: "bytes32";
    }, {
        readonly indexed: false;
        readonly internalType: "string";
        readonly name: "winnerCid";
        readonly type: "string";
    }];
    readonly name: "VoteClosed";
    readonly type: "event";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: true;
        readonly internalType: "bytes32";
        readonly name: "voteId";
        readonly type: "bytes32";
    }, {
        readonly indexed: false;
        readonly internalType: "string[]";
        readonly name: "cids";
        readonly type: "string[]";
    }, {
        readonly components: readonly [{
            readonly internalType: "enum DropManager.VoteMethod";
            readonly name: "method";
            readonly type: "uint8";
        }, {
            readonly internalType: "enum DropManager.VoteGate";
            readonly name: "gate";
            readonly type: "uint8";
        }, {
            readonly internalType: "uint256";
            readonly name: "duration";
            readonly type: "uint256";
        }, {
            readonly internalType: "uint256";
            readonly name: "startTime";
            readonly type: "uint256";
        }, {
            readonly internalType: "bool";
            readonly name: "isOpen";
            readonly type: "bool";
        }];
        readonly indexed: false;
        readonly internalType: "struct DropManager.VoteConfig";
        readonly name: "config";
        readonly type: "tuple";
    }];
    readonly name: "VoteOpened";
    readonly type: "event";
}, {
    readonly inputs: readonly [{
        readonly internalType: "bytes32";
        readonly name: "voteId";
        readonly type: "bytes32";
    }, {
        readonly internalType: "uint256";
        readonly name: "index";
        readonly type: "uint256";
    }];
    readonly name: "castVote";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "bytes32";
        readonly name: "voteId";
        readonly type: "bytes32";
    }];
    readonly name: "closeVote";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "bytes32";
        readonly name: "voteId";
        readonly type: "bytes32";
    }, {
        readonly internalType: "string";
        readonly name: "winnerCid";
        readonly type: "string";
    }, {
        readonly internalType: "string";
        readonly name: "tokenURI";
        readonly type: "string";
    }];
    readonly name: "finalizeMint";
    readonly outputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "bytes32";
        readonly name: "voteId";
        readonly type: "bytes32";
    }];
    readonly name: "getVote";
    readonly outputs: readonly [{
        readonly internalType: "string[]";
        readonly name: "cids";
        readonly type: "string[]";
    }, {
        readonly components: readonly [{
            readonly internalType: "enum DropManager.VoteMethod";
            readonly name: "method";
            readonly type: "uint8";
        }, {
            readonly internalType: "enum DropManager.VoteGate";
            readonly name: "gate";
            readonly type: "uint8";
        }, {
            readonly internalType: "uint256";
            readonly name: "duration";
            readonly type: "uint256";
        }, {
            readonly internalType: "uint256";
            readonly name: "startTime";
            readonly type: "uint256";
        }, {
            readonly internalType: "bool";
            readonly name: "isOpen";
            readonly type: "bool";
        }];
        readonly internalType: "struct DropManager.VoteConfig";
        readonly name: "config";
        readonly type: "tuple";
    }, {
        readonly internalType: "uint256[]";
        readonly name: "voteCounts";
        readonly type: "uint256[]";
    }, {
        readonly internalType: "uint256";
        readonly name: "totalVotes";
        readonly type: "uint256";
    }, {
        readonly internalType: "string";
        readonly name: "winnerCid";
        readonly type: "string";
    }, {
        readonly internalType: "bool";
        readonly name: "finalized";
        readonly type: "bool";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [];
    readonly name: "getVoteIds";
    readonly outputs: readonly [{
        readonly internalType: "bytes32[]";
        readonly name: "";
        readonly type: "bytes32[]";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "bytes32";
        readonly name: "voteId";
        readonly type: "bytes32";
    }, {
        readonly internalType: "address";
        readonly name: "voter";
        readonly type: "address";
    }];
    readonly name: "hasVoted";
    readonly outputs: readonly [{
        readonly internalType: "bool";
        readonly name: "";
        readonly type: "bool";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "string[]";
        readonly name: "cids";
        readonly type: "string[]";
    }, {
        readonly components: readonly [{
            readonly internalType: "enum DropManager.VoteMethod";
            readonly name: "method";
            readonly type: "uint8";
        }, {
            readonly internalType: "enum DropManager.VoteGate";
            readonly name: "gate";
            readonly type: "uint8";
        }, {
            readonly internalType: "uint256";
            readonly name: "duration";
            readonly type: "uint256";
        }, {
            readonly internalType: "uint256";
            readonly name: "startTime";
            readonly type: "uint256";
        }, {
            readonly internalType: "bool";
            readonly name: "isOpen";
            readonly type: "bool";
        }];
        readonly internalType: "struct DropManager.VoteConfig";
        readonly name: "config";
        readonly type: "tuple";
    }];
    readonly name: "openVote";
    readonly outputs: readonly [{
        readonly internalType: "bytes32";
        readonly name: "voteId";
        readonly type: "bytes32";
    }];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [];
    readonly name: "owner";
    readonly outputs: readonly [{
        readonly internalType: "address";
        readonly name: "";
        readonly type: "address";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "_historianMedals";
        readonly type: "address";
    }, {
        readonly internalType: "address";
        readonly name: "_nftContract";
        readonly type: "address";
    }];
    readonly name: "setNFTContracts";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "initialOwner";
        readonly type: "address";
    }];
    readonly stateMutability: "nonpayable";
    readonly type: "constructor";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "sender";
        readonly type: "address";
    }, {
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }, {
        readonly internalType: "address";
        readonly name: "owner";
        readonly type: "address";
    }];
    readonly name: "ERC721IncorrectOwner";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "operator";
        readonly type: "address";
    }, {
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "ERC721InsufficientApproval";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "approver";
        readonly type: "address";
    }];
    readonly name: "ERC721InvalidApprover";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "operator";
        readonly type: "address";
    }];
    readonly name: "ERC721InvalidOperator";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "owner";
        readonly type: "address";
    }];
    readonly name: "ERC721InvalidOwner";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "receiver";
        readonly type: "address";
    }];
    readonly name: "ERC721InvalidReceiver";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "sender";
        readonly type: "address";
    }];
    readonly name: "ERC721InvalidSender";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "ERC721NonexistentToken";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "string";
        readonly name: "uri";
        readonly type: "string";
    }];
    readonly name: "InvalidTokenURI";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "owner";
        readonly type: "address";
    }];
    readonly name: "OwnableInvalidOwner";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "account";
        readonly type: "address";
    }];
    readonly name: "OwnableUnauthorizedAccount";
    readonly type: "error";
}, {
    readonly inputs: readonly [];
    readonly name: "ReentrancyGuardReentrantCall";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "TokenAlreadyMinted";
    readonly type: "error";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "caller";
        readonly type: "address";
    }];
    readonly name: "UnauthorizedMinter";
    readonly type: "error";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "owner";
        readonly type: "address";
    }, {
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "approved";
        readonly type: "address";
    }, {
        readonly indexed: true;
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "Approval";
    readonly type: "event";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "owner";
        readonly type: "address";
    }, {
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "operator";
        readonly type: "address";
    }, {
        readonly indexed: false;
        readonly internalType: "bool";
        readonly name: "approved";
        readonly type: "bool";
    }];
    readonly name: "ApprovalForAll";
    readonly type: "event";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: false;
        readonly internalType: "uint256";
        readonly name: "_fromTokenId";
        readonly type: "uint256";
    }, {
        readonly indexed: false;
        readonly internalType: "uint256";
        readonly name: "_toTokenId";
        readonly type: "uint256";
    }];
    readonly name: "BatchMetadataUpdate";
    readonly type: "event";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "oldManager";
        readonly type: "address";
    }, {
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "newManager";
        readonly type: "address";
    }];
    readonly name: "DropManagerUpdated";
    readonly type: "event";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: false;
        readonly internalType: "uint256";
        readonly name: "_tokenId";
        readonly type: "uint256";
    }];
    readonly name: "MetadataUpdate";
    readonly type: "event";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "previousOwner";
        readonly type: "address";
    }, {
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "newOwner";
        readonly type: "address";
    }];
    readonly name: "OwnershipTransferred";
    readonly type: "event";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: true;
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }, {
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "to";
        readonly type: "address";
    }, {
        readonly indexed: false;
        readonly internalType: "string";
        readonly name: "tokenURI";
        readonly type: "string";
    }];
    readonly name: "TokenMinted";
    readonly type: "event";
}, {
    readonly anonymous: false;
    readonly inputs: readonly [{
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "from";
        readonly type: "address";
    }, {
        readonly indexed: true;
        readonly internalType: "address";
        readonly name: "to";
        readonly type: "address";
    }, {
        readonly indexed: true;
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "Transfer";
    readonly type: "event";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "to";
        readonly type: "address";
    }, {
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "approve";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "owner";
        readonly type: "address";
    }];
    readonly name: "balanceOf";
    readonly outputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "";
        readonly type: "uint256";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address[]";
        readonly name: "recipients";
        readonly type: "address[]";
    }, {
        readonly internalType: "string[]";
        readonly name: "uris";
        readonly type: "string[]";
    }];
    readonly name: "batchMint";
    readonly outputs: readonly [{
        readonly internalType: "uint256[]";
        readonly name: "";
        readonly type: "uint256[]";
    }];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [];
    readonly name: "contractURI";
    readonly outputs: readonly [{
        readonly internalType: "string";
        readonly name: "";
        readonly type: "string";
    }];
    readonly stateMutability: "pure";
    readonly type: "function";
}, {
    readonly inputs: readonly [];
    readonly name: "dropManager";
    readonly outputs: readonly [{
        readonly internalType: "address";
        readonly name: "";
        readonly type: "address";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "exists";
    readonly outputs: readonly [{
        readonly internalType: "bool";
        readonly name: "";
        readonly type: "bool";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "getApproved";
    readonly outputs: readonly [{
        readonly internalType: "address";
        readonly name: "";
        readonly type: "address";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "getTokenMetadata";
    readonly outputs: readonly [{
        readonly internalType: "address";
        readonly name: "owner";
        readonly type: "address";
    }, {
        readonly internalType: "string";
        readonly name: "uri";
        readonly type: "string";
    }, {
        readonly internalType: "bool";
        readonly name: "tokenExists";
        readonly type: "bool";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "owner";
        readonly type: "address";
    }, {
        readonly internalType: "address";
        readonly name: "operator";
        readonly type: "address";
    }];
    readonly name: "isApprovedForAll";
    readonly outputs: readonly [{
        readonly internalType: "bool";
        readonly name: "";
        readonly type: "bool";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "to";
        readonly type: "address";
    }, {
        readonly internalType: "string";
        readonly name: "uri";
        readonly type: "string";
    }];
    readonly name: "mint";
    readonly outputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "";
        readonly type: "uint256";
    }];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [];
    readonly name: "name";
    readonly outputs: readonly [{
        readonly internalType: "string";
        readonly name: "";
        readonly type: "string";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [];
    readonly name: "owner";
    readonly outputs: readonly [{
        readonly internalType: "address";
        readonly name: "";
        readonly type: "address";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "ownerOf";
    readonly outputs: readonly [{
        readonly internalType: "address";
        readonly name: "";
        readonly type: "address";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [];
    readonly name: "renounceOwnership";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "from";
        readonly type: "address";
    }, {
        readonly internalType: "address";
        readonly name: "to";
        readonly type: "address";
    }, {
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "safeTransferFrom";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "from";
        readonly type: "address";
    }, {
        readonly internalType: "address";
        readonly name: "to";
        readonly type: "address";
    }, {
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }, {
        readonly internalType: "bytes";
        readonly name: "data";
        readonly type: "bytes";
    }];
    readonly name: "safeTransferFrom";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "operator";
        readonly type: "address";
    }, {
        readonly internalType: "bool";
        readonly name: "approved";
        readonly type: "bool";
    }];
    readonly name: "setApprovalForAll";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "_dropManager";
        readonly type: "address";
    }];
    readonly name: "setDropManager";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "bytes4";
        readonly name: "interfaceId";
        readonly type: "bytes4";
    }];
    readonly name: "supportsInterface";
    readonly outputs: readonly [{
        readonly internalType: "bool";
        readonly name: "";
        readonly type: "bool";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [];
    readonly name: "symbol";
    readonly outputs: readonly [{
        readonly internalType: "string";
        readonly name: "";
        readonly type: "string";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "tokenURI";
    readonly outputs: readonly [{
        readonly internalType: "string";
        readonly name: "";
        readonly type: "string";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "owner";
        readonly type: "address";
    }];
    readonly name: "tokensOfOwner";
    readonly outputs: readonly [{
        readonly internalType: "uint256[]";
        readonly name: "";
        readonly type: "uint256[]";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [];
    readonly name: "totalSupply";
    readonly outputs: readonly [{
        readonly internalType: "uint256";
        readonly name: "";
        readonly type: "uint256";
    }];
    readonly stateMutability: "view";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "from";
        readonly type: "address";
    }, {
        readonly internalType: "address";
        readonly name: "to";
        readonly type: "address";
    }, {
        readonly internalType: "uint256";
        readonly name: "tokenId";
        readonly type: "uint256";
    }];
    readonly name: "transferFrom";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}, {
    readonly inputs: readonly [{
        readonly internalType: "address";
        readonly name: "newOwner";
        readonly type: "address";
    }];
    readonly name: "transferOwnership";
    readonly outputs: readonly [];
    readonly stateMutability: "nonpayable";
    readonly type: "function";
}];
export type { DropManager, HistorianMedals } from "../typechain-types/contracts/index.js";
export type DropManagerAbiType = typeof import("./DropManager.json");
export type HistorianMedalsAbiType = typeof import("./HistorianMedals.json");
//# sourceMappingURL=index.d.ts.map