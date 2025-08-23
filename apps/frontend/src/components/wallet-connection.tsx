'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Wallet, ChevronDown, AlertTriangle } from 'lucide-react';
import { walletManager } from '@/lib/wallet';
import { formatAddress } from '@/lib/utils';
import { toast } from '@/components/ui/use-toast';

interface WalletConnectionProps {
  onConnect: (address: string) => void;
}

export function WalletConnection({ onConnect }: WalletConnectionProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [address, setAddress] = useState<string>('');
  const [chainId, setChainId] = useState<number>(0);
  const [isConnecting, setIsConnecting] = useState(false);
  const [wrongNetwork, setWrongNetwork] = useState(false);

  useEffect(() => {
    checkConnection();
  }, []);

  const checkConnection = async () => {
    if (!walletManager || !window.ethereum) return;

    try {
      const accounts = await window.ethereum.request({ method: 'eth_accounts' });
      const currentChainId = await walletManager.getChainId();
      
      if (accounts.length > 0) {
        setAddress(accounts[0]);
        setIsConnected(true);
        setChainId(currentChainId);
        setWrongNetwork(currentChainId !== 360); // Shape testnet
        onConnect(accounts[0]);
      }
    } catch (error) {
      console.error('Failed to check wallet connection:', error);
    }
  };

  const connectWallet = async () => {
    if (!walletManager) {
      toast({
        title: 'Wallet Not Found',
        description: 'Please install MetaMask or another Web3 wallet.',
        variant: 'destructive',
      });
      return;
    }

    setIsConnecting(true);
    try {
      const accounts = await walletManager.connect();
      const currentChainId = await walletManager.getChainId();
      
      setAddress(accounts[0]);
      setIsConnected(true);
      setChainId(currentChainId);
      setWrongNetwork(currentChainId !== 360);
      onConnect(accounts[0]);

      toast({
        title: 'Wallet Connected',
        description: `Connected to ${formatAddress(accounts[0])}`,
      });
    } catch (error) {
      console.error('Failed to connect wallet:', error);
      toast({
        title: 'Connection Failed',
        description: 'Failed to connect to wallet. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsConnecting(false);
    }
  };

  const switchToShapeTestnet = async () => {
    if (!walletManager) return;

    try {
      await walletManager.switchToShapeTestnet();
      const currentChainId = await walletManager.getChainId();
      setChainId(currentChainId);
      setWrongNetwork(currentChainId !== 360);

      toast({
        title: 'Network Switched',
        description: 'Successfully switched to Shape Testnet',
      });
    } catch (error) {
      console.error('Failed to switch network:', error);
      toast({
        title: 'Network Switch Failed',
        description: 'Failed to switch to Shape Testnet',
        variant: 'destructive',
      });
    }
  };

  const disconnect = () => {
    setIsConnected(false);
    setAddress('');
    setChainId(0);
    setWrongNetwork(false);
    onConnect('');
  };

  // Listen for account/chain changes
  useEffect(() => {
    if (!window.ethereum) return;

    const handleAccountsChanged = (accounts: string[]) => {
      if (accounts.length === 0) {
        disconnect();
      } else {
        setAddress(accounts[0]);
        onConnect(accounts[0]);
      }
    };

    const handleChainChanged = (chainIdHex: string) => {
      const newChainId = parseInt(chainIdHex, 16);
      setChainId(newChainId);
      setWrongNetwork(newChainId !== 360);
    };

    window.ethereum.on('accountsChanged', handleAccountsChanged);
    window.ethereum.on('chainChanged', handleChainChanged);

    return () => {
      window.ethereum?.removeListener('accountsChanged', handleAccountsChanged);
      window.ethereum?.removeListener('chainChanged', handleChainChanged);
    };
  }, []);

  if (!isConnected) {
    return (
      <Button onClick={connectWallet} disabled={isConnecting}>
        <Wallet className="h-4 w-4 mr-2" />
        {isConnecting ? 'Connecting...' : 'Connect Wallet'}
      </Button>
    );
  }

  return (
    <div className="flex items-center gap-2">
      {wrongNetwork && (
        <Button
          onClick={switchToShapeTestnet}
          variant="outline"
          size="sm"
          className="text-yellow-600 border-yellow-600 hover:bg-yellow-50"
        >
          <AlertTriangle className="h-4 w-4 mr-2" />
          Wrong Network
        </Button>
      )}

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline">
            <Wallet className="h-4 w-4 mr-2" />
            <span className="mr-2">{formatAddress(address)}</span>
            <ChevronDown className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-64">
          <div className="p-2">
            <div className="text-sm font-medium mb-1">Connected Account</div>
            <div className="text-xs text-muted-foreground font-mono">{address}</div>
          </div>
          
          <div className="p-2 border-t">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm">Network</span>
              <Badge variant={wrongNetwork ? 'destructive' : 'default'}>
                {chainId === 360 ? 'Shape Testnet' : `Chain ${chainId}`}
              </Badge>
            </div>
            
            {wrongNetwork && (
              <Button
                onClick={switchToShapeTestnet}
                size="sm"
                variant="outline"
                className="w-full mb-2"
              >
                Switch to Shape Testnet
              </Button>
            )}
          </div>
          
          <DropdownMenuItem onClick={disconnect} className="text-red-600">
            Disconnect Wallet
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
