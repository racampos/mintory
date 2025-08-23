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

interface CheckpointActionsProps {
  checkpoint: 'lore_approval' | 'art_sanity' | 'finalize_mint';
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
    setIsSubmitting(true);
    try {
      await onAction({
        checkpoint,
        decision,
        payload,
      });
    } catch (error) {
      console.error('Action failed:', error);
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
