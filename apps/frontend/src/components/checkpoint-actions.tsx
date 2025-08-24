'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { 
  CheckCircle, 
  Edit, 
  Play, 
  RefreshCw, 
  Sparkles,
  AlertTriangle,
  Vote,
  Coins
} from 'lucide-react';
import type { RunState, CheckpointAction } from '@/lib/types';
import { walletManager } from '@/lib/wallet';
import { toast } from '@/components/ui/use-toast';

interface CheckpointActionsProps {
  checkpoint: 'lore_approval' | 'art_sanity' | 'vote_tx_approval' | 'finalize_mint';
  runState: RunState;
  onAction: (action: CheckpointAction) => void;
  onShowVoting?: () => void;
}

const checkpointInfo = {
  lore_approval: {
    title: 'Lore Package Review',
    description: 'Review the historical summary and approve or request edits',
    icon: CheckCircle,
    color: 'text-blue-500',
  },
  art_sanity: {
    title: 'Art Generation Review',
    description: 'Review generated artworks and decide how to proceed',
    icon: Sparkles,
    color: 'text-purple-500',
  },
  vote_tx_approval: {
    title: 'Vote Transaction Confirmation',
    description: 'Review and confirm the blockchain vote transaction',
    icon: Vote,
    color: 'text-orange-500',
  },
  finalize_mint: {
    title: 'Finalize NFT Mint',
    description: 'Complete the minting process after voting',
    icon: Coins,
    color: 'text-green-500',
  },
} as const;

export function CheckpointActions({ 
  checkpoint, 
  runState, 
  onAction, 
  onShowVoting 
}: CheckpointActionsProps) {
  const [editText, setEditText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showEditMode, setShowEditMode] = useState(false);

  const info = checkpointInfo[checkpoint];
  const IconComponent = info.icon;

  const handleAction = async (decision: CheckpointAction['decision'], payload: any = {}) => {
    console.log('🎯 handleAction called with:', { checkpoint, decision, payload });
    setIsSubmitting(true);
    try {
      const action = {
        checkpoint,
        decision,
        payload,
      };
      console.log('📤 Calling onAction with:', action);
      await onAction(action);
      console.log('✅ onAction completed successfully');
    } catch (error) {
      console.error('❌ Action failed:', error);
    } finally {
      setIsSubmitting(false);
      if (decision === 'edit') {
        setShowEditMode(false);
        setEditText('');
      }
    }
  };

  const renderLoreApprovalActions = () => (
    <div className="space-y-4">
      {runState.lore_pack && (
        <div className="p-4 bg-muted rounded-lg">
          <h4 className="font-medium mb-2">Summary Preview</h4>
          <p className="text-sm text-muted-foreground mb-2">
            {runState.lore_pack.summary_md.slice(0, 200)}...
          </p>
          <div className="flex gap-2 text-xs text-muted-foreground">
            <span>{runState.lore_pack.bullet_facts.length} facts</span>
            <span>•</span>
            <span>{runState.lore_pack.sources.length} sources</span>
          </div>
        </div>
      )}

      {showEditMode ? (
        <div className="space-y-3">
          <Textarea
            placeholder="Describe what changes you'd like to see in the lore package..."
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            className="min-h-24"
          />
          <div className="flex gap-2">
            <Button
              onClick={() => handleAction('edit', { instructions: editText })}
              disabled={!editText.trim() || isSubmitting}
            >
              Submit Edit Request
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setShowEditMode(false);
                setEditText('');
              }}
            >
              Cancel
            </Button>
          </div>
        </div>
      ) : (
        <div className="flex gap-2">
          <Button
            onClick={() => handleAction('approve')}
            disabled={isSubmitting}
            className="flex-1"
          >
            <CheckCircle className="h-4 w-4 mr-2" />
            Approve
          </Button>
          <Button
            variant="outline"
            onClick={() => setShowEditMode(true)}
            disabled={isSubmitting}
            className="flex-1"
          >
            <Edit className="h-4 w-4 mr-2" />
            Request Edits
          </Button>
        </div>
      )}
    </div>
  );

  const renderArtSanityActions = () => (
    <div className="space-y-4">
      {runState.art_set && (
        <div className="p-4 bg-muted rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-medium">Generated Artworks</h4>
            <Badge variant="outline">
              {runState.art_set.cids.length} pieces
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground">
            {runState.art_set.style_notes}
          </p>
        </div>
      )}

      <div className="grid grid-cols-2 gap-2">
        <Button
          onClick={() => handleAction('proceed')}
          disabled={isSubmitting}
        >
          <Play className="h-4 w-4 mr-2" />
          Proceed to Vote
        </Button>
        <Button
          variant="outline"
          onClick={() => handleAction('regen')}
          disabled={isSubmitting}
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Regenerate Art
        </Button>
      </div>

      {onShowVoting && (
        <Button
          variant="secondary"
          onClick={onShowVoting}
          className="w-full"
        >
          <Vote className="h-4 w-4 mr-2" />
          Open Voting Interface
        </Button>
      )}
    </div>
  );

  const renderVoteTxApprovalActions = () => (
    <div className="space-y-4">
      {runState.vote && (
        <div className="p-4 bg-muted rounded-lg">
          <h4 className="font-medium mb-3">📊 Vote Details</h4>
          <div className="text-sm space-y-2">
            <div>
              <span className="font-medium">Vote ID:</span>{' '}
              <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                {runState.vote.id}
              </code>
            </div>
            <div>
              <span className="font-medium">Duration:</span> {runState.vote.config?.duration_s}s
            </div>
            <div>
              <span className="font-medium">Method:</span> {runState.vote.config?.method}
            </div>
            <div>
              <span className="font-medium">Gate:</span> {runState.vote.config?.gate}
            </div>
          </div>
        </div>
      )}

      {runState.prepared_tx && (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 className="font-medium mb-3 text-blue-800">🔐 Transaction Preview</h4>
          <div className="text-sm space-y-2">
            <div>
              <span className="font-medium text-blue-700">To:</span>{' '}
              <code className="text-xs bg-blue-100 px-2 py-1 rounded">
                {runState.prepared_tx.to}
              </code>
            </div>
            <div>
              <span className="font-medium text-blue-700">Value:</span>{' '}
              {runState.prepared_tx.value || '0'} ETH
            </div>
            <div>
              <span className="font-medium text-blue-700">Gas Limit:</span>{' '}
              {runState.prepared_tx.gas?.toLocaleString() || 'N/A'}
            </div>
            <div>
              <span className="font-medium text-blue-700">Data:</span>{' '}
              <code className="text-xs bg-blue-100 px-2 py-1 rounded break-all">
                {runState.prepared_tx.data?.slice(0, 42)}...
              </code>
            </div>
          </div>
        </div>
      )}

      <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
        <div className="flex items-center gap-2 text-orange-800">
          <Vote className="h-4 w-4" />
          <span className="text-sm font-medium">Ready to Sign Transaction</span>
        </div>
        <p className="text-xs text-orange-700 mt-1">
          This will create a blockchain vote with the generated art options. You'll need to sign the transaction in your wallet.
        </p>
      </div>

      <Button
        onClick={async () => {
          if (!walletManager) {
            toast({
              title: 'Wallet Not Found',
              description: 'Please connect your wallet to continue.',
              variant: 'destructive',
            });
            return;
          }

          if (!runState.prepared_tx) {
            console.error('❌ No prepared transaction available');
            toast({
              title: 'Transaction Error',
              description: 'No prepared transaction found. Please try again.',
              variant: 'destructive',
            });
            return;
          }

          try {
            console.log('🔘 Vote button clicked - sending transaction to wallet:', runState.prepared_tx);
            
            // Debug: Check current chain before sending transaction
            const currentChainId = await walletManager.getChainId();
            console.log('🔗 Current chain ID from wallet:', currentChainId);
            console.log('🎯 Expected chain ID:', 11011);
            
            if (currentChainId !== 11011) {
              console.warn('⚠️ Chain mismatch detected! Current:', currentChainId, 'Expected:', 11011);
              toast({
                title: 'Switching Network',
                description: 'Please approve the network switch to Shape Testnet',
              });
              
              try {
                await walletManager.switchToShapeTestnet();
                
                // Wait a moment for the switch to complete
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                const newChainId = await walletManager.getChainId();
                console.log('🔄 After switch, chain ID:', newChainId);
                
                if (newChainId !== 11011) {
                  throw new Error(`Chain switch failed. Expected: 11011, Got: ${newChainId}`);
                }
                
                toast({
                  title: 'Network Switched',
                  description: 'Successfully switched to Shape Testnet',
                });
              } catch (switchError) {
                console.error('❌ Failed to switch chains:', switchError);
                toast({
                  title: 'Network Switch Failed',
                  description: 'Please manually switch to Shape Testnet (Chain ID: 11011)',
                  variant: 'destructive',
                });
                throw new Error(`Wrong network. Please switch to Shape Testnet (Chain ID: 11011)`);
              }
            }
            
            // This will trigger MetaMask popup for user to sign the transaction
            const txHash = await walletManager.sendTransaction(runState.prepared_tx);
            
            console.log('✅ Transaction signed successfully:', txHash);
            toast({
              title: 'Transaction Confirmed',
              description: `Transaction signed: ${txHash.slice(0, 16)}... Waiting for confirmation...`,
            });
            
            // Wait for transaction receipt and extract vote ID
            const { txHash: confirmedTxHash, voteId } = await walletManager.waitForTransactionAndExtractVoteId(txHash);
            
            console.log('🎯 Transaction confirmed with vote ID:', { confirmedTxHash, voteId });
            
            if (voteId) {
              toast({
                title: 'Vote Created Successfully',
                description: `Vote ID: ${voteId.slice(0, 16)}... Transaction: ${confirmedTxHash.slice(0, 16)}...`,
              });
              
              // Send both tx_hash and vote_id to backend
              handleAction('confirm', { tx_hash: confirmedTxHash, vote_id: voteId });
            } else {
              toast({
                title: 'Transaction Confirmed',
                description: `Transaction: ${confirmedTxHash.slice(0, 16)}... (No vote ID extracted)`,
                variant: 'destructive',
              });
              
              // Send just tx_hash to backend (fallback)
              handleAction('confirm', { tx_hash: confirmedTxHash });
            }
          } catch (error) {
            console.error('❌ Transaction signing failed:', error);
            toast({
              title: 'Transaction Failed',
              description: error instanceof Error ? error.message : 'Failed to sign transaction',
              variant: 'destructive',
            });
          }
        }}
        disabled={isSubmitting}
        className="w-full"
        size="lg"
      >
        <Vote className="h-4 w-4 mr-2" />
        {isSubmitting ? 'Processing...' : 'Confirm & Sign Transaction'}
      </Button>
    </div>
  );

  const renderFinalizeMintActions = () => (
    <div className="space-y-4">
      {runState.vote_result && (
        <div className="p-4 bg-muted rounded-lg">
          <h4 className="font-medium mb-2">Vote Results</h4>
          <div className="text-sm text-muted-foreground">
            <div>Winner: {runState.vote_result.winner_cid.slice(0, 16)}...</div>
            <div className="mt-1">
              Total votes: {Object.values(runState.vote_result.tally).reduce((a, b) => a + b, 0)}
            </div>
          </div>
        </div>
      )}

      <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="flex items-center gap-2 text-yellow-800">
          <AlertTriangle className="h-4 w-4" />
          <span className="text-sm font-medium">Ready to Mint</span>
        </div>
        <p className="text-xs text-yellow-700 mt-1">
          This will create the NFT on the blockchain and cannot be undone.
        </p>
      </div>

      <Button
        onClick={() => handleAction('finalize')}
        disabled={isSubmitting}
        className="w-full"
        size="lg"
      >
        <Coins className="h-4 w-4 mr-2" />
        {isSubmitting ? 'Minting...' : 'Finalize Mint'}
      </Button>
    </div>
  );

  const renderActions = () => {
    switch (checkpoint) {
      case 'lore_approval':
        return renderLoreApprovalActions();
      case 'art_sanity':
        return renderArtSanityActions();
      case 'vote_tx_approval':
        return renderVoteTxApprovalActions();
      case 'finalize_mint':
        return renderFinalizeMintActions();
      default:
        return null;
    }
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <IconComponent className={`h-5 w-5 ${info.color}`} />
          {info.title}
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          {info.description}
        </p>
      </CardHeader>
      
      <CardContent>
        {renderActions()}
      </CardContent>
    </Card>
  );
}
