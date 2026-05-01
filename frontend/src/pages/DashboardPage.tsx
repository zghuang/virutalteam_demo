import React, { useState, useEffect } from 'react';

interface KpiCard { label: string; value: number; change: number; }
interface Alert { id: number; name: string; severity: string; message: string; }
interface Trend { trend: string; count: number; }

const mockKpis: KpiCard[] = [
  { label: 'Total Articles', value: 1284, change: 12 },
  { label: 'Active Sources', value: 14, change: 2 },
  { label: 'Active Alerts', value: 8, change: -1 },
  { label: 'Analyses Run', value: 47, change: 5 },
];

const mockAlerts: Alert[] = [
  { id: 1, name: 'FDA Approval Update', severity: 'critical', message: 'New drug approvals detected' },
  { id: 2, name: 'Patent Filing Spike', severity: 'high', message: 'USPTO filings up 30% this week' },
  { id: 3, name: 'Semiconductor Supply', severity: 'medium', message: 'TSMC capacity update' },
];

const mockTrends: Trend[] = [
  { trend: 'AI Drug Discovery', count: 24 },
  { trend: 'Chip Shortage', count: 18 },
  { trend: 'Gene Therapy', count: 15 },
  { trend: 'EUV Lithography', count: 12 },
  { trend: 'mRNA Vaccines', count: 10 },
];

const DashboardPage: React.FC = () => {
  const [industry, setIndustry] = useState('all');
  const [loading, setLoading] = useState(true);
  const industries = ['All', 'Pharma', 'Life Science', 'Semiconductor'];

  useEffect(() => {
    const t = setTimeout(() => setLoading(false), 800);
    return () => clearTimeout(t);
  }, []);

  if (loading) return <div className="space-y-4"><div className="h-8 bg-dark-700 rounded animate-pulse w-48" /><div className="grid grid-cols-4 gap-4">{Array(4).fill(0).map((_,i) => <div key={i} className="h-24 bg-dark-700 rounded-lg animate-pulse" />)}</div></div>;

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-2xl font-semibold text-white mb-6">Dashboard</h1>

      {/* Industry tabs */}
      <div className="flex gap-2 mb-6">
        {industries.map(ind => (
          <button key={ind} onClick={() => setIndustry(ind.toLowerCase())}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              industry === ind.toLowerCase() ? 'bg-primary-600 text-white' : 'bg-dark-800 text-dark-300 hover:bg-dark-700'
            }`}>{ind}</button>
        ))}
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {mockKpis.map(kpi => (
          <div key={kpi.label} className="bg-dark-800 border border-dark-700 rounded-lg p-4">
            <div className="text-dark-400 text-xs mb-1">{kpi.label}</div>
            <div className="text-2xl font-bold text-white">{kpi.value.toLocaleString()}</div>
            <div className={`text-xs mt-1 ${kpi.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {kpi.change >= 0 ? '▲' : '▼'} {Math.abs(kpi.change)}%
            </div>
          </div>
        ))}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-dark-800 border border-dark-700 rounded-lg p-4">
          <h3 className="text-white font-medium mb-3">Article Volume by Industry</h3>
          <div className="space-y-2">
            {[{label:'Pharma',val:65},{label:'Life Science',val:45},{label:'Semiconductor',val:52}].map(item => (
              <div key={item.label}>
                <div className="flex justify-between text-xs text-dark-400 mb-1"><span>{item.label}</span><span>{item.val}%</span></div>
                <div className="w-full bg-dark-700 rounded-full h-2"><div className="bg-primary-500 h-2 rounded-full" style={{width:`${item.val}%`}} /></div>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-dark-800 border border-dark-700 rounded-lg p-4">
          <h3 className="text-white font-medium mb-3">Recent Alerts</h3>
          <div className="space-y-2">
            {mockAlerts.map(a => (
              <div key={a.id} className="flex items-center gap-2 p-2 bg-dark-900 rounded-lg">
                <span className={`w-2 h-2 rounded-full ${
                  a.severity === 'critical' ? 'bg-red-500' : a.severity === 'high' ? 'bg-yellow-500' : 'bg-blue-500'
                }`} />
                <div className="flex-1"><div className="text-white text-sm">{a.name}</div><div className="text-dark-400 text-xs">{a.message}</div></div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Trending Topics */}
      <div className="bg-dark-800 border border-dark-700 rounded-lg p-4">
        <h3 className="text-white font-medium mb-3">Trending Topics</h3>
        <div className="flex flex-wrap gap-2">
          {mockTrends.map(t => (
            <span key={t.trend} className="px-3 py-1 bg-dark-700 rounded-full text-sm text-dark-200">
              {t.trend} <span className="text-dark-500 ml-1">x{t.count}</span>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
