import { render, screen } from '@testing-library/react';
import PriceTicker from '../PriceTicker';

describe('PriceTicker', () => {
  it('renders symbol, price and change when live', () => {
    render(
      <PriceTicker symbol="BTC/USDT" price={64000.42} changePct={1.23} status="open" error={null} />,
    );

    expect(screen.getByText('BTC/USDT')).toBeInTheDocument();
    expect(screen.getByText(/\$64,000\.42/)).toBeInTheDocument();
    expect(screen.getByText('+1.23%')).toBeInTheDocument();
    expect(screen.getByText('Live')).toBeInTheDocument();
  });

  it('shows error badge and placeholder values when websocket errored', () => {
    render(
      <PriceTicker symbol="BTC/USDT" price={null} changePct={0} status="error" error="boom" />,
    );

    expect(screen.getByText('Error')).toBeInTheDocument();
    const placeholders = screen.getAllByText('—');
    expect(placeholders).toHaveLength(2);
  });
});
