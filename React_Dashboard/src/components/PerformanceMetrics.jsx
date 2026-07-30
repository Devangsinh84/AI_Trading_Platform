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

    fetchMetrics();
  }, []);

  if (loading) return <div className="text-white">Loading metrics...</div>;

  return (
    <div className="flex gap-4 mb-6">
      {/* Sharpe Ratio Card */}
      <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 flex-1 flex items-center justify-between">
        <div>
          <p className="text-slate-400 text-sm font-medium mb-1">Sharpe Ratio</p>
          <h3 className="text-2xl font-bold text-green-400">{metrics.sharpeRatio}</h3>
        </div>
        <div className="bg-slate-700 p-3 rounded-full">
          <Activity className="text-green-400" size={24} />
        </div>
      </div>

      {/* Maximum Drawdown Card */}
      <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 flex-1 flex items-center justify-between">
        <div>
          <p className="text-slate-400 text-sm font-medium mb-1">Max Drawdown</p>
          <h3 className="text-2xl font-bold text-red-400">{metrics.maximumDrawdown}%</h3>
        </div>
        <div className="bg-slate-700 p-3 rounded-full">
          <TrendingDown className="text-red-400" size={24} />
        </div>
      </div>

      {/* Cumulative Return Card */}
      <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 flex-1 flex items-center justify-between">
        <div>
          <p className="text-slate-400 text-sm font-medium mb-1">Cumulative Return</p>
          <h3 className="text-2xl font-bold text-emerald-400">+{metrics.cumulativeReturn}%</h3>
        </div>
        <div className="bg-slate-700 p-3 rounded-full">
          <TrendingUp className="text-emerald-400" size={24} />
        </div>
      </div>
    </div>
  );
};

export default PerformanceMetrics;