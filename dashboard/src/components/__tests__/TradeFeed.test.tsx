import { render, screen } from '@testing-library/react';
import TradeFeed from '../TradeFeed';
import type { TradeEvent } from '../../hooks/useTradeStream';

const baseTrades: TradeEvent[] = [
  { id: '1-0', ts: 1700000000000, price: 64000, qty: 0.01, side: 'buy' },
  { id: '1-1', ts: 1700000001000, price: 64010, qty: 0.02, side: 'sell' },
  { id: '1-2', ts: 1700000002000, price: 64005, qty: 0.03, side: 'buy' },
];

describe('TradeFeed', () => {
  it('renders the latest trades in reverse chronological order', () => {
    render(<TradeFeed symbol="BTC/USDT" trades={baseTrades} status="open" />);

    const rows = screen.getAllByTestId('trade-row');
    expect(rows).toHaveLength(3);
    expect(rows[0]).toHaveTextContent('$64,005');
    expect(rows[2]).toHaveTextContent('$64,000');
  });

  it('shows placeholder when there are no trades yet', () => {
    render(<TradeFeed symbol="BTC/USDT" trades={[]} status="connecting" />);

    expect(screen.getByText(/Trades will appear here/)).toBeInTheDocument();
  });
});
