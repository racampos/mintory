'use client';

import { useEffect, useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Bot, 
  CheckCircle, 
  AlertCircle, 
  Info, 
  Clock,
  ExternalLink,
  Palette,
  Vote,
  Coins
} from 'lucide-react';
import { cn } from '@/lib/utils';
import type { RunState, StreamUpdate } from '@/lib/types';

interface AgentConsoleProps {
  runState: RunState | null;
  updates: StreamUpdate[];
  onUpdate: (update: StreamUpdate) => void;
}

const agentEmojis = {
  lore: '📚',
  artist: '🎨',
  vote: '🗳️',
  mint: '💎',
  guard: '🛡️',
} as const;

const levelIcons = {
  info: Info,
  success: CheckCircle,
  warning: AlertCircle,
  error: AlertCircle,
} as const;

const levelColors = {
  info: 'text-blue-500',
  success: 'text-green-500',
  warning: 'text-yellow-500',
  error: 'text-red-500',
} as const;

export function AgentConsole({ runState, updates, onUpdate }: AgentConsoleProps) {
  const [eventSource, setEventSource] = useState<EventSource | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  // Auto-scroll to bottom when new updates arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [updates]);

  // Setup EventSource connection when run starts
  useEffect(() => {
    if (!runState?.run_id) {
      if (eventSource) {
        eventSource.close();
        setEventSource(null);
      }
      return;
    }

    const connectToStream = () => {
      const es = new EventSource(
        `/api/orchestrator/runs/${runState.run_id}/stream`
      );

      // Handle different event types from the backend
      es.addEventListener('update', (event) => {
        try {
          const messageData = JSON.parse(event.data);
          const update: StreamUpdate = {
            agent: messageData.agent,
            level: messageData.level,
            message: messageData.message,
            links: messageData.links?.map((link: any) => link.href) || [],
            timestamp: new Date().toISOString()
          };
          console.log('Received update event:', update);
          onUpdate(update);
        } catch (error) {
          console.error('Failed to parse update event:', error);
        }
      });

      es.addEventListener('state', (event) => {
        try {
          const stateData = JSON.parse(event.data);
          console.log('Received state event:', stateData);
          
          // Update the run state with the new data
          if (stateData.state_update) {
            const stateUpdate: StreamUpdate = {
              agent: 'System',
              level: 'info',
              message: 'State updated',
              state_delta: stateData.state_update,
              timestamp: new Date().toISOString()
            };
            onUpdate(stateUpdate);
          }
        } catch (error) {
          console.error('Failed to parse state event:', error);
        }
      });

      es.addEventListener('complete', (event) => {
        try {
          const completeData = JSON.parse(event.data);
          console.log('Workflow completed:', completeData);
          
          const update: StreamUpdate = {
            agent: 'System',
            level: 'success',
            message: 'Workflow completed successfully!',
            timestamp: new Date().toISOString()
          };
          onUpdate(update);
          
          // Close the EventSource connection when workflow is complete
          console.log('Closing EventSource connection - workflow complete');
          es.close();
          setEventSource(null);
        } catch (error) {
          console.error('Failed to parse complete event:', error);
        }
      });

      es.addEventListener('error', (event) => {
        try {
          // Only try to parse if there's actual data (custom backend error)
          if (event.data && event.data !== 'undefined') {
            const errorData = JSON.parse(event.data);
            console.error('Received custom backend error event:', errorData);
            
            const update: StreamUpdate = {
              agent: 'System',
              level: 'error',
              message: `Error: ${errorData.error}`,
              timestamp: new Date().toISOString()
            };
            onUpdate(update);
            
            // Close connection on custom backend error
            console.log('Closing EventSource connection - backend error received');
            es.close();
            setEventSource(null);
          } else {
            // This is a native browser error event, let es.onerror handle it
            console.log('Ignoring native browser error event (no data), es.onerror will handle connection issues');
          }
        } catch (error) {
          console.error('Failed to parse error event:', error);
        }
      });

      // Keep the default onmessage as fallback
      es.onmessage = (event) => {
        console.log('Received default message event:', event.data);
        try {
          const update: StreamUpdate = JSON.parse(event.data);
          update.timestamp = new Date().toISOString();
          onUpdate(update);
        } catch (error) {
          console.error('Failed to parse default message:', error);
        }
      };

      es.onerror = (error) => {
        console.error('EventSource connection error:', error);
        
        // Only reconnect if the EventSource is still in a connecting/open state
        // Don't reconnect if we explicitly closed it (completed/error workflows)
        if (eventSource && es.readyState !== EventSource.CLOSED) {
          console.log('Attempting to reconnect EventSource...');
          // Implement exponential backoff reconnection
          const delay = Math.min(1000 * Math.pow(2, 1), 10000); // Max 10s
          
          reconnectTimeoutRef.current = setTimeout(() => {
            if (eventSource && es.readyState === EventSource.CLOSED) {
              connectToStream();
            }
          }, delay);
        } else {
          console.log('EventSource was explicitly closed, not reconnecting');
        }
      };

      es.onopen = () => {
        console.log('EventSource connected');
      };

      setEventSource(es);
    };

    connectToStream();

    return () => {
      if (eventSource) {
        eventSource.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [runState?.run_id]);

  const getAgentEmoji = (agent: string) => {
    return agentEmojis[agent as keyof typeof agentEmojis] || '🤖';
  };

  const getLevelIcon = (level: string) => {
    const IconComponent = levelIcons[level as keyof typeof levelIcons] || Info;
    return IconComponent;
  };

  const getLevelColor = (level: string) => {
    return levelColors[level as keyof typeof levelColors] || 'text-gray-500';
  };

  const renderRunStateInfo = () => {
    if (!runState) {
      return (
        <div className="text-center text-muted-foreground p-8">
          <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-medium mb-2">No Active Run</h3>
          <p className="text-sm">Start a new creation run from the Curator chat to see the agent console in action.</p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Current Run
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Date Label:</span>
              <span className="text-sm font-medium">{runState.date_label}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Status:</span>
              <Badge variant={runState.status === 'completed' ? 'default' : 'secondary'}>
                {runState.status}
              </Badge>
            </div>
            {runState.current_agent && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Current Agent:</span>
                <Badge variant="outline">
                  {getAgentEmoji(runState.current_agent)} {runState.current_agent}
                </Badge>
              </div>
            )}
            {runState.checkpoint && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Checkpoint:</span>
                <Badge variant="destructive">
                  {runState.checkpoint}
                </Badge>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Lore Pack Preview */}
        {runState.lore_pack && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                📚 Lore Pack
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm">{runState.lore_pack.summary_md.slice(0, 200)}...</p>
              <div className="mt-2 text-xs text-muted-foreground">
                {runState.lore_pack.sources.length} sources • {runState.lore_pack.bullet_facts.length} facts
              </div>
            </CardContent>
          </Card>
        )}

        {/* Art Set Preview */}
        {runState.art_set && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Palette className="h-4 w-4" />
                Art Set
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-2 mb-2">
                {runState.art_set.cids.slice(0, 4).map((cid, i) => (
                  <div key={i} className="aspect-square bg-muted rounded border flex items-center justify-center text-xs">
                    Art #{i + 1}
                  </div>
                ))}
              </div>
              <div className="text-xs text-muted-foreground">
                {runState.art_set.cids.length} artworks generated
              </div>
            </CardContent>
          </Card>
        )}

        {/* Vote Result */}
        {runState.vote_result && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Vote className="h-4 w-4" />
                Vote Result
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm">
                <div className="font-medium">Winner: {runState.vote_result.winner_cid.slice(0, 12)}...</div>
                <div className="text-muted-foreground mt-1">
                  Total votes: {Object.values(runState.vote_result.tally).reduce((a, b) => a + b, 0)}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Mint Receipt */}
        {runState.mint_receipt && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Coins className="h-4 w-4" />
                Mint Receipt
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Token ID:</span>
                  <span className="text-sm font-mono">{runState.mint_receipt.token_id}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">TX Hash:</span>
                  <Button variant="ghost" size="sm" className="h-auto p-0">
                    <span className="text-sm font-mono">{runState.mint_receipt.tx_hash.slice(0, 12)}...</span>
                    <ExternalLink className="h-3 w-3 ml-1" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    );
  };

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b border-border p-4">
        <h2 className="text-lg font-semibold">Agent Console</h2>
        <p className="text-sm text-muted-foreground">
          Real-time updates from the orchestration system
        </p>
      </div>

      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        {renderRunStateInfo()}

        {/* Updates Timeline */}
        {updates.length > 0 && (
          <div className="mt-6 space-y-3">
            <h3 className="text-sm font-medium text-muted-foreground mb-3">Activity Timeline</h3>
            {updates.map((update, index) => {
              const IconComponent = getLevelIcon(update.level);
              return (
                <Card key={index} className="border-l-4 border-l-primary/20">
                  <CardContent className="p-3">
                    <div className="flex items-start gap-3">
                      <div className={cn('mt-0.5', getLevelColor(update.level))}>
                        <IconComponent className="h-4 w-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant="outline" className="text-xs">
                            {getAgentEmoji(update.agent)} {update.agent}
                          </Badge>
                          {update.timestamp && (
                            <span className="text-xs text-muted-foreground">
                              {new Date(update.timestamp).toLocaleTimeString()}
                            </span>
                          )}
                        </div>
                        <p className="text-sm">{update.message}</p>
                        
                        {/* Links */}
                        {update.links && update.links.length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-1">
                            {update.links.map((link, i) => (
                              <Button
                                key={i}
                                variant="ghost"
                                size="sm"
                                className="h-auto p-1 text-xs"
                                onClick={() => window.open(link, '_blank')}
                              >
                                <ExternalLink className="h-3 w-3 mr-1" />
                                Link
                              </Button>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
