// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/interfaces/IERC721.sol";

/**
 * @title DropManager
 * @dev Manages voting sessions for NFT drops and coordinates minting with HistorianMedals
 */
contract DropManager is Ownable, ReentrancyGuard {
    // Custom errors
    error VoteNotFound(bytes32 voteId);
    error VoteAlreadyClosed(bytes32 voteId);
    error VoteNotOpen(bytes32 voteId);
    error InvalidVoteIndex(uint256 index, uint256 maxIndex);
    error UnauthorizedVoter(address voter);
    error InvalidDuration(uint256 duration);
    error EmptyCIDs();
    error DuplicateCID(string cid);

    // Enums
    enum VoteMethod {
        Simple,
        Quadratic
    }
    enum VoteGate {
        Open,
        TokenGated
    }

    // Structs
    struct VoteConfig {
        VoteMethod method;
        VoteGate gate;
        uint256 duration; // in seconds
        uint256 startTime;
        bool isOpen;
    }

    struct Vote {
        bytes32 voteId;
        string[] cids;
        VoteConfig config;
        mapping(uint256 => uint256) votes; // index => vote count
        mapping(address => bool) hasVoted;
        mapping(address => uint256) voterIndex;
        uint256 totalVotes;
        string winnerCid;
        bool finalized;
    }

    // State variables
    mapping(bytes32 => Vote) public votes;
    bytes32[] public voteIds;

    IERC721 public historianMedals;
    IERC721 public nftContract;

    // Events
    event VoteOpened(bytes32 indexed voteId, string[] cids, VoteConfig config);
    event VoteCast(
        bytes32 indexed voteId,
        address indexed voter,
        uint256 indexed index
    );
    event VoteClosed(bytes32 indexed voteId, string winnerCid);
    event MintFinalized(
        bytes32 indexed voteId,
        uint256 indexed tokenId,
        string tokenURI
    );
    event NFTContractsUpdated(
        address indexed historianMedals,
        address indexed nftContract
    );

    // Modifiers
    modifier voteExists(bytes32 voteId) {
        if (votes[voteId].config.startTime == 0) revert VoteNotFound(voteId);
        _;
    }

    modifier voteOpen(bytes32 voteId) {
        if (!votes[voteId].config.isOpen) revert VoteNotOpen(voteId);
        _;
    }

    modifier voteClosed(bytes32 voteId) {
        if (votes[voteId].config.isOpen) revert VoteAlreadyClosed(voteId);
        _;
    }

    constructor(address initialOwner) Ownable(initialOwner) {}

    /**
     * @dev Update NFT contract addresses
     */
    function setNFTContracts(
        address _historianMedals,
        address _nftContract
    ) external onlyOwner {
        historianMedals = IERC721(_historianMedals);
        nftContract = IERC721(_nftContract);
        emit NFTContractsUpdated(_historianMedals, _nftContract);
    }

    /**
     * @dev Open a new voting session
     */
    function openVote(
        string[] calldata cids,
        VoteConfig calldata config
    ) external onlyOwner returns (bytes32 voteId) {
        // Validate inputs
        if (cids.length == 0) revert EmptyCIDs();
        if (config.duration == 0) revert InvalidDuration(config.duration);

        // Check for duplicate CIDs
        for (uint256 i = 0; i < cids.length; i++) {
            for (uint256 j = i + 1; j < cids.length; j++) {
                if (
                    keccak256(abi.encodePacked(cids[i])) ==
                    keccak256(abi.encodePacked(cids[j]))
                ) {
                    revert DuplicateCID(cids[i]);
                }
            }
        }

        // Generate vote ID
        bytes32 cidsHash;
        for (uint256 i = 0; i < cids.length; i++) {
            cidsHash = keccak256(abi.encodePacked(cidsHash, cids[i]));
        }

        voteId = keccak256(
            abi.encodePacked(
                block.timestamp,
                block.prevrandao,
                cidsHash,
                msg.sender
            )
        );

        // Create vote
        Vote storage vote = votes[voteId];
        vote.voteId = voteId;

        // Copy cids array to storage
        for (uint256 i = 0; i < cids.length; i++) {
            vote.cids.push(cids[i]);
        }

        vote.config = config;
        vote.config.startTime = block.timestamp;
        vote.config.isOpen = true;

        voteIds.push(voteId);

        emit VoteOpened(voteId, cids, config);
    }

    /**
     * @dev Cast a vote in an open voting session
     */
    function castVote(
        bytes32 voteId,
        uint256 index
    ) external voteExists(voteId) voteOpen(voteId) nonReentrant {
        Vote storage vote = votes[voteId];

        // Check if vote is still open (time-based)
        if (block.timestamp > vote.config.startTime + vote.config.duration) {
            _closeVote(voteId);
            return;
        }

        // Check gate requirements
        if (vote.config.gate == VoteGate.TokenGated) {
            if (historianMedals.balanceOf(msg.sender) == 0) {
                revert UnauthorizedVoter(msg.sender);
            }
        }

        // Validate index
        if (index >= vote.cids.length) {
            revert InvalidVoteIndex(index, vote.cids.length - 1);
        }

        // Check if already voted
        if (vote.hasVoted[msg.sender]) {
            // Remove previous vote
            uint256 prevIndex = vote.voterIndex[msg.sender];
            vote.votes[prevIndex]--;
            vote.totalVotes--;
        }

        // Cast vote
        vote.hasVoted[msg.sender] = true;
        vote.voterIndex[msg.sender] = index;
        vote.votes[index]++;
        vote.totalVotes++;

        emit VoteCast(voteId, msg.sender, index);
    }

    /**
     * @dev Close a voting session (automatically or manually)
     */
    function closeVote(
        bytes32 voteId
    ) external voteExists(voteId) voteOpen(voteId) {
        _closeVote(voteId);
    }

    /**
     * @dev Internal function to close vote and determine winner
     */
    function _closeVote(bytes32 voteId) internal {
        Vote storage vote = votes[voteId];
        vote.config.isOpen = false;

        // Find winner (index with most votes)
        uint256 maxVotes = 0;
        uint256 winnerIndex = 0;

        for (uint256 i = 0; i < vote.cids.length; i++) {
            if (vote.votes[i] > maxVotes) {
                maxVotes = vote.votes[i];
                winnerIndex = i;
            }
        }

        // If tie, pick first index
        vote.winnerCid = vote.cids[winnerIndex];

        emit VoteClosed(voteId, vote.winnerCid);
    }

    /**
     * @dev Finalize mint after vote is closed
     */
    function finalizeMint(
        bytes32 voteId,
        string calldata winnerCid,
        string calldata tokenURI
    )
        external
        voteExists(voteId)
        voteClosed(voteId)
        onlyOwner
        returns (uint256 tokenId)
    {
        Vote storage vote = votes[voteId];

        // Verify winner CID matches
        require(
            keccak256(abi.encodePacked(vote.winnerCid)) ==
                keccak256(abi.encodePacked(winnerCid)),
            "Winner CID mismatch"
        );

        // Mark as finalized
        vote.finalized = true;

        // This would typically call mint on the NFT contract
        // For now, we'll just emit the event with a placeholder tokenId
        // In a real implementation, you'd call: tokenId = nftContract.mint(tokenURI);
        tokenId = uint256(voteId); // Placeholder

        emit MintFinalized(voteId, tokenId, tokenURI);
    }

    /**
     * @dev Get vote details
     */
    function getVote(
        bytes32 voteId
    )
        external
        view
        voteExists(voteId)
        returns (
            string[] memory cids,
            VoteConfig memory config,
            uint256[] memory voteCounts,
            uint256 totalVotes,
            string memory winnerCid,
            bool finalized
        )
    {
        Vote storage vote = votes[voteId];

        voteCounts = new uint256[](vote.cids.length);
        for (uint256 i = 0; i < vote.cids.length; i++) {
            voteCounts[i] = vote.votes[i];
        }

        return (
            vote.cids,
            vote.config,
            voteCounts,
            vote.totalVotes,
            vote.winnerCid,
            vote.finalized
        );
    }

    /**
     * @dev Get all vote IDs
     */
    function getVoteIds() external view returns (bytes32[] memory) {
        return voteIds;
    }

    /**
     * @dev Check if an address has voted in a specific vote
     */
    function hasVoted(
        bytes32 voteId,
        address voter
    ) external view voteExists(voteId) returns (bool) {
        return votes[voteId].hasVoted[voter];
    }
}
