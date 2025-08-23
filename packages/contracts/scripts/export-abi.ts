import * as fs from "fs";
import * as path from "path";
import { Contract } from "ethers";

// Contract names to export
const CONTRACT_NAMES = ["DropManager", "HistorianMedals"];

interface ContractArtifact {
  abi: any[];
  bytecode: string;
  deployedBytecode: string;
  contractName: string;
  sourceName: string;
}

async function main() {
  console.log("Exporting contract ABIs...");

  // Ensure abi directory exists
  const abiDir = path.join(__dirname, "../abi");
  if (!fs.existsSync(abiDir)) {
    fs.mkdirSync(abiDir, { recursive: true });
  }

  // Process each contract
  for (const contractName of CONTRACT_NAMES) {
    const artifactPath = path.join(__dirname, "../artifacts/contracts", `${contractName}.sol`, `${contractName}.json`);

    if (!fs.existsSync(artifactPath)) {
      console.warn(`⚠️  Artifact not found for ${contractName} at ${artifactPath}`);
      console.log("Make sure to compile contracts first with: npm run compile");
      continue;
    }

    try {
      const artifact: ContractArtifact = JSON.parse(fs.readFileSync(artifactPath, "utf8"));

      // Filter ABI to only include functions we need (as specified in contracts_and_addresses.md)
      let filteredAbi = artifact.abi;

      if (contractName === "DropManager") {
        // Filter DropManager ABI to only include specified functions and events
        const allowedNames = [
          "openVote",
          "castVote",
          "closeVote",
          "finalizeMint",
          "getVote",
          "getVoteIds",
          "hasVoted",
          "setNFTContracts",
          "owner",
          "VoteOpened",
          "VoteClosed",
          "MintFinalized",
          "NFTContractsUpdated"
        ];

        filteredAbi = artifact.abi.filter((item: any) =>
          allowedNames.includes(item.name || item.type)
        );
      }

      // Save filtered ABI
      const abiPath = path.join(abiDir, `${contractName}.json`);
      fs.writeFileSync(abiPath, JSON.stringify(filteredAbi, null, 2));
      console.log(`✅ ${contractName} ABI saved to: ${abiPath}`);

      // Also save full ABI with .full suffix
      const fullAbiPath = path.join(abiDir, `${contractName}.full.json`);
      fs.writeFileSync(fullAbiPath, JSON.stringify(artifact.abi, null, 2));
      console.log(`📄 ${contractName} full ABI saved to: ${fullAbiPath}`);

    } catch (error) {
      console.error(`❌ Error processing ${contractName}:`, error);
    }
  }

  // Create a combined ABI file for convenience
  try {
    const combinedAbi: any[] = [];

    for (const contractName of CONTRACT_NAMES) {
      const abiPath = path.join(abiDir, `${contractName}.json`);
      if (fs.existsSync(abiPath)) {
        const abi = JSON.parse(fs.readFileSync(abiPath, "utf8"));
        combinedAbi.push(...abi);
      }
    }

    const combinedPath = path.join(abiDir, "combined.json");
    fs.writeFileSync(combinedPath, JSON.stringify(combinedAbi, null, 2));
    console.log(`🔗 Combined ABI saved to: ${combinedPath}`);

  } catch (error) {
    console.error("❌ Error creating combined ABI:", error);
  }

  // Create TypeScript types for the ABIs
  await generateTypeScriptTypes(abiDir);

  console.log("\n🎉 ABI export completed!");
}

async function generateTypeScriptTypes(abiDir: string) {
  console.log("\nGenerating TypeScript types...");

  try {
    const typesPath = path.join(abiDir, "index.ts");

    let typesContent = `// Auto-generated ABI exports for ShapeCraft2 contracts
// Generated on: ${new Date().toISOString()}

`;

    for (const contractName of CONTRACT_NAMES) {
      const abiPath = path.join(abiDir, `${contractName}.json`);
      if (fs.existsSync(abiPath)) {
        const abi = JSON.parse(fs.readFileSync(abiPath, "utf8"));
        typesContent += `export const ${contractName}Abi = ${JSON.stringify(abi, null, 2)} as const;\n\n`;
      }
    }

    // Add combined export
    const combinedPath = path.join(abiDir, "combined.json");
    if (fs.existsSync(combinedPath)) {
      const combinedAbi = JSON.parse(fs.readFileSync(combinedPath, "utf8"));
      typesContent += `export const CombinedAbi = ${JSON.stringify(combinedAbi, null, 2)} as const;\n\n`;
    }

    // Add type exports
    typesContent += `// Type exports
export type { ${CONTRACT_NAMES.join(", ")} } from "./types";

// Re-export contract types for convenience
export type DropManagerAbiType = typeof import("./DropManager.json");
export type HistorianMedalsAbiType = typeof import("./HistorianMedals.json");
`;

    fs.writeFileSync(typesPath, typesContent);
    console.log(`📝 TypeScript types saved to: ${typesPath}`);

  } catch (error) {
    console.error("❌ Error generating TypeScript types:", error);
  }
}

main().catch((error) => {
  console.error("ABI export failed:", error);
  process.exitCode = 1;
});
