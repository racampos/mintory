'use client';

import { useState } from 'react';
import { CuratorChat } from '@/components/curator-chat';
import { AgentConsole } from '@/components/agent-console';
import { WalletConnection } from '@/components/wallet-connection';
import { VotingModal } from '@/components/voting-modal';
import { CheckpointActions } from '@/components/checkpoint-actions';
import type { RunState, StreamUpdate } from '@/lib/types';

export default function Home() {
  const [runState, setRunState] = useState<RunState | null>(null);
  const [updates, setUpdates] = useState<StreamUpdate[]>([]);
  const [showVotingModal, setShowVotingModal] = useState(false);

  const handleRunStart = (newRunState: RunState) => {
    setRunState(newRunState);
    setUpdates([]);
  };

  const handleUpdate = (update: StreamUpdate) => {
    setUpdates(prev => {
      // Filter out empty messages (used for state-only updates)
      if (!update.message.trim()) {
        console.log(`🔄 State-only update (no UI message)`);
        // Don't add to UI, but still process state_delta below
        return prev;
      }
      
      // Smart deduplication: Check if this exact message already exists
      const isDuplicate = prev.some(existingUpdate => 
        existingUpdate.agent === update.agent && 
        existingUpdate.message === update.message &&
        existingUpdate.level === update.level
      );
      
      if (isDuplicate) {
        console.log(`🚫 Deduped: ${update.agent} - "${update.message.slice(0, 50)}..."`);
        return prev; // Don't add duplicate
      }
      
      console.log(`✅ New: ${update.agent} - "${update.message.slice(0, 50)}..."`);
      return [...prev, update];
    });
    
    // Always process state_delta regardless of message deduplication
    if (update.state_delta) {
      setRunState(prev => prev ? { ...prev, ...update.state_delta } : null);
    }
  };

  const handleCheckpointAction = async (action: any) => {
    console.log('🎬 handleCheckpointAction called with:', action);
    if (!runState) {
      console.log('❌ No runState available, cannot proceed');
      return;
    }

    // 🚀 IMMEDIATE UI FIX: Clear checkpoint instantly for better UX
    console.log('🚀 Immediately clearing checkpoint UI for instant feedback');
    setRunState(prev => prev ? { ...prev, checkpoint: null } : null);

    try {
      console.log('🌐 Making request to:', `/api/orchestrator/runs/${runState.run_id}/resume`);
      const response = await fetch(`/api/orchestrator/runs/${runState.run_id}/resume`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(action),
      });

      console.log('📡 Response status:', response.status, response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Response error:', errorText);
        throw new Error(`Failed to resume run: ${response.statusText} - ${errorText}`);
      }

      const result = await response.text();
      console.log('✅ Resume successful, response:', result);

      // 🔄 CRITICAL FIX: Refresh runState after successful checkpoint action
      try {
        console.log('🔄 Fetching updated runState after checkpoint action...');
        
        // Add a small delay to ensure backend state is updated
        await new Promise(resolve => setTimeout(resolve, 100));
        
        const stateResponse = await fetch(`/api/orchestrator/runs/${runState.run_id}`);
        if (stateResponse.ok) {
          const updatedState = await stateResponse.json();
          console.log('✅ Updated state fetched:', { 
            before_checkpoint: runState.checkpoint, 
            after_checkpoint: updatedState.checkpoint, 
            keys: Object.keys(updatedState) 
          });
          
          // Force update the state immediately to hide checkpoint UI
          setRunState(updatedState);
          
          // Double-check: if checkpoint is still there, force clear it locally
          if (updatedState.checkpoint === action.checkpoint) {
            console.warn('⚠️ Backend still has checkpoint, forcing local clear');
            setRunState(prev => prev ? { ...prev, checkpoint: null } : null);
          }
        } else {
          console.warn('⚠️ Failed to fetch updated state, but action succeeded');
          // Fallback: force clear checkpoint locally
          console.log('🔧 Fallback: Clearing checkpoint locally');
          setRunState(prev => prev ? { ...prev, checkpoint: null } : null);
        }
      } catch (stateError) {
        console.warn('⚠️ Failed to refresh state after action, but action succeeded:', stateError);
        // Fallback: force clear checkpoint locally
        console.log('🔧 Fallback: Clearing checkpoint locally');
        setRunState(prev => prev ? { ...prev, checkpoint: null } : null);
      }

    } catch (error) {
      console.error('❌ Failed to perform checkpoint action:', error);
    }
  };

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="flex h-16 items-center justify-between px-6">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-bold">Mintory: Make History Mintable</h1>
            {runState && (
              <div className="text-sm text-muted-foreground">
                Run: {runState.run_id.slice(0, 8)}...
              </div>
            )}
          </div>
          <WalletConnection onConnect={() => {}} />
        </div>
      </header>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-4rem)]">
        {/* Left Panel - Curator Chat */}
        <div className="w-1/2 border-r border-border">
          <CuratorChat onRunStart={handleRunStart} />
        </div>

        {/* Right Panel - Agent Console */}
        <div className="w-1/2 flex flex-col">
          <AgentConsole 
            runState={runState}
            updates={updates}
            onUpdate={handleUpdate}
          />
          
          {/* Checkpoint Actions */}
          {runState?.checkpoint && (
            <div className="border-t border-border p-4">
              <CheckpointActions
                checkpoint={runState.checkpoint}
                runState={runState}
                onAction={handleCheckpointAction}
                onShowVoting={() => setShowVotingModal(true)}
              />
            </div>
          )}
        </div>
      </div>

      {/* Voting Modal */}
      <VotingModal
        isOpen={showVotingModal}
        onClose={() => setShowVotingModal(false)}
        artSet={runState?.art_set}
        onVote={() => {/* Handle vote */}}
      />
    </main>
  );
}
