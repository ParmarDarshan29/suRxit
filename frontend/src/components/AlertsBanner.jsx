import React, { useState } from 'react';
import { useWebSocket, useSSE } from '../hooks/useRealtime';

/**
 * AlertsBanner
 * Listens to /alerts/stream (SSE or WebSocket) and shows real-time alerts as a banner.
 */
export default function AlertsBanner() {
  const [alert, setAlert] = useState(null);
  const [dismissed, setDismissed] = useState(false);
  
  const alertUrl = import.meta.env.VITE_ALERTS_STREAM_URL;
  const enabled = !!alertUrl && !import.meta.env.VITE_ENABLE_MOCK_DATA;
  const isWebSocket = alertUrl?.startsWith('ws');

  // Handle incoming alert messages
  const handleMessage = (data) => {
    const message = typeof data === 'string' ? data : data.message || JSON.stringify(data);
    setAlert(message);
    setDismissed(false);
  };

  // Always call hooks at top level - use enabled flag to control behavior
  useWebSocket(isWebSocket ? alertUrl : null, handleMessage, enabled && isWebSocket);
  useSSE(!isWebSocket ? alertUrl : null, handleMessage, enabled && !isWebSocket);

  if (!alert || dismissed) return null;

  return (
    <div className="fixed top-0 left-0 w-full z-50 bg-yellow-400 text-black text-center py-2 font-semibold shadow">
      <div className="flex items-center justify-center gap-2">
        <span className="mr-2">⚠️</span> 
        <span className="flex-1">{alert}</span>
        <button 
          onClick={() => setDismissed(true)}
          className="ml-2 px-2 py-1 text-sm bg-yellow-500 hover:bg-yellow-600 rounded"
          aria-label="Dismiss alert"
        >
          ×
        </button>
      </div>
    </div>
  );
}
