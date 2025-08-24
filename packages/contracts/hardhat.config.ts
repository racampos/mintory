import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import * as dotenv from "dotenv";

dotenv.config();

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  networks: {
    hardhat: {
      chainId: 1337,
    },
    // Shape Mainnet
    shapemainnet: {
      url: process.env.SHAPE_RPC_URL || "https://shape-mainnet.g.alchemy.com/v2/YOUR_API_KEY",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      chainId: 360, // Shape Mainnet chain ID
    },
    // Shape Testnet (for testing)
    shapetestnet: {
      url: process.env.SHAPE_TESTNET_RPC_URL || "https://shape-sepolia.g.alchemy.com/v2/lFQY2zhDOR9h_q3Z0CNTWMdLy7q8n692",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      chainId: 11011, // Shape testnet chain ID
    },
  },
  etherscan: {
    apiKey: {
      // Note: Shape uses its own verification system
      // You may need to configure a custom verifier
      mainnet: process.env.ETHERSCAN_API_KEY || "",
    },
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    scripts: "./scripts",
    artifacts: "./artifacts",
    cache: "./cache",
  },
  typechain: {
    outDir: "./typechain-types",
    target: "ethers-v6",
  },
};

export default config;
