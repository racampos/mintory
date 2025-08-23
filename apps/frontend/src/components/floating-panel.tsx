'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Coins, Trophy, ExternalLink, RefreshCw } from 'lucide-react';
import { mcpClient } from '@/lib/mcp-client';
import { formatAddress } from '@/lib/utils';
import type { GasbackInfo, MedalInfo } from '@/lib/types';

interface FloatingPanelProps {
  connectedAddress: string;
}

export function FloatingPanel({ connectedAddress }: FloatingPanelProps) {
  const [gasbackInfo, setGasbackInfo] = useState<GasbackInfo | null>(null);
  const [medalInfo, setMedalInfo] = useState<MedalInfo | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [isExpanded, setIsExpanded] = useState(false);

  // Mock contract address for gasback - replace with actual contract
  const mockContractAddress = '0x742d35Cc67C0532c6B0Ce1d0C8e4E2c2bDF9f000';

  useEffect(() => {
    if (connectedAddress) {
      fetchUserData();
    } else {
      setGasbackInfo(null);
      setMedalInfo(null);
    }
  }, [connectedAddress]);

  const fetchUserData = async () => {
    if (!connectedAddress) return;

    setIsLoading(true);
    setError('');

    try {
      const [gasback, medals] = await Promise.all([
        mcpClient.getGasbackInfo(mockContractAddress),
        mcpClient.getMedalsOf(connectedAddress),
      ]);

      setGasbackInfo(gasback);
      setMedalInfo(medals);
    } catch (err) {
      console.error('Failed to fetch user data:', err);
      setError('Failed to load user data');
    } finally {
      setIsLoading(false);
    }
  };

  const formatGasback = (value: string) => {
    // Convert wei to ETH for display
    const wei = BigInt(value || '0');
    const eth = Number(wei) / 1e18;
    return eth.toFixed(6);
  };

  if (!connectedAddress) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <Card className="w-80 shadow-lg border-2">
        <CardHeader 
          className="pb-2 cursor-pointer"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <CardTitle className="text-base flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Coins className="h-4 w-4" />
              My Status
            </span>
            <Button variant="ghost" size="sm" onClick={(e) => {
              e.stopPropagation();
              fetchUserData();
            }}>
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
          </CardTitle>
          <div className="text-xs text-muted-foreground">
            {formatAddress(connectedAddress)}
          </div>
        </CardHeader>

        {isExpanded && (
          <CardContent className="space-y-4">
            {error ? (
              <div className="text-sm text-red-500 p-2 bg-red-50 rounded">
                {error}
              </div>
            ) : (
              <>
                {/* Gasback Section */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Coins className="h-4 w-4" />
                    <span className="text-sm font-medium">Gasback Rewards</span>
                  </div>
                  
                  {gasbackInfo ? (
                    <div className="grid grid-cols-2 gap-2">
                      <div className="p-2 bg-muted rounded text-center">
                        <div className="text-xs text-muted-foreground">Accrued</div>
                        <div className="text-sm font-mono">
                          {formatGasback(gasbackInfo.accrued)} ETH
                        </div>
                      </div>
                      <div className="p-2 bg-muted rounded text-center">
                        <div className="text-xs text-muted-foreground">Claimable</div>
                        <div className="text-sm font-mono">
                          {formatGasback(gasbackInfo.claimable)} ETH
                        </div>
                      </div>
                    </div>
                  ) : isLoading ? (
                    <div className="p-2 bg-muted rounded text-center text-sm">
                      Loading...
                    </div>
                  ) : null}
                </div>

                <Separator />

                {/* Medals Section */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Trophy className="h-4 w-4" />
                    <span className="text-sm font-medium">Medals</span>
                  </div>
                  
                  {medalInfo ? (
                    <div className="space-y-2">
                      {medalInfo.medals.length > 0 ? (
                        medalInfo.medals.map((medal) => (
                          <div key={medal.id} className="flex items-center justify-between p-2 bg-muted rounded">
                            <div className="flex items-center gap-2">
                              <Badge variant="outline" className="text-xs">
                                #{medal.id}
                              </Badge>
                              <span className="text-sm">Historian Medal</span>
                            </div>
                            <span className="text-sm font-mono">×{medal.balance}</span>
                          </div>
                        ))
                      ) : (
                        <div className="p-2 bg-muted rounded text-center text-sm text-muted-foreground">
                          No medals yet
                        </div>
                      )}
                    </div>
                  ) : isLoading ? (
                    <div className="p-2 bg-muted rounded text-center text-sm">
                      Loading...
                    </div>
                  ) : null}
                </div>

                {/* Quick Links */}
                <Separator />
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1"
                    onClick={() => window.open('https://explorer.shape.network', '_blank')}
                  >
                    <ExternalLink className="h-3 w-3 mr-1" />
                    Explorer
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1"
                    onClick={() => window.open('https://docs.shape.network', '_blank')}
                  >
                    <ExternalLink className="h-3 w-3 mr-1" />
                    Docs
                  </Button>
                </div>
              </>
            )}
          </CardContent>
        )}
      </Card>
    </div>
  );
}
