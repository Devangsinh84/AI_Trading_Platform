import React, { useState, useEffect } from 'react';
import { Activity, TrendingDown, TrendingUp } from 'lucide-react'; 

const PerformanceMetrics = () => {
  const [metrics, setMetrics] = useState({ sharpeRatio: 0, maximumDrawdown: 0, cumulativeReturn: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch('http://localhost:5200/api/performance-metrics');
        const data = await response.json();
        setMetrics(data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching metrics:', error);
        setLoading(false);
      }
    };

    // Fetch immediately, then poll every 3 seconds to keep it LIVE
    fetchMetrics();
    const intervalId = setInterval(fetchMetrics, 3000);

    // Cleanup the interval when the component unmounts
    return () => clearInterval(intervalId);
  }, []);

  // Helper function to prevent the "+-" bug for negative numbers
  const formatReturn = (value) => {
    const num = Number(value);
    if (num > 0) return `+${num}%`;
    if (num < 0) return `${num}%`;
    return `0%`;
  };

  if (loading) {
    return (
      <div className="flex gap-6 mb-6 animate-pulse">
        {[1, 2, 3].map(i => (
          <div key={i} className="bg-slate-800/40 h-24 rounded-xl flex-1 border border-slate-700/30"></div>
        ))}
      </div>
    );
  }

  return (
    <div className="flex flex-col md:flex-row gap-6 mb-6">
      {/* Sharpe Ratio Card */}
      <div className="bg-slate-800/60 backdrop-blur-md p-5 rounded-xl border border-slate-700/50 shadow-lg flex-1 flex items-center justify-between transition-all duration-300 hover:shadow-indigo-500/10">
        <div>
          <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">Sharpe Ratio</p>
          <h3 className={`text-2xl font-bold font-mono ${metrics.sharpeRatio >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {metrics.sharpeRatio}
          </h3>
        </div>
        <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-700/50 shadow-inner">
          <Activity className={metrics.sharpeRatio >= 0 ? "text-emerald-400" : "text-rose-400"} size={24} />
        </div>
      </div>

      {/* Maximum Drawdown Card */}
      <div className="bg-slate-800/60 backdrop-blur-md p-5 rounded-xl border border-slate-700/50 shadow-lg flex-1 flex items-center justify-between transition-all duration-300 hover:shadow-rose-500/10">
        <div>
          <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">Max Drawdown</p>
          <h3 className="text-2xl font-bold font-mono text-rose-400">
            {metrics.maximumDrawdown}%
          </h3>
        </div>
        <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-700/50 shadow-inner">
          <TrendingDown className="text-rose-400" size={24} />
        </div>
      </div>

      {/* Cumulative Return Card */}
      <div className="bg-slate-800/60 backdrop-blur-md p-5 rounded-xl border border-slate-700/50 shadow-lg flex-1 flex items-center justify-between transition-all duration-300 hover:shadow-emerald-500/10">
        <div>
          <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">Cumulative Return</p>
          <h3 className={`text-2xl font-bold font-mono ${metrics.cumulativeReturn >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {formatReturn(metrics.cumulativeReturn)}
          </h3>
        </div>
        <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-700/50 shadow-inner">
          <TrendingUp className={metrics.cumulativeReturn >= 0 ? "text-emerald-400" : "text-rose-400"} size={24} />
        </div>
      </div>
    </div>
  );
};

export default PerformanceMetrics;