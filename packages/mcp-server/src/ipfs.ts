import { createHelia } from 'helia';
import { unixfs } from '@helia/unixfs';
import { json } from '@helia/json';
import { MemoryBlockstore } from 'blockstore-core';
import { MemoryDatastore } from 'datastore-core';
import { fromString as uint8ArrayFromString } from 'uint8arrays/from-string';
import type { PinResult } from './types.js';

// Create IPFS node
let helia: Awaited<ReturnType<typeof createHelia>> | null = null;
let fs: ReturnType<typeof unixfs> | null = null;
let jsonIpfs: ReturnType<typeof json> | null = null;

async function getIPFS() {
  if (!helia || !fs || !jsonIpfs) {
    helia = await createHelia({
      blockstore: new MemoryBlockstore(),
      datastore: new MemoryDatastore(),
    });
    fs = unixfs(helia);
    jsonIpfs = json(helia);
  }
  return { helia, fs, jsonIpfs };
}

export async function pinFile(data: Buffer | Uint8Array): Promise<PinResult> {
  const { fs } = await getIPFS();
  
  const cid = await fs.addBytes(data);
  return {
    cid: `ipfs://${cid.toString()}`,
  };
}

export async function pinText(text: string): Promise<PinResult> {
  const data = uint8ArrayFromString(text);
  return pinFile(data);
}

export async function pinJSON(data: any): Promise<PinResult> {
  const { jsonIpfs } = await getIPFS();
  
  const cid = await jsonIpfs.add(data);
  return {
    cid: `ipfs://${cid.toString()}`,
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

// Cleanup function
export async function shutdown() {
  if (helia) {
    await helia.stop();
    helia = null;
    fs = null;
    jsonIpfs = null;
  }
}
