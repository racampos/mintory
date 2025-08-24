'use client';

import { useState } from 'react';
import { useChat } from 'ai/react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Send, Bot, User, Coins, Trophy } from 'lucide-react';
import type { RunState } from '@/lib/types';

interface CuratorChatProps {
  onRunStart: (runState: RunState) => void;
}

export function CuratorChat({ onRunStart }: CuratorChatProps) {
  const [dateInput, setDateInput] = useState('');
  const [isStartingRun, setIsStartingRun] = useState(false);

  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/chat',
  });

  const startNewRun = async () => {
    if (!dateInput.trim()) return;

    setIsStartingRun(true);
    try {
      const response = await fetch('/api/orchestrator/runs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date_label: dateInput }),
      });

      if (!response.ok) {
        throw new Error(`Failed to start run: ${response.statusText}`);
      }

      const { run_id } = await response.json();
      
      const runState: RunState = {
        run_id,
        date_label: dateInput,
        status: 'running',
      };

      onRunStart(runState);
      setDateInput('');
    } catch (error) {
      console.error('Failed to start run:', error);
    } finally {
      setIsStartingRun(false);
    }
  };

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b border-border p-4">
        <h2 className="text-lg font-semibold">AI Curator</h2>
        <p className="text-sm text-muted-foreground">
          Ask questions about blockchain data, gasback, or start a new creation run
        </p>
      </div>

      {/* Start Run Section */}
      <Card className="m-4">
        <CardHeader>
          <CardTitle className="text-base">Start New Creation Run</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input
              placeholder="Enter date label (e.g., '2015-07-30 — Ethereum Genesis Block')"
              value={dateInput}
              onChange={(e) => setDateInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && startNewRun()}
            />
            <Button 
              onClick={startNewRun}
              disabled={!dateInput.trim() || isStartingRun}
            >
              {isStartingRun ? '...' : 'Start'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Chat Messages */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-muted-foreground'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  {message.role === 'user' ? (
                    <User className="h-4 w-4" />
                  ) : (
                    <Bot className="h-4 w-4" />
                  )}
                  <span className="text-xs font-medium">
                    {message.role === 'user' ? 'You' : 'Curator'}
                  </span>
                </div>
                <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                
                {/* Tool Call Indicators (optional - shows which tools were used) */}
                {message.toolInvocations && message.toolInvocations.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {message.toolInvocations.map((toolInvocation) => (
                      <Badge key={toolInvocation.toolCallId} variant="outline" className="text-xs">
                        {toolInvocation.toolName}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-muted text-muted-foreground rounded-lg p-3">
                <div className="flex items-center gap-2">
                  <Bot className="h-4 w-4" />
                  <span className="text-xs">Curator is typing...</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Chat Input */}
      <form onSubmit={handleSubmit} className="border-t border-border p-4">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={handleInputChange}
            placeholder="Ask about gasback, medals, chain info, or anything else..."
            disabled={isLoading}
          />
          <Button type="submit" size="icon" disabled={isLoading || !input.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
        
        <div className="flex gap-2 mt-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => handleInputChange({ target: { value: 'What is the current chain info?' } } as any)}
          >
            <Coins className="h-3 w-3 mr-1" />
            Chain Info
          </Button>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => handleInputChange({ target: { value: 'Check my medals and gasback' } } as any)}
          >
            <Trophy className="h-3 w-3 mr-1" />
            My Status
          </Button>
        </div>
      </form>
    </div>
  );
}
