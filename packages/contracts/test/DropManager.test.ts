import { expect } from "chai";
import { ethers } from "hardhat";
import { DropManager, HistorianMedals } from "../typechain-types";

describe("DropManager", function () {
  let dropManager: DropManager;
  let historianMedals: HistorianMedals;
  let owner: any;
  let user1: any;
  let user2: any;

  beforeEach(async function () {
    [owner, user1, user2] = await ethers.getSigners();

    // Deploy HistorianMedals first
    const HistorianMedalsFactory = await ethers.getContractFactory("HistorianMedals");
    historianMedals = await HistorianMedalsFactory.deploy(owner.address);
    await historianMedals.waitForDeployment();

    // Deploy DropManager
    const DropManagerFactory = await ethers.getContractFactory("DropManager");
    dropManager = await DropManagerFactory.deploy(owner.address);
    await dropManager.waitForDeployment();

    // Set up contract references
    await historianMedals.setDropManager(await dropManager.getAddress());
    await dropManager.setNFTContracts(
      await historianMedals.getAddress(),
      await historianMedals.getAddress()
    );
  });

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      expect(await dropManager.owner()).to.equal(owner.address);
      expect(await historianMedals.owner()).to.equal(owner.address);
    });

    it("Should have correct contract references", async function () {
      expect(await historianMedals.dropManager()).to.equal(await dropManager.getAddress());
    });
  });

  describe("Voting", function () {
    it("Should open a vote successfully", async function () {
      const cids = ["ipfs://QmTest1", "ipfs://QmTest2"];
      const voteConfig = {
        method: 0, // Simple voting
        gate: 0,   // Open voting
        duration: 3600 // 1 hour
      };

      await expect(dropManager.openVote(cids, voteConfig))
        .to.emit(dropManager, "VoteOpened");

      const voteIds = await dropManager.getVoteIds();
      expect(voteIds.length).to.equal(1);
    });

    it("Should reject empty CIDs", async function () {
      const cids: string[] = [];
      const voteConfig = {
        method: 0,
        gate: 0,
        duration: 3600
      };

      await expect(dropManager.openVote(cids, voteConfig))
        .to.be.revertedWithCustomError(dropManager, "EmptyCIDs");
    });

    it("Should cast votes correctly", async function () {
      // Open a vote
      const cids = ["ipfs://QmTest1", "ipfs://QmTest2"];
      const voteConfig = {
        method: 0,
        gate: 0,
        duration: 3600
      };

      await dropManager.openVote(cids, voteConfig);
      const voteIds = await dropManager.getVoteIds();
      const voteId = voteIds[0];

      // Cast votes
      await expect(dropManager.connect(user1).castVote(voteId, 0))
        .to.emit(dropManager, "VoteCast")
        .withArgs(voteId, user1.address, 0);

      await expect(dropManager.connect(user2).castVote(voteId, 1))
        .to.emit(dropManager, "VoteCast")
        .withArgs(voteId, user2.address, 1);

      // Check voting status
      expect(await dropManager.hasVoted(voteId, user1.address)).to.be.true;
      expect(await dropManager.hasVoted(voteId, user2.address)).to.be.true;
    });

    it("Should prevent double voting", async function () {
      // Open a vote
      const cids = ["ipfs://QmTest1", "ipfs://QmTest2"];
      const voteConfig = {
        method: 0,
        gate: 0,
        duration: 3600
      };

      await dropManager.openVote(cids, voteConfig);
      const voteIds = await dropManager.getVoteIds();
      const voteId = voteIds[0];

      // Cast first vote
      await dropManager.connect(user1).castVote(voteId, 0);

      // Cast second vote (should change the first vote, not add another)
      await dropManager.connect(user1).castVote(voteId, 1);

      // Check vote details
      const voteData = await dropManager.getVote(voteId);
      expect(voteData.totalVotes).to.equal(1); // Should still be 1 vote
      expect(voteData.voteCounts[1]).to.equal(1); // Should be on index 1
    });
  });
});
