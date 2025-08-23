import { run } from "hardhat";
import * as fs from "fs";
import * as path from "path";
import { ethers } from "hardhat";

/**
 * Verify contracts on Shape Network
 * Shape uses a custom verification system, not Etherscan
 */
async function main() {
  console.log("🔍 Verifying contracts on Shape Network...");

  // Check current network
  const network = await ethers.provider.getNetwork();
  const chainId = Number(network.chainId);
  console.log("🌐 Connected to network:", network.name, "Chain ID:", chainId);

  // Read deployed addresses
  const addressesPath = path.join(__dirname, "../../../infra/deploy/addresses.json");
  if (!fs.existsSync(addressesPath)) {
    throw new Error("❌ addresses.json not found. Deploy contracts first.");
  }

  const addresses = JSON.parse(fs.readFileSync(addressesPath, "utf8"));
  console.log("📄 Loaded addresses:", addresses);

  // Verify chain ID matches
  if (addresses.chainId !== chainId) {
    console.log(`⚠️  Warning: Address file shows Chain ID ${addresses.chainId}, but connected to ${chainId}`);
    console.log("📝 Verification may fail due to network mismatch");
  }

  // Verify DropManager
  if (addresses.DropManager) {
    console.log(`\n🔍 Verifying DropManager at ${addresses.DropManager}...`);
    try {
      await run("verify:verify", {
        address: addresses.DropManager,
        // Network will be determined by --network flag
        // Shape may require custom verification parameters
        // You may need to adjust these based on Shape's verification API
      });
      console.log("✅ DropManager verified successfully");
    } catch (error) {
      console.log("⚠️  DropManager verification failed:", error instanceof Error ? error.message : String(error));
      console.log("📝 Manual verification may be required at: https://explorer.shape.network");
    }
  }

  // Verify HistorianMedals
  if (addresses.HistorianMedals) {
    console.log(`\n🔍 Verifying HistorianMedals at ${addresses.HistorianMedals}...`);
    try {
      await run("verify:verify", {
        address: addresses.HistorianMedals,
        // Network will be determined by --network flag
        // Constructor arguments if any
        // constructorArguments: [],
      });
      console.log("✅ HistorianMedals verified successfully");
    } catch (error) {
      console.log("⚠️  HistorianMedals verification failed:", error instanceof Error ? error.message : String(error));
      console.log("📝 Manual verification may be required at: https://explorer.shape.network");
    }
  }

  console.log("\n🎉 Verification process completed!");
  console.log("📋 Check https://explorer.shape.network for contract details");
}

// Handle Shape Network verification
main().catch((error) => {
  console.error("❌ Verification failed:", error);
  console.log("\n💡 Troubleshooting tips:");
  console.log("1. Ensure contracts are deployed to the target network");
  console.log("2. Check if Shape explorer supports verification");
  console.log("3. Manual verification may be required");
  console.log("4. Visit: https://explorer.shape.network (mainnet) or https://explorer-sepolia.shape.network (testnet)");
  process.exitCode = 1;
});
