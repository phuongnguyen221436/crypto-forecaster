import { useEffect, useMemo, useRef, useState } from 'react';

export interface TradeEvent {
  id: string;
  ts: number;
  price: number;
  qty: number;
  side: 'buy' | 'sell';
}

type ConnectionState = 'connecting' | 'open' | 'closed' | 'error';

interface UseTradeStreamOptions {
  bufferSize?: number;
  endpoint?: string;
}

const DEFAULT_BUFFER = 200;

const resolveEndpoint = (endpoint?: string) => {
  if (endpoint) {
    return endpoint;
  }

  const envEndpoint = import.meta.env?.VITE_TRADES_WS as string | undefined;
  if (envEndpoint) {
    return envEndpoint;
  }

  if (typeof window === 'undefined') {
    return 'ws://localhost:8000/ws/trades';
  }

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const hostname = window.location.hostname;

  return `${protocol}//${hostname}:8000/ws/trades`;
};

export const useTradeStream = ({ bufferSize = DEFAULT_BUFFER, endpoint }: UseTradeStreamOptions = {}) => {
  const [trades, setTrades] = useState<TradeEvent[]>([]);
  const [status, setStatus] = useState<ConnectionState>('connecting');
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const resolvedEndpoint = useMemo(() => resolveEndpoint(endpoint), [endpoint]);

  useEffect(() => {
    let isMounted = true;
    const ws = new WebSocket(resolvedEndpoint);
    wsRef.current = ws;

    ws.onopen = () => {
      if (!isMounted) return;
      setStatus('open');
      setError(null);
    };

    ws.onmessage = (event) => {
      if (!isMounted) return;
      try {
        const payload = JSON.parse(event.data);
        const idValue: string = payload.id ?? `${payload.ts}-${payload.qty}-${payload.price}-${Date.now()}`;
        const tsValue = Number(payload.ts ?? payload.T);
        const priceValue = Number(payload.price ?? payload.p);
        const qtyValue = Number(payload.qty ?? payload.q);
        const sideValue = payload.side ?? (payload.m === false ? 'buy' : 'sell');

        if (Number.isNaN(tsValue) || Number.isNaN(priceValue) || Number.isNaN(qtyValue)) {
          return;
        }

        setTrades((prev) => {
          const next = prev.length >= bufferSize ? prev.slice(prev.length - bufferSize + 1) : prev.slice();
          next.push({
            id: String(idValue),
            ts: tsValue,
            price: priceValue,
            qty: qtyValue,
            side: sideValue === 'buy' ? 'buy' : 'sell',
          });
          return next;
        });
      } catch (err) {
        console.error('Failed to parse trade event', err);
      }
    };

    ws.onclose = () => {
      if (!isMounted) return;
      setStatus('closed');
    };

    ws.onerror = (event) => {
      console.error('WebSocket error', event);
      if (!isMounted) return;
      setStatus('error');
      setError('Unable to stream trades');
    };

    return () => {
      isMounted = false;
      ws.close();
    };
  }, [bufferSize, resolvedEndpoint]);

  const latestTrade = trades.at(-1) ?? null;

  const summary = useMemo(() => {
    if (trades.length === 0) {
      return {
        lastPrice: null as number | null,
        changePct: 0,
      };
    }

    const first = trades[0];
    const last = trades[trades.length - 1];
    const changePct = first.price === 0 ? 0 : ((last.price - first.price) / first.price) * 100;

    return {
      lastPrice: last.price,
      changePct,
    };
  }, [trades]);

  return {
    trades,
    latestTrade,
    status,
    error,
    summary,
  };
};
