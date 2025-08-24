import FormData from 'form-data';
import type { PinResult } from './types.js';

// IPFS Pinning Service Configuration
const PINNING_SERVICE = {
  // Using Pinata as the pinning service
  PINATA_JWT: process.env.PINATA_JWT || '',
  PINATA_API_URL: 'https://api.pinata.cloud/pinning',
  
  // Fallback to Web3.Storage if preferred
  WEB3_STORAGE_TOKEN: process.env.WEB3_STORAGE_TOKEN || '',
  WEB3_STORAGE_API_URL: 'https://api.web3.storage',
};

export async function pinFile(data: Buffer | Uint8Array): Promise<PinResult> {
  // Try Pinata first
  if (PINNING_SERVICE.PINATA_JWT) {
    return await pinFileToPinata(data);
  }
  
  // Fallback to Web3.Storage
  if (PINNING_SERVICE.WEB3_STORAGE_TOKEN) {
    return await pinFileToWeb3Storage(data);
  }
  
  throw new Error('No IPFS pinning service configured. Please set PINATA_JWT or WEB3_STORAGE_TOKEN');
}

async function pinFileToPinata(data: Buffer | Uint8Array): Promise<PinResult> {
  const formData = new FormData();
  
  // Convert data to Buffer if it's Uint8Array
  const buffer = Buffer.isBuffer(data) ? data : Buffer.from(data);
  
  // Append file - Pinata expects just 'file' field with minimal options
  formData.append('file', buffer, 'image.png');
  
  const response = await fetch(`${PINNING_SERVICE.PINATA_API_URL}/pinFileToIPFS`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${PINNING_SERVICE.PINATA_JWT}`,
      // Let FormData set Content-Type with boundary
    },
    body: formData as any,
  });
  
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Pinata API error: ${response.statusText} - ${errorText}`);
  }
  
  const result = await response.json();
  return {
    cid: `ipfs://${result.IpfsHash}`,
  };
}

async function pinFileToWeb3Storage(data: Buffer | Uint8Array): Promise<PinResult> {
  const response = await fetch(`${PINNING_SERVICE.WEB3_STORAGE_API_URL}/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${PINNING_SERVICE.WEB3_STORAGE_TOKEN}`,
      'Content-Type': 'application/octet-stream',
    },
    body: data as any,
  });
  
  if (!response.ok) {
    throw new Error(`Web3.Storage API error: ${response.statusText}`);
  }
  
  const result = await response.json();
  return {
    cid: `ipfs://${result.cid}`,
  };
}

export async function pinText(text: string): Promise<PinResult> {
  const data = Buffer.from(text, 'utf-8');
  return pinFile(data);
}

export async function pinJSON(data: any): Promise<PinResult> {
  // Convert JSON to buffer
  const jsonBuffer = Buffer.from(JSON.stringify(data), 'utf-8');
  
  // Try Pinata first
  if (PINNING_SERVICE.PINATA_JWT) {
    return await pinJSONToPinata(data);
  }
  
  // Fallback to Web3.Storage
  if (PINNING_SERVICE.WEB3_STORAGE_TOKEN) {
    return await pinFileToWeb3Storage(jsonBuffer);
  }
  
  throw new Error('No IPFS pinning service configured. Please set PINATA_JWT or WEB3_STORAGE_TOKEN');
}

async function pinJSONToPinata(data: any): Promise<PinResult> {
  const response = await fetch(`${PINNING_SERVICE.PINATA_API_URL}/pinJSONToIPFS`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${PINNING_SERVICE.PINATA_JWT}`,
    },
    body: JSON.stringify({
      pinataContent: data,
      pinataMetadata: {
        name: `shapecraft-metadata-${Date.now()}`,
        keyvalues: {
          project: 'shapecraft2',
          type: 'metadata'
        }
      }
    }),
  });
  
  if (!response.ok) {
    throw new Error(`Pinata API error: ${response.statusText}`);
  }
  
  const result = await response.json();
  return {
    cid: `ipfs://${result.IpfsHash}`,
  };
}

export async function pinFromUrl(url: string): Promise<PinResult> {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to fetch: ${response.statusText}`);
    }
    
    const data = new Uint8Array(await response.arrayBuffer());
    return pinFile(data);
  } catch (error) {
    throw new Error(`Failed to pin from URL: ${error}`);
  }
}

// Cleanup function (no-op for pinning services)
export async function shutdown() {
  // No cleanup needed for external pinning services
}
