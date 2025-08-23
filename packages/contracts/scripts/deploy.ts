import { ethers } from "hardhat";
import * as fs from "fs";
import * as path from "path";

async function main() {
  console.log("Starting deployment of ShapeCraft2 contracts...");

  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);
  console.log("Account balance:", (await deployer.provider.getBalance(deployer.address)).toString());

  // Get network info
  const network = await ethers.provider.getNetwork();
  const chainId = Number(network.chainId);
  console.log("Network:", network.name, "Chain ID:", chainId);

  // Deploy HistorianMedals first
  console.log("\nDeploying HistorianMedals...");
  const HistorianMedals = await ethers.getContractFactory("HistorianMedals");
  const historianMedals = await HistorianMedals.deploy(deployer.address);
  await historianMedals.waitForDeployment();

  const historianMedalsAddress = await historianMedals.getAddress();
  console.log("HistorianMedals deployed to:", historianMedalsAddress);

  // Deploy DropManager
  console.log("\nDeploying DropManager...");
  const DropManager = await ethers.getContractFactory("DropManager");
  const dropManager = await DropManager.deploy(deployer.address);
  await dropManager.waitForDeployment();

  const dropManagerAddress = await dropManager.getAddress();
  console.log("DropManager deployed to:", dropManagerAddress);

  // Set contract references
  console.log("\nSetting contract references...");

  // Set DropManager in HistorianMedals
  console.log("Setting DropManager in HistorianMedals...");
  await historianMedals.setDropManager(dropManagerAddress);

  // Set NFT contracts in DropManager
  console.log("Setting NFT contracts in DropManager...");
  await dropManager.setNFTContracts(historianMedalsAddress, historianMedalsAddress);

  // Prepare addresses configuration
  const addressesConfig = {
    chainId: chainId,
    DropManager: dropManagerAddress,
    HistorianMedals: historianMedalsAddress,
    NFT: historianMedalsAddress // Using HistorianMedals as the NFT contract
  };

  console.log("\nDeployment addresses:", addressesConfig);

  // Ensure infra/deploy directory exists
  const deployDir = path.join(__dirname, "../../infra/deploy");
  if (!fs.existsSync(deployDir)) {
    fs.mkdirSync(deployDir, { recursive: true });
  }

  // Write addresses.json
  const addressesPath = path.join(deployDir, "addresses.json");
  fs.writeFileSync(addressesPath, JSON.stringify(addressesConfig, null, 2));
  console.log(`\nAddresses saved to: ${addressesPath}`);

  // Verify contracts
  console.log("\nVerifying contract deployments...");
  const dropManagerOwner = await dropManager.owner();
  const historianMedalsOwner = await historianMedals.owner();
  const historianMedalsManager = await historianMedals.dropManager();

  console.log("DropManager owner:", dropManagerOwner);
  console.log("HistorianMedals owner:", historianMedalsOwner);
  console.log("HistorianMedals DropManager:", historianMedalsManager);

  if (dropManagerOwner !== deployer.address || historianMedalsOwner !== deployer.address) {
    throw new Error("Contract ownership verification failed");
  }

  if (historianMedalsManager !== dropManagerAddress) {
    throw new Error("Contract reference verification failed");
  }

  console.log("\n✅ All contracts deployed and configured successfully!");
  console.log("📄 Addresses saved to:", addressesPath);
}

main().catch((error) => {
  console.error("Deployment failed:", error);
  process.exitCode = 1;
});
