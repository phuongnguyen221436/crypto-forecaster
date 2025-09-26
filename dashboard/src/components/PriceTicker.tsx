interface PriceTickerProps {
  symbol: string;
  price: number | null;
  changePct: number;
  status: 'connecting' | 'open' | 'closed' | 'error';
  error: string | null;
}

const PriceTicker = ({ symbol, price, changePct, status, error }: PriceTickerProps) => {
  const formattedPrice = price !== null ? `$${price.toLocaleString(undefined, { maximumFractionDigits: 2 })}` : '—';
  const formattedChange = price !== null ? `${changePct >= 0 ? '+' : ''}${changePct.toFixed(2)}%` : '—';

  const statusLabel = (() => {
    if (error) return 'Error';
    if (status === 'connecting') return 'Connecting';
    if (status === 'open') return 'Live';
    if (status === 'closed') return 'Closed';
    return status;
  })();

  const statusColor = error
    ? 'bg-rose-500/10 text-rose-400'
    : status === 'open'
    ? 'bg-emerald-500/10 text-emerald-400'
    : 'bg-amber-500/10 text-amber-300';

  const changeColor = changePct >= 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400';

  return (
    <div className="flex h-full items-center justify-between">
      <div>
        <p className="text-sm uppercase tracking-widest text-slate-400">{symbol}</p>
        <p className="mt-1 text-3xl font-semibold text-white">{formattedPrice}</p>
      </div>
      <div className="flex items-center gap-3">
        <span className={`rounded-full px-4 py-2 text-xs uppercase tracking-widest ${statusColor}`}>{statusLabel}</span>
        <div className={`rounded-full px-4 py-2 text-sm font-medium ${changeColor}`}>{formattedChange}</div>
      </div>
    </div>
  );
};

export default PriceTicker;
