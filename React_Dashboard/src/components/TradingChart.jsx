import React, { useEffect, useRef } from 'react';
import { createChart, ColorType, LineSeries } from 'lightweight-charts'; // NEW: Imported LineSeries

const TradingChart = ({ data }) => {
  const chartContainerRef = useRef();
  const chartRef = useRef(null);
  const seriesRef = useRef(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // 1. Initialize the chart with a sleek dark theme
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#1e293b' }, // slate-800
        textColor: '#94a3b8', // slate-400
      },
      grid: {
        vertLines: { color: '#334155' }, // slate-700
        horzLines: { color: '#334155' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 384, // matches Tailwind's h-96
      timeScale: {
        timeVisible: true,
        secondsVisible: true,
      },
    });

    // 2. Add the main price line (Glowing Indigo) - UPDATED FOR V5 API
    const lineSeries = chart.addSeries(LineSeries, {
      color: '#818cf8', 
      lineWidth: 2,
      crosshairMarkerVisible: true,
      crosshairMarkerRadius: 6,
    });

    chartRef.current = chart;
    seriesRef.current = lineSeries;

    // 3. Handle window resizing smoothly
    const handleResize = () => {
      chart.applyOptions({ width: chartContainerRef.current.clientWidth });
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  // 4. Update data dynamically when the live feed sends new ticks
  useEffect(() => {
    if (seriesRef.current && data && data.length > 0) {
      // Lightweight charts expects { time, value }, so we map it
      const formattedData = data.map(point => ({
        time: point.timestamp || Math.floor(Date.now() / 1000), // UNIX timestamp
        value: point.price
      }));
      seriesRef.current.setData(formattedData);
    }
  }, [data]);

  return <div ref={chartContainerRef} className="w-full h-full rounded-xl overflow-hidden" />;
};

export default TradingChart;