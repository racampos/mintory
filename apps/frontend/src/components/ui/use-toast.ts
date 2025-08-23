// Simple toast hook for demo purposes
// In a production app, you'd want to use a proper toast library like sonner

import { useState, useCallback } from 'react';

interface ToastProps {
  title: string;
  description?: string;
  variant?: 'default' | 'destructive';
}

let toastCount = 0;

export function toast({ title, description, variant = 'default' }: ToastProps) {
  // Simple browser toast implementation
  // In production, replace with proper toast system
  
  if ('Notification' in window) {
    if (Notification.permission === 'granted') {
      new Notification(title, {
        body: description,
        icon: variant === 'destructive' ? '❌' : '✅',
      });
    } else if (Notification.permission !== 'denied') {
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          new Notification(title, {
            body: description,
            icon: variant === 'destructive' ? '❌' : '✅',
          });
        }
      });
    }
  }
  
  // Fallback to console for development
  console.log(`[Toast] ${title}${description ? `: ${description}` : ''}`);
}

export function useToast() {
  return {
    toast,
  };
}
