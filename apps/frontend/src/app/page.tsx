'use client';

import { useState } from 'react';
import { CuratorChat } from '@/components/curator-chat';
import { AgentConsole } from '@/components/agent-console';
import { FloatingPanel } from '@/components/floating-panel';
import { WalletConnection } from '@/components/wallet-connection';
import { VotingModal } from '@/components/voting-modal';
import { CheckpointActions } from '@/components/checkpoint-actions';
import type { RunState, StreamUpdate } from '@/lib/types';

export default function Home() {
  const [runState, setRunState] = useState<RunState | null>(null);
  const [updates, setUpdates] = useState<StreamUpdate[]>([]);
  const [showVotingModal, setShowVotingModal] = useState(false);
  const [connectedAddress, setConnectedAddress] = useState<string>('');

  const handleRunStart = (newRunState: RunState) => {
    setRunState(newRunState);
    setUpdates([]);
  };

  const handleUpdate = (update: StreamUpdate) => {
    setUpdates(prev => [...prev, update]);
    if (update.state_delta) {
      setRunState(prev => prev ? { ...prev, ...update.state_delta } : null);
    }
  };

  const handleCheckpointAction = async (action: any) => {
    if (!runState) return;

    try {
      const response = await fetch(`/api/orchestrator/runs/${runState.run_id}/resume`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(action),
      });

      if (!response.ok) {
        throw new Error(`Failed to resume run: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Failed to perform checkpoint action:', error);
    }
  };

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="flex h-16 items-center justify-between px-6">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-bold">Shapecraft Curator</h1>
            {runState && (
              <div className="text-sm text-muted-foreground">
                Run: {runState.run_id.slice(0, 8)}...
              </div>
            )}
          </div>
          <WalletConnection onConnect={setConnectedAddress} />
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

      {/* Floating Panel */}
      <FloatingPanel connectedAddress={connectedAddress} />

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
