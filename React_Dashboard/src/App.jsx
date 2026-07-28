import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceArea, BarChart, Bar } from 'recharts';
import { Activity, ShieldCheck, AlertTriangle } from 'lucide-react';

function App() {
  const [apiStatus, setApiStatus] = useState('Checking connection...');
  const [activeAgent, setActiveAgent] = useState('Loading...');
  
  // New state variables to hold the live data from .NET
  const [marketData, setMarketData] = useState([]);
  const [shapData, setShapData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // 1. Keep the connection status check
    fetch('http://localhost:5200/scalar/v1')
      .then(res => res.ok ? 'Connected to MetaController ✅' : 'API Error ❌')
      .catch(() => 'Backend unreachable (Possible CORS block) ❌')
      .then(setApiStatus);
      
    // 2. Fetch the live trading data from the new endpoint
    fetch('http://localhost:5200/api/trading-state')
      .then(res => res.json())
      .then(data => {
        setMarketData(data.marketData);
        setShapData(data.shapData);
        
        // Dynamically set the active agent based on the latest data point
        if (data.marketData && data.marketData.length > 0) {
          setActiveAgent(data.marketData[data.marketData.length - 1].agent);
        }
        setIsLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch data:", err);
        setApiStatus('Data Fetch Error ❌');
        setIsLoading(false);
      });
  }, []);

  // Show a loading screen while fetching data to prevent crashes
  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 text-slate-100 flex items-center justify-center p-4">
        <h1 className="text-2xl font-bold text-indigo-400 animate-pulse">Fetching Data from .NET Meta-Controller...</h1>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6 font-sans">
      
      {/* Header & Status */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-indigo-400 tracking-tight">XAI Trading Dashboard</h1>
          <p className="text-slate-400 mt-1">Deep Reinforcement Learning Meta-Controller</p>
        </div>
        <div className="bg-slate-800 px-4 py-2 rounded-lg border border-slate-700 shadow-md flex items-center gap-2">
          <Activity className="w-5 h-5 text-emerald-400" />
          <span className="font-mono text-sm">{apiStatus}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Core Trading Chart */}
        <div className="lg:col-span-2 bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl">
          <h2 className="text-xl font-semibold mb-4 text-slate-200">Live Agent Execution & Market State</h2>
          <div className="h-96 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={marketData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="time" stroke="#94a3b8" />
                <YAxis domain={['auto', 'auto']} stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#475569' }} />
                
                {marketData.map((dataPoint, index) => {
                  if (index === 0) return null;
                  const prevPoint = marketData[index - 1];
                  return (
                    <ReferenceArea
                      key={index}
                      x1={prevPoint.time}
                      x2={dataPoint.time}
                      fill={dataPoint.agent === 'Bull' ? '#10b981' : '#ef4444'}
                      fillOpacity={0.15}
                    />
                  );
                })}
                <Line type="monotone" dataKey="price" stroke="#818cf8" strokeWidth={3} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* XAI Explainability Panel */}
        <div className="flex flex-col gap-6">
          
          <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl">
            <h2 className="text-lg font-semibold mb-2 text-slate-200">Active Sub-Agent</h2>
            <div className={`p-4 rounded-lg flex items-center gap-3 ${activeAgent === 'Bull' ? 'bg-emerald-900/30 border border-emerald-500/50' : 'bg-red-900/30 border border-red-500/50'}`}>
              {activeAgent === 'Bull' ? <ShieldCheck className="w-8 h-8 text-emerald-400" /> : <AlertTriangle className="w-8 h-8 text-red-400" />}
              <div>
                <p className={`text-2xl font-bold ${activeAgent === 'Bull' ? 'text-emerald-400' : 'text-red-400'}`}>
                  {activeAgent.toUpperCase()} MARKET
                </p>
                <p className="text-sm text-slate-400">Meta-controller routing active</p>
              </div>
            </div>
          </div>

          <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl flex-grow">
            <h2 className="text-lg font-semibold mb-4 text-slate-200">XAI Decision Drivers (SHAP)</h2>
            <p className="text-sm text-slate-400 mb-4">Real-time metrics influencing the Meta-Controller's switch.</p>
            <div className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={shapData} layout="vertical" margin={{ top: 0, right: 0, left: 30, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                  <XAxis type="number" stroke="#94a3b8" />
                  <YAxis dataKey="feature" type="category" stroke="#94a3b8" fontSize={12} />
                  <Tooltip cursor={{fill: '#334155'}} contentStyle={{ backgroundColor: '#1e293b', borderColor: '#475569' }} />
                  <Bar dataKey="importance" fill="#c084fc" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

export default App;