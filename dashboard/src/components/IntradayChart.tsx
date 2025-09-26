import { useEffect, useRef } from 'react';
import { createChart, IChartApi, ISeriesApi, LineStyle, Time } from 'lightweight-charts';
import type { TradeEvent } from '../hooks/useTradeStream';

interface IntradayChartProps {
  symbol: string;
  trades: TradeEvent[];
  status: 'connecting' | 'open' | 'closed' | 'error';
}

const IntradayChart = ({ symbol, trades, status }: IntradayChartProps) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<'Area'> | null>(null);

  useEffect(() => {
    if (!containerRef.current) {
      return;
    }

    const chart = createChart(containerRef.current, {
      layout: {
        background: { color: 'transparent' },
        textColor: '#cbd5f5',
      },
      grid: {
        vertLines: { color: 'rgba(148, 163, 184, 0.1)' },
        horzLines: { color: 'rgba(148, 163, 184, 0.1)' },
      },
      width: containerRef.current.clientWidth,
      height: 360,
      rightPriceScale: {
        borderColor: 'rgba(148, 163, 184, 0.12)',
      },
      timeScale: {
        borderColor: 'rgba(148, 163, 184, 0.12)',
        timeVisible: true,
        secondsVisible: true,
      },
    });

    const series = chart.addAreaSeries({
      lineColor: '#00c805',
      topColor: 'rgba(0, 200, 5, 0.35)',
      bottomColor: 'rgba(0, 200, 5, 0.05)',
    });

    series.createPriceLine({
      price: 0,
      color: '#00c805',
      lineStyle: LineStyle.Dotted,
      lineWidth: 2,
      axisLabelVisible: true,
      title: symbol,
    });

    chartRef.current = chart;
    seriesRef.current = series;

    const handleResize = () => {
      if (!containerRef.current || !chartRef.current) {
        return;
      }
      chartRef.current.applyOptions({ width: containerRef.current.clientWidth });
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, [symbol]);

  useEffect(() => {
    if (!seriesRef.current) {
      return;
    }

    if (trades.length === 0) {
      seriesRef.current.setData([]);
      return;
    }

    const sortedTrades = [...trades].sort((a, b) => a.ts - b.ts);

    let lastTime = 0;
    const points = sortedTrades.map((trade, index) => {
      const rawTime = Math.floor(trade.ts / 1000);
      const time = rawTime <= lastTime ? lastTime + 1 : rawTime;
      lastTime = time;

      return {
        time: time as Time,
        value: trade.price,
      };
    });

    seriesRef.current.setData(points);
  }, [symbol, trades]);

  return (
    <div className="flex h-full flex-col gap-6">
      <div>
        <h2 className="text-lg font-semibold text-white">Intraday</h2>
        <p className="text-sm text-slate-400">
          {status === 'open' ? 'Live price action' : 'Waiting for trade data'} for {symbol}
        </p>
      </div>
      <div ref={containerRef} className="relative h-[360px] w-full rounded-2xl border border-slate-800 bg-slate-900/40">
        {trades.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center text-sm text-slate-500">
            {status === 'error' ? 'Unable to load trade data' : 'Streaming will appear here once trades arrive'}
          </div>
        )}
      </div>
    </div>
  );
};

export default IntradayChart;
