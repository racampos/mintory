// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

/**
 * @title HistorianMedals
 * @dev ERC721 token for ShapeCraft2 commemorative NFTs with metadata support
 */
contract HistorianMedals is ERC721, ERC721URIStorage, Ownable, ReentrancyGuard {
    using Strings for uint256;

    // Custom errors
    error UnauthorizedMinter(address caller);
    error InvalidTokenURI(string uri);
    error TokenAlreadyMinted(uint256 tokenId);

    // State variables
    uint256 private _nextTokenId;
    address public dropManager;

    // Events
    event DropManagerUpdated(
        address indexed oldManager,
        address indexed newManager
    );
    event TokenMinted(
        uint256 indexed tokenId,
        address indexed to,
        string tokenURI
    );

    // Modifiers
    modifier onlyDropManager() {
        if (msg.sender != dropManager) revert UnauthorizedMinter(msg.sender);
        _;
    }

    constructor(
        address initialOwner
    ) ERC721("HistorianMedals", "HMDL") Ownable(initialOwner) {
        _nextTokenId = 1;
    }

    /**
     * @dev Set the DropManager contract address
     */
    function setDropManager(address _dropManager) external onlyOwner {
        address oldManager = dropManager;
        dropManager = _dropManager;
        emit DropManagerUpdated(oldManager, _dropManager);
    }

    /**
     * @dev Mint a new token (only callable by DropManager)
     */
    function mint(
        address to,
        string calldata uri
    ) external onlyDropManager nonReentrant returns (uint256) {
        // Validate URI format (should be IPFS CID)
        if (bytes(uri).length == 0) revert InvalidTokenURI(uri);
        if (!startsWith(uri, "ipfs://")) revert InvalidTokenURI(uri);

        uint256 tokenId = _nextTokenId++;
        _mint(to, tokenId);
        _setTokenURI(tokenId, uri);

        emit TokenMinted(tokenId, to, uri);
        return tokenId;
    }

    /**
     * @dev Batch mint multiple tokens (for efficiency)
     */
    function batchMint(
        address[] calldata recipients,
        string[] calldata uris
    ) external onlyDropManager nonReentrant returns (uint256[] memory) {
        if (recipients.length != uris.length) revert("Arrays length mismatch");
        if (recipients.length == 0) revert("Empty arrays");

        uint256[] memory tokenIds = new uint256[](recipients.length);

        for (uint256 i = 0; i < recipients.length; i++) {
            // Validate URI
            if (bytes(uris[i]).length == 0) revert InvalidTokenURI(uris[i]);
            if (!startsWith(uris[i], "ipfs://"))
                revert InvalidTokenURI(uris[i]);

            uint256 tokenId = _nextTokenId++;
            _mint(recipients[i], tokenId);
            _setTokenURI(tokenId, uris[i]);

            tokenIds[i] = tokenId;
            emit TokenMinted(tokenId, recipients[i], uris[i]);
        }

        return tokenIds;
    }

    /**
     * @dev Get the total supply of tokens
     */
    function totalSupply() external view returns (uint256) {
        return _nextTokenId - 1;
    }

    /**
     * @dev Get all token IDs owned by an address
     */
    function tokensOfOwner(
        address owner
    ) external view returns (uint256[] memory) {
        uint256 tokenCount = balanceOf(owner);
        if (tokenCount == 0) return new uint256[](0);

        uint256[] memory tokens = new uint256[](tokenCount);
        uint256 index = 0;

        for (uint256 tokenId = 1; tokenId < _nextTokenId; tokenId++) {
            if (ownerOf(tokenId) == owner) {
                tokens[index] = tokenId;
                index++;
            }
        }

        return tokens;
    }

    /**
     * @dev Check if a token exists
     */
    function exists(uint256 tokenId) external view returns (bool) {
        return _ownerOf(tokenId) != address(0);
    }

    /**
     * @dev Get token metadata with enhanced information
     */
    function getTokenMetadata(
        uint256 tokenId
    )
        external
        view
        returns (address owner, string memory uri, bool tokenExists)
    {
        tokenExists = _ownerOf(tokenId) != address(0);
        if (!tokenExists) return (address(0), "", false);

        return (ownerOf(tokenId), tokenURI(tokenId), true);
    }

    /**
     * @dev Get contract metadata for marketplaces
     */
    function contractURI() external pure returns (string memory) {
        return "ipfs://QmYourContractMetadataCID"; // Replace with actual contract metadata
    }

    /**
     * @dev Internal helper to check if string starts with prefix
     */
    function startsWith(
        string memory str,
        string memory prefix
    ) internal pure returns (bool) {
        bytes memory strBytes = bytes(str);
        bytes memory prefixBytes = bytes(prefix);

        if (strBytes.length < prefixBytes.length) return false;

        for (uint256 i = 0; i < prefixBytes.length; i++) {
            if (strBytes[i] != prefixBytes[i]) return false;
        }

        return true;
    }

    /**
     * @dev Override required by Solidity for multiple inheritance
     */
    function tokenURI(
        uint256 tokenId
    ) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId);
    }

    /**
     * @dev Override required by Solidity for multiple inheritance
     */
    function supportsInterface(
        bytes4 interfaceId
    ) public view override(ERC721, ERC721URIStorage) returns (bool) {
        return super.supportsInterface(interfaceId);
    }

    /**
     * @dev Override _update to add custom logic if needed
     */
    function _update(
        address to,
        uint256 tokenId,
        address auth
    ) internal override returns (address) {
        return super._update(to, tokenId, auth);
    }

    /**
     * @dev Custom transfer logic can be added here if needed
     * Note: In newer OpenZeppelin versions, use _beforeTokenTransfer is replaced by _update
     */
}
