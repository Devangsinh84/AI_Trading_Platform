// src/components/Dashboard.jsx
import React, { useState, useEffect, useRef } from 'react';
import { 
  BarChart, 
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer 
} from 'recharts';
import { Activity, ShieldCheck, AlertTriangle, Download } from 'lucide-react';
import { toPng } from 'html-to-image';
import PerformanceMetrics from './PerformanceMetrics';
import TradingChart from './TradingChart'; // NEW: Our lightweight-chart engine

const Dashboard = () => {
  const [apiStatus, setApiStatus] = useState('Checking connection...');
  const [activeAgent, setActiveAgent] = useState('Loading...');
  const [marketData, setMarketData] = useState([]);
  const [shapData, setShapData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // 1. Reference for the export container
  const dashboardRef = useRef(null);

  useEffect(() => {
    // Check connection status
    fetch('http://localhost:5200/scalar/v1')
      .then(res => res.ok ? 'Connected to MetaController ✅' : 'API Error ❌')
      .catch(() => 'Backend unreachable (Possible CORS block) ❌')
      .then(setApiStatus);
      
    // Create a fetch function we can call repeatedly
    const fetchLiveData = () => {
      fetch('http://localhost:5200/api/TradingIntelligence/live-feed')
        .then(res => res.json())
        .then(data => {
          // 1. Map SHAP data to the new Python key
          setShapData(data.shap_values || []);
          
          // 2. Normalize "BEAR MARKET" to "Bear" or "Bull"
          const currentAgent = data.agent && data.agent.includes('BULL') ? 'Bull' : 'Bear';
          setActiveAgent(currentAgent);
          
          // 3. Create a STRICT UNIX timestamp for TradingView Lightweight Charts
          const now = new Date();
          const unixTimestamp = Math.floor(now.getTime() / 1000); 
          
          // 4. Append the new point to the historical array
          setMarketData(prevData => {
            // Safety check: Lightweight charts crashes if time isn't strictly increasing
            if (prevData.length > 0 && prevData[prevData.length - 1].timestamp >= unixTimestamp) {
                return prevData; 
            }

            const newPoint = {
              timestamp: unixTimestamp,
              price: data.price,
              agent: currentAgent
            };
            
            const updatedData = [...prevData, newPoint];
            // Keep last 100 ticks so the user has data to pan/zoom through
            return updatedData.slice(-100); 
          });
          
          setIsLoading(false);
        })
        .catch(err => {
          console.error("Failed to fetch data:", err);
          setApiStatus('Data Fetch Error ❌');
          setIsLoading(false);
        });
    };

    fetchLiveData();
    const intervalId = setInterval(fetchLiveData, 3000);

    return () => clearInterval(intervalId);
  }, []);

  // 2. Export function for the academic report
  const handleExport = async () => {
    if (dashboardRef.current) {
      try {
        const dataUrl = await toPng(dashboardRef.current, {
          backgroundColor: '#0f172a',
          pixelRatio: 2 
        });
        
        const link = document.createElement('a');
        link.download = 'xai-trading-results.png';
        link.href = dataUrl;
        link.click();
      } catch (err) {
        console.error('Failed to export dashboard image:', err);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-4">
        <div className="flex flex-col items-center gap-4">
            <Activity className="w-12 h-12 text-indigo-500 animate-pulse" />
            <h1 className="text-2xl font-bold text-indigo-400">Syncing with Meta-Controller...</h1>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 font-sans bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-slate-950">
      
      {/* Header & Status */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400 tracking-tight">
            XAI Trading Terminal
          </h1>
          <p className="text-slate-400 mt-1">Deep Reinforcement Learning Meta-Controller</p>
        </div>
        <div className="flex gap-4 items-center">
          {/* Glassmorphic Status Badge */}
          <div className="bg-slate-800/60 backdrop-blur-md px-4 py-2 rounded-lg border border-slate-700/50 shadow-lg flex items-center gap-3">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
            <span className="font-mono text-sm text-slate-200">{apiStatus}</span>
          </div>
          <button 
            onClick={handleExport}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-lg font-medium transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)] hover:shadow-[0_0_25px_rgba(79,70,229,0.5)] border border-indigo-500/50"
          >
            <Download size={18} />
            Export Snapshot
          </button>
        </div>
      </div>

      {/* 3. The export container wrapper */}
      <div ref={dashboardRef} className="p-1 rounded-xl">
        
        {/* Performance Metrics Cards */}
        <PerformanceMetrics />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Core Trading Chart Component */}
          <div className="lg:col-span-2 bg-slate-800/60 backdrop-blur-md p-6 rounded-xl border border-slate-700/50 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 to-cyan-500 opacity-50"></div>
            <h2 className="text-xl font-semibold mb-4 text-slate-200">Live Agent Execution & Market State</h2>
            <div className="h-96 w-full">
               <TradingChart data={marketData} />
            </div>
          </div>

          {/* XAI Explainability Panel */}
          <div className="flex flex-col gap-6">
            
            {/* Active Sub-Agent Card */}
            <div className="bg-slate-800/60 backdrop-blur-md p-6 rounded-xl border border-slate-700/50 shadow-2xl">
              <h2 className="text-lg font-semibold mb-3 text-slate-200">Active Sub-Agent</h2>
              <div className={`p-5 rounded-xl flex items-center gap-4 transition-all duration-500 ${activeAgent === 'Bull' ? 'bg-emerald-900/20 border border-emerald-500/30 shadow-[inset_0_0_20px_rgba(16,185,129,0.1)]' : 'bg-rose-900/20 border border-rose-500/30 shadow-[inset_0_0_20px_rgba(244,63,94,0.1)]'}`}>
                {activeAgent === 'Bull' ? <ShieldCheck className="w-10 h-10 text-emerald-400 drop-shadow-[0_0_8px_rgba(52,211,153,0.5)]" /> : <AlertTriangle className="w-10 h-10 text-rose-400 drop-shadow-[0_0_8px_rgba(251,113,133,0.5)]" />}
                <div>
                  <p className={`text-2xl font-black tracking-wider ${activeAgent === 'Bull' ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {activeAgent.toUpperCase()} MARKET
                  </p>
                  <p className="text-sm text-slate-400 font-medium">Meta-controller routing active</p>
                </div>
              </div>
            </div>

            {/* Recharts SHAP Component (Styled up to match) */}
            <div className="bg-slate-800/60 backdrop-blur-md p-6 rounded-xl border border-slate-700/50 shadow-2xl flex-grow">
              <h2 className="text-lg font-semibold mb-1 text-slate-200">XAI Decision Drivers (SHAP)</h2>
              <p className="text-xs text-slate-400 mb-6">Real-time metrics influencing the model's routing.</p>
              <div className="h-48 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={shapData} layout="vertical" margin={{ top: 0, right: 10, left: 10, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} vertical={true} opacity={0.5} />
                    <XAxis type="number" stroke="#64748b" axisLine={false} tickLine={false} />
                    <YAxis dataKey="feature" type="category" stroke="#94a3b8" fontSize={11} axisLine={false} tickLine={false} />
                    <Tooltip cursor={{ fill: '#334155', opacity: 0.4 }} contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#e2e8f0' }} />
                    <Bar dataKey="importance" fill="#818cf8" radius={[0, 4, 4, 0]} barSize={20} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;