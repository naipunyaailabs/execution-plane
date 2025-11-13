import { useEffect, useRef, useState, useCallback } from "react";
import { OBSERVABILITY_ENDPOINTS } from "@/lib/api-config";

interface MetricsUpdate {
  type: "initial" | "update" | "pong";
  timestamp?: string;
  data?: any;
}

interface ExecutionUpdate {
  type: "status_update" | "error";
  execution_id: string;
  status?: string;
  started_at?: string;
  completed_at?: string;
  execution_time?: number;
  error_message?: string;
  steps?: Array<{
    step_id: string;
    agent_id: string;
    status: string;
    started_at?: string;
    completed_at?: string;
    error_message?: string;
  }>;
  message?: string;
}

export function useObservabilityMetrics() {
  const [metrics, setMetrics] = useState<any>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    // Use observability endpoint from config
    const wsUrl = OBSERVABILITY_ENDPOINTS.METRICS_WS;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
        console.log("Observability WebSocket connected");
      };

      ws.onmessage = (event) => {
        try {
          const message: MetricsUpdate = JSON.parse(event.data);
          
          if (message.type === "initial" || message.type === "update") {
            setMetrics(message.data);
          } else if (message.type === "pong") {
            // Heartbeat response
          }
        } catch (err) {
          console.error("Error parsing WebSocket message:", err);
        }
      };

      ws.onerror = (err) => {
        console.error("WebSocket error:", err);
        setError("Connection error");
        setIsConnected(false);
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log("Observability WebSocket disconnected");
        
        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000);
      };
    } catch (err) {
      console.error("Error creating WebSocket:", err);
      setError("Failed to connect");
      setIsConnected(false);
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  const sendPing = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "ping" }));
    }
  }, []);

  useEffect(() => {
    connect();

    // Send ping every 30 seconds to keep connection alive
    const pingInterval = setInterval(sendPing, 30000);

    return () => {
      clearInterval(pingInterval);
      disconnect();
    };
  }, [connect, disconnect, sendPing]);

  return { metrics, isConnected, error, reconnect: connect };
}

export function useExecutionUpdates(executionId: string | null) {
  const [execution, setExecution] = useState<ExecutionUpdate | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!executionId) {
      return;
    }

    // Use observability endpoint from config
    const wsUrl = OBSERVABILITY_ENDPOINTS.EXECUTION_WS(executionId);

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
      };

      ws.onmessage = (event) => {
        try {
          const message: ExecutionUpdate = JSON.parse(event.data);
          setExecution(message);
          
          // Close connection if execution is complete
          if (message.status && ["completed", "failed", "cancelled"].includes(message.status)) {
            setTimeout(() => {
              ws.close();
            }, 1000);
          }
        } catch (err) {
          console.error("Error parsing execution update:", err);
        }
      };

      ws.onerror = (err) => {
        console.error("WebSocket error:", err);
        setError("Connection error");
        setIsConnected(false);
      };

      ws.onclose = () => {
        setIsConnected(false);
      };
    } catch (err) {
      console.error("Error creating WebSocket:", err);
      setError("Failed to connect");
      setIsConnected(false);
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [executionId]);

  return { execution, isConnected, error };
}

