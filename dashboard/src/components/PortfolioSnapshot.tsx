interface Position {
  symbol: string;
  quantity: number;
  value: number;
}

interface PortfolioSnapshotProps {
  positions: Position[];
}

const PortfolioSnapshot = ({ positions }: PortfolioSnapshotProps) => {
  const totalValue = positions.reduce((acc, item) => acc + item.value, 0);

  return (
    <div className="flex h-full flex-col gap-6">
      <div>
        <h2 className="text-lg font-semibold text-white">Portfolio</h2>
        <p className="text-sm text-slate-500">Snapshot of holdings and allocation</p>
      </div>
      <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-5">
        <p className="text-xs uppercase tracking-widest text-slate-400">Total Value</p>
        <p className="mt-2 text-2xl font-semibold text-white">${totalValue.toLocaleString()}</p>
      </div>
      <div className="space-y-4">
        {positions.map((position) => (
          <div key={position.symbol} className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-white">{position.symbol}</p>
              <p className="text-xs text-slate-500">{position.quantity} coins</p>
            </div>
            <span className="text-sm font-medium text-white">${position.value.toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PortfolioSnapshot;
