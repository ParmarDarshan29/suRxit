import { useEffect, useRef } from 'react';

export function useWebSocket(url, onMessage, enabled = true) {
  const ws = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  useEffect(() => {
    if (!enabled || !url) return;

    const connect = () => {
      try {
        ws.current = new WebSocket(url);
        
        ws.current.onopen = () => {
          console.log('WebSocket connected');
          reconnectAttempts.current = 0;
        };

        ws.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            onMessage(data);
          } catch (err) {
            console.error('Failed to parse WebSocket message:', err);
            onMessage(event.data);
          }
        };

        ws.current.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason);
          
          // Attempt to reconnect if not intentionally closed
          if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
            const timeout = Math.pow(2, reconnectAttempts.current) * 1000; // Exponential backoff
            reconnectTimeoutRef.current = setTimeout(() => {
              reconnectAttempts.current += 1;
              console.log(`Reconnecting... Attempt ${reconnectAttempts.current}`);
              connect();
            }, timeout);
          }
        };

        ws.current.onerror = (error) => {
          console.error('WebSocket error:', error);
        };

      } catch (err) {
        console.error('Failed to create WebSocket connection:', err);
      }
    };

    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (ws.current) {
        ws.current.close(1000, 'Component unmounting');
      }
    };
  }, [url, enabled]);

  const sendMessage = (message) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  };

  return { sendMessage };
}

export function useSSE(url, onMessage, enabled = true) {
  const eventSource = useRef(null);

  useEffect(() => {
    if (!enabled || !url) return;

    const connect = () => {
      try {
        eventSource.current = new EventSource(url);
        
        eventSource.current.onopen = () => {
          console.log('SSE connected');
        };

        eventSource.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            onMessage(data);
          } catch (err) {
            console.error('Failed to parse SSE message:', err);
            onMessage(event.data);
          }
        };

        eventSource.current.onerror = (error) => {
          console.error('SSE error:', error);
          eventSource.current.close();
          
          // Reconnect after 5 seconds
          setTimeout(() => {
            console.log('Reconnecting SSE...');
            connect();
          }, 5000);
        };

      } catch (err) {
        console.error('Failed to create SSE connection:', err);
      }
    };

    connect();

    return () => {
      if (eventSource.current) {
        eventSource.current.close();
      }
    };
  }, [url, enabled]);
}