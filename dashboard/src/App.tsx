import { useMemo } from 'react';
import ShellLayout from './components/ShellLayout';
import PriceTicker from './components/PriceTicker';
import IntradayChart from './components/IntradayChart';
import TradeFeed from './components/TradeFeed';
import PortfolioSnapshot from './components/PortfolioSnapshot';
import { useTradeStream } from './hooks/useTradeStream';

const App = () => {
  const { trades, summary, status, error } = useTradeStream();

  const positions = useMemo(
    () => [
      { symbol: 'BTC', quantity: 0.5, value: 32000 },
      { symbol: 'ETH', quantity: 4, value: 12500 },
      { symbol: 'SOL', quantity: 120, value: 18000 },
    ],
    [],
  );

  return (
    <ShellLayout
      sidebar={<PortfolioSnapshot positions={positions} />}
      header={
        <PriceTicker
          symbol="BTC/USDT"
          price={summary.lastPrice}
          changePct={summary.changePct}
          status={status}
          error={error}
        />
      }
      main={<IntradayChart symbol="BTC/USDT" trades={trades} status={status} />}
      activity={<TradeFeed symbol="BTC/USDT" trades={trades} status={status} />}
    />
  );
};

export default App;
