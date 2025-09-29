import type { TradeEvent } from '../hooks/useTradeStream';

interface TradeFeedProps {
  symbol: string;
  trades: TradeEvent[];
  status: 'connecting' | 'open' | 'closed' | 'error';
}

const TradeFeed = ({ symbol, trades, status }: TradeFeedProps) => {
  const items = [...trades].slice(-30).reverse();

  return (
    <div className="flex h-full flex-col gap-4">
      <div>
        <h2 className="text-lg font-semibold text-white">Recent Trades</h2>
        <p className="text-sm text-slate-500">Streaming ticks for {symbol}</p>
      </div>
      <div className="space-y-3">
        {items.length === 0 && (
          <div className="rounded-xl border border-dashed border-slate-700 px-4 py-6 text-center text-sm text-slate-500">
            {status === 'error' ? 'Unable to stream trades right now.' : 'Trades will appear here once live data arrives.'}
          </div>
        )}
        {items.map((trade) => {
          const date = new Date(trade.ts);
          const timeLabel = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
          const sideColor = trade.side === 'buy' ? 'bg-emerald-500/5 text-emerald-300' : 'bg-rose-500/5 text-rose-300';

          return (
            <div
              key={trade.id}
              data-testid="trade-row"
              className={`flex items-center justify-between rounded-xl border border-slate-800 px-4 py-3 text-sm ${sideColor}`}
            >
              <div className="flex flex-col">
                <span className="text-xs uppercase tracking-widest text-slate-400">{timeLabel}</span>
                <span className="font-semibold text-white">${trade.price.toLocaleString()}</span>
              </div>
              <div className="text-right">
                <p className="font-medium">{trade.qty.toFixed(6)} BTC</p>
                <span className="text-xs uppercase tracking-widest text-slate-400">{trade.side}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default TradeFeed;
