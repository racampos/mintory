'use client';

import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Clock, Vote, ExternalLink } from 'lucide-react';
import { mcpClient } from '@/lib/mcp-client';
import { walletManager } from '@/lib/wallet';
import { formatCid, getIpfsUrl } from '@/lib/utils';
import { toast } from '@/components/ui/use-toast';
import type { ArtSet } from '@/lib/types';

interface VotingModalProps {
  isOpen: boolean;
  onClose: () => void;
  artSet?: ArtSet;
  onVote: (selectedIndex: number) => void;
}

interface VoteStatus {
  open: boolean;
  tallies: number[];
  endsAt: string;
  voteId?: string;
}

export function VotingModal({ isOpen, onClose, artSet, onVote }: VotingModalProps) {
  const [selectedArt, setSelectedArt] = useState<number>(-1);
  const [isVoting, setIsVoting] = useState(false);
  const [voteStatus, setVoteStatus] = useState<VoteStatus | null>(null);
  const [timeRemaining, setTimeRemaining] = useState<string>('');
  const [hasVoted, setHasVoted] = useState(false);

  // Mock vote ID for demonstration - would come from actual vote creation
  const mockVoteId = '0x1234567890abcdef1234567890abcdef12345678';

  useEffect(() => {
    if (isOpen && artSet) {
      fetchVoteStatus();
      const interval = setInterval(fetchVoteStatus, 5000); // Poll every 5 seconds
      return () => clearInterval(interval);
    }
  }, [isOpen, artSet]);

  useEffect(() => {
    if (voteStatus?.endsAt) {
      const interval = setInterval(updateTimeRemaining, 1000);
      return () => clearInterval(interval);
    }
  }, [voteStatus?.endsAt]);

  const fetchVoteStatus = async () => {
    try {
      const status = await mcpClient.getVoteStatus(mockVoteId);
      setVoteStatus({
        ...status,
        voteId: mockVoteId,
      });
    } catch (error) {
      console.error('Failed to fetch vote status:', error);
      // Mock data for demo
      setVoteStatus({
        open: true,
        tallies: artSet ? new Array(artSet.cids.length).fill(0) : [],
        endsAt: new Date(Date.now() + 60000).toISOString(), // 1 minute from now
        voteId: mockVoteId,
      });
    }
  };

  const updateTimeRemaining = () => {
    if (!voteStatus?.endsAt) return;

    const endTime = new Date(voteStatus.endsAt).getTime();
    const now = Date.now();
    const remaining = Math.max(0, endTime - now);

    if (remaining === 0) {
      setTimeRemaining('Vote ended');
      return;
    }

    const minutes = Math.floor(remaining / 60000);
    const seconds = Math.floor((remaining % 60000) / 1000);
    setTimeRemaining(`${minutes}:${seconds.toString().padStart(2, '0')}`);
  };

  const handleVote = async () => {
    if (selectedArt === -1 || !artSet || !walletManager) return;

    setIsVoting(true);
    try {
      // In a real implementation, this would:
      // 1. Call MCP to create a vote transaction
      // 2. Sign with wallet
      // 3. Submit to blockchain
      
      toast({
        title: 'Vote Submitted',
        description: `You voted for artwork #${selectedArt + 1}`,
      });
      
      setHasVoted(true);
      onVote(selectedArt);
      
      // Update local tallies optimistically
      if (voteStatus) {
        const newTallies = [...voteStatus.tallies];
        newTallies[selectedArt] += 1;
        setVoteStatus({
          ...voteStatus,
          tallies: newTallies,
        });
      }

    } catch (error) {
      console.error('Failed to vote:', error);
      toast({
        title: 'Vote Failed',
        description: 'Failed to submit your vote. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsVoting(false);
    }
  };

  const getTotalVotes = () => {
    return voteStatus?.tallies.reduce((sum, count) => sum + count, 0) || 0;
  };

  const getVotePercentage = (index: number) => {
    const total = getTotalVotes();
    if (total === 0) return 0;
    return Math.round((voteStatus?.tallies[index] || 0) / total * 100);
  };

  if (!artSet) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Vote className="h-5 w-5" />
            Vote for Your Favorite Artwork
          </DialogTitle>
          
          {voteStatus && (
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                {timeRemaining || 'Loading...'}
              </div>
              <Badge variant={voteStatus.open ? 'default' : 'secondary'}>
                {voteStatus.open ? 'Active' : 'Ended'}
              </Badge>
              <span>{getTotalVotes()} total votes</span>
            </div>
          )}
        </DialogHeader>

        <div className="space-y-6">
          {/* Art Grid */}
          <div className="grid grid-cols-2 gap-4">
            {artSet.cids.map((cid, index) => (
              <Card
                key={index}
                className={`cursor-pointer transition-all ${
                  selectedArt === index
                    ? 'ring-2 ring-primary ring-offset-2'
                    : 'hover:shadow-lg'
                } ${hasVoted && selectedArt !== index ? 'opacity-60' : ''}`}
                onClick={() => !hasVoted && setSelectedArt(index)}
              >
                <CardContent className="p-4">
                  <div className="aspect-square bg-muted rounded-lg mb-3 flex items-center justify-center relative overflow-hidden">
                    {artSet.thumbnails && artSet.thumbnails[index] ? (
                      <img
                        src={artSet.thumbnails[index]}
                        alt={`Artwork ${index + 1}`}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="text-center">
                        <div className="text-4xl mb-2">🎨</div>
                        <div className="text-sm text-muted-foreground">
                          Artwork #{index + 1}
                        </div>
                      </div>
                    )}
                    
                    {/* Vote Count Overlay */}
                    {voteStatus && voteStatus.tallies[index] > 0 && (
                      <div className="absolute top-2 right-2">
                        <Badge className="bg-black/70 text-white">
                          {voteStatus.tallies[index]} votes
                        </Badge>
                      </div>
                    )}

                    {/* Selected Indicator */}
                    {selectedArt === index && (
                      <div className="absolute inset-0 bg-primary/20 flex items-center justify-center">
                        <Badge className="bg-primary text-primary-foreground">
                          Selected
                        </Badge>
                      </div>
                    )}
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <h3 className="font-medium">Artwork #{index + 1}</h3>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          window.open(getIpfsUrl(cid), '_blank');
                        }}
                      >
                        <ExternalLink className="h-3 w-3" />
                      </Button>
                    </div>
                    
                    <div className="text-xs text-muted-foreground font-mono">
                      {formatCid(cid)}
                    </div>

                    {/* Vote Progress */}
                    {voteStatus && getTotalVotes() > 0 && (
                      <div className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span>{voteStatus.tallies[index]} votes</span>
                          <span>{getVotePercentage(index)}%</span>
                        </div>
                        <Progress value={getVotePercentage(index)} className="h-1" />
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Style Notes */}
          {artSet.style_notes && (
            <div className="p-4 bg-muted rounded-lg">
              <h4 className="font-medium mb-2">Artist's Notes</h4>
              <p className="text-sm text-muted-foreground">{artSet.style_notes}</p>
            </div>
          )}

          {/* Vote Actions */}
          <div className="flex items-center justify-between pt-4 border-t">
            <div className="text-sm text-muted-foreground">
              {hasVoted ? (
                'Your vote has been recorded'
              ) : selectedArt === -1 ? (
                'Select an artwork to vote'
              ) : (
                `Ready to vote for Artwork #${selectedArt + 1}`
              )}
            </div>

            <div className="flex gap-2">
              <Button variant="outline" onClick={onClose}>
                {hasVoted ? 'Close' : 'Cancel'}
              </Button>
              
              {!hasVoted && voteStatus?.open && (
                <Button
                  onClick={handleVote}
                  disabled={selectedArt === -1 || isVoting}
                >
                  {isVoting ? 'Voting...' : 'Submit Vote'}
                </Button>
              )}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
