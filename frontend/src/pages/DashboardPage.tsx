import React, { useState, useEffect } from 'react';
import api from '../services/api';

interface Alert {
  id: number;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  source_name: string;
  created_at: string;
}

interface KPI {
  totalArticles: number;
  activeSources: number;
  activeAlerts: number;
  analysesRun: number;
  articleTrend: 'up' | 'down' | 'flat';
}

interface IndustryVolume {
  name: string;
  count: number;
}

const Skeleton: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`animate-pulse bg-dark-700 rounded ${className}`} />
);

const DashboardPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('All');
  const [loading, setLoading] = useState(true);
  const [kpi, setKpi] = useState<KPI | null>(null);
  const [industryVolumes, setIndustryVolumes] = useState<IndustryVolume[]>([]);
  const [recentAlerts, setRecentAlerts] = useState<Alert[]>([]);
  const [trendingTopics, setTrendingTopics] = useState<string[]>([]);

  const tabs = ['Pharma', 'Life Science', 'Semiconductor', 'All'];

  useEffect(() => {
    const fetchDashboard = async () => {
      setLoading(true);
      try {
        // Simulate dashboard data from the API
        const [kpiRes, volRes, alertsRes, topicsRes] = await Promise.all([
          api.get('/api/dashboard/kpi'),
          api.get('/api/dashboard/industry-volume'),
          api.get('/api/dashboard/recent-alerts'),
          api.get('/api/dashboard/trending-topics'),
        ]);
        setKpi(kpiRes.data);
        setIndustryVolumes(volRes.data);
        setRecentAlerts(alertsRes.data);
        setTrendingTopics(topicsRes.data);
      } catch {
        // Fallback mock data for development
        setKpi({
          totalArticles: 1247,
          activeSources: 38,
          activeAlerts: 12,
          analysesRun: 89,
          articleTrend: 'up',
        });
        setIndustryVolumes([
          { name: 'Pharma', count: 482 },
          { name: 'Life Science', count: 358 },
          { name: 'Semiconductor', count: 226 },
        ]);
        setRecentAlerts([
          { id: 1, title: 'FDA approval expected for new gene therapy', severity: 'critical', source_name: 'BioPharma Dive', created_at: '2h ago' },
          { id: 2, title: 'Supply chain disruption in API manufacturing', severity: 'high', source_name: 'Chemical Weekly', created_at: '5h ago' },
          { id: 3, title: 'New patent filing for mRNA delivery system', severity: 'medium', source_name: 'Nature Biotech', created_at: '12h ago' },
          { id: 4, title: 'EU reviews semiconductor subsidy framework', severity: 'medium', source_name: 'Reuters', created_at: '1d ago' },
          { id: 5, title: 'Q3 earnings beat estimates for major pharma', severity: 'low', source_name: 'Bloomberg', created_at: '2d ago' },
        ]);
        setTrendingTopics([
          'mRNA vaccine', 'gene editing', 'AI drug discovery',
          'biosimilars', 'supply chain', 'clinical trials',
          'regulatory approval', 'cell therapy',
        ]);
      }
      setLoading(false);
    };
    fetchDashboard();
  }, [activeTab]);

  const severityColors: Record<string, string> = {
    critical: 'bg-red-500/20 text-red-400 border-red-500/30',
    high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    low: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  };

  const maxVolume = Math.max(...industryVolumes.map((v) => v.count), 1);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-white">Dashboard</h1>
        <span className="text-dark-400 text-sm">
          {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
        </span>
      </div>

      {/* Industry Tabs */}
      <div className="flex gap-2 border-b border-dark-700 pb-3">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === tab
                ? 'bg-primary-600/20 text-primary-400 border border-primary-500/30'
                : 'text-dark-400 hover:text-white hover:bg-dark-700 border border-transparent'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {loading ? (
          <>
            <Skeleton className="h-24" />
            <Skeleton className="h-24" />
            <Skeleton className="h-24" />
            <Skeleton className="h-24" />
          </>
        ) : (
          kpi && (
            <>
              <div className="bg-dark-800 border border-dark-700 rounded-xl p-4">
                <p className="text-dark-400 text-xs uppercase tracking-wider mb-1">Total Articles</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-bold text-white">{kpi.totalArticles.toLocaleString()}</span>
                  <span className={`text-sm ${kpi.articleTrend === 'up' ? 'text-green-400' : kpi.articleTrend === 'down' ? 'text-red-400' : 'text-dark-400'}`}>
                    {kpi.articleTrend === 'up' ? '↑' : kpi.articleTrend === 'down' ? '↓' : '→'}
                  </span>
                </div>
                <p className="text-dark-500 text-xs mt-1">from all sources</p>
              </div>
              <div className="bg-dark-800 border border-dark-700 rounded-xl p-4">
                <p className="text-dark-400 text-xs uppercase tracking-wider mb-1">Active Sources</p>
                <span className="text-2xl font-bold text-white">{kpi.activeSources}</span>
                <p className="text-dark-500 text-xs mt-1">monitored continuously</p>
              </div>
              <div className="bg-dark-800 border border-dark-700 rounded-xl p-4">
                <p className="text-dark-400 text-xs uppercase tracking-wider mb-1">Active Alerts</p>
                <span className="text-2xl font-bold text-white">{kpi.activeAlerts}</span>
                <p className="text-dark-500 text-xs mt-1">triggered this week</p>
              </div>
              <div className="bg-dark-800 border border-dark-700 rounded-xl p-4">
                <p className="text-dark-400 text-xs uppercase tracking-wider mb-1">Analyses Run</p>
                <span className="text-2xl font-bold text-white">{kpi.analysesRun}</span>
                <p className="text-dark-500 text-xs mt-1">total to date</p>
              </div>
            </>
          )
        )}
      </div>

      {/* Article Volume + Recent Alerts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Article Volume by Industry */}
        <div className="bg-dark-800 border border-dark-700 rounded-xl p-5">
          <h2 className="text-white font-medium mb-4">Article Volume by Industry</h2>
          {loading ? (
            <div className="space-y-3">
              <Skeleton className="h-6" />
              <Skeleton className="h-6" />
              <Skeleton className="h-6" />
            </div>
          ) : (
            <div className="space-y-3">
              {industryVolumes.map((iv) => (
                <div key={iv.name}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-dark-300">{iv.name}</span>
                    <span className="text-white font-medium">{iv.count.toLocaleString()}</span>
                  </div>
                  <div className="h-2 bg-dark-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-primary-500 to-primary-400 rounded-full transition-all duration-500"
                      style={{ width: `${(iv.count / maxVolume) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Alerts */}
        <div className="bg-dark-800 border border-dark-700 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-white font-medium">Recent Alerts</h2>
            <span className="text-dark-400 text-xs">{recentAlerts.length} active</span>
          </div>
          {loading ? (
            <div className="space-y-3">
              <Skeleton className="h-14" />
              <Skeleton className="h-14" />
              <Skeleton className="h-14" />
            </div>
          ) : (
            <div className="space-y-2">
              {recentAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className="flex items-start gap-3 p-3 rounded-lg bg-dark-900/50 border border-dark-700 hover:border-dark-500 transition-colors"
                >
                  <span
                    className={`text-xs px-2 py-0.5 rounded border font-medium capitalize ${severityColors[alert.severity]}`}
                  >
                    {alert.severity}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-white text-sm truncate">{alert.title}</p>
                    <p className="text-dark-500 text-xs mt-0.5">
                      {alert.source_name} · {alert.created_at}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Trending Topics */}
      <div className="bg-dark-800 border border-dark-700 rounded-xl p-5">
        <h2 className="text-white font-medium mb-4">Trending Topics</h2>
        {loading ? (
          <div className="flex gap-2 flex-wrap">
            <Skeleton className="h-8 w-20" />
            <Skeleton className="h-8 w-24" />
            <Skeleton className="h-8 w-16" />
            <Skeleton className="h-8 w-28" />
          </div>
        ) : (
          <div className="flex flex-wrap gap-2">
            {trendingTopics.map((topic) => (
              <span
                key={topic}
                className="px-3 py-1.5 bg-dark-700/50 text-dark-300 text-sm rounded-full border border-dark-600 hover:border-primary-500/30 hover:text-primary-400 transition-colors cursor-pointer"
              >
                {topic}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
