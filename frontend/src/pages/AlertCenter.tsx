import React, { useState, useEffect } from 'react';
import api from '../services/api';

interface Alert {
  id: number;
  name: string;
  keyword: string;
  category: string | null;
  source: string | null;
  frequency: string;
  enabled: boolean;
  notify_email: boolean;
  created_at: string;
}

interface AlertEvent {
  alert_id: number;
  message: string;
  timestamp: string;
}

const AlertCenter: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [events, setEvents] = useState<AlertEvent[]>([]);
  const [name, setName] = useState('');
  const [keyword, setKeyword] = useState('');
  const [frequency, setFrequency] = useState('daily');
  const [tab, setTab] = useState<'alerts' | 'events'>('alerts');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAlerts();
    fetchEvents();
  }, []);

  const fetchAlerts = async () => {
    try {
      const res = await api.get('/api/alerts');
      setAlerts(res.data.alerts);
    } catch {
      setError('Failed to load alerts');
    }
  };

  const fetchEvents = async () => {
    try {
      const res = await api.get('/api/alerts/events');
      setEvents(res.data.events);
    } catch {
      // silently fail for events
    }
  };

  const createAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !keyword.trim()) {
      setError('Name and keyword are required');
      return;
    }
    try {
      await api.post('/api/alerts', { name, keyword, frequency });
      setName('');
      setKeyword('');
      setFrequency('daily');
      setError('');
      fetchAlerts();
    } catch {
      setError('Failed to create alert');
    }
  };

  const toggleAlert = async (alert: Alert) => {
    try {
      await api.put(`/api/alerts/${alert.id}`, { enabled: !alert.enabled });
      fetchAlerts();
    } catch {
      setError('Failed to update alert');
    }
  };

  const deleteAlert = async (id: number) => {
    try {
      await api.delete(`/api/alerts/${id}`);
      fetchAlerts();
    } catch {
      setError('Failed to delete alert');
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">Alert Center</h1>

      {/* Tab bar */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setTab('alerts')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            tab === 'alerts'
              ? 'bg-primary-600 text-white'
              : 'bg-dark-700 text-dark-300 hover:text-white'
          }`}
        >
          My Alerts
        </button>
        <button
          onClick={() => setTab('events')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            tab === 'events'
              ? 'bg-primary-600 text-white'
              : 'bg-dark-700 text-dark-300 hover:text-white'
          }`}
        >
          Events
        </button>
      </div>

      {error && (
        <div className="bg-red-900/50 border border-red-700 text-red-200 px-4 py-3 rounded-lg mb-4">
          {error}
          <button className="float-right text-red-300 hover:text-white" onClick={() => setError('')}>×</button>
        </div>
      )}

      {tab === 'alerts' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Create form */}
          <div className="bg-dark-800 rounded-xl p-5 border border-dark-700">
            <h2 className="text-lg font-semibold text-white mb-4">New Alert</h2>
            <form onSubmit={createAlert}>
              <div className="mb-3">
                <label className="block text-sm text-dark-300 mb-1">Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  className="w-full bg-dark-700 border border-dark-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-primary-500"
                  placeholder="e.g. AI Drug Discovery"
                />
              </div>
              <div className="mb-3">
                <label className="block text-sm text-dark-300 mb-1">Keyword</label>
                <input
                  type="text"
                  value={keyword}
                  onChange={e => setKeyword(e.target.value)}
                  className="w-full bg-dark-700 border border-dark-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-primary-500"
                  placeholder="e.g. CRISPR, mRNA"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm text-dark-300 mb-1">Frequency</label>
                <select
                  value={frequency}
                  onChange={e => setFrequency(e.target.value)}
                  className="w-full bg-dark-700 border border-dark-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-primary-500"
                >
                  <option value="realtime">Real-time</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                </select>
              </div>
              <button
                type="submit"
                className="w-full bg-primary-600 hover:bg-primary-500 text-white font-medium py-2 px-4 rounded-lg transition-colors text-sm"
              >
                Create Alert
              </button>
            </form>
          </div>

          {/* Alerts list */}
          <div className="lg:col-span-2 space-y-3">
            {alerts.length === 0 && (
              <p className="text-dark-400 text-sm">No alerts configured yet. Create one to get started.</p>
            )}
            {alerts.map(alert => (
              <div
                key={alert.id}
                className="bg-dark-800 rounded-xl p-4 border border-dark-700 flex items-center justify-between"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-white font-medium">{alert.name}</h3>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      alert.enabled ? 'bg-green-900/60 text-green-300' : 'bg-dark-600 text-dark-400'
                    }`}>
                      {alert.enabled ? 'Active' : 'Paused'}
                    </span>
                  </div>
                  <p className="text-dark-400 text-sm mt-1">
                    Keyword: <span className="text-primary-300">{alert.keyword}</span>
                    {' · '}Frequency: {alert.frequency}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => toggleAlert(alert)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                      alert.enabled
                        ? 'bg-yellow-900/50 text-yellow-300 hover:bg-yellow-800/50'
                        : 'bg-green-900/50 text-green-300 hover:bg-green-800/50'
                    }`}
                  >
                    {alert.enabled ? 'Pause' : 'Activate'}
                  </button>
                  <button
                    onClick={() => deleteAlert(alert.id)}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium bg-red-900/50 text-red-300 hover:bg-red-800/50 transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === 'events' && (
        <div className="bg-dark-800 rounded-xl border border-dark-700">
          {events.length === 0 ? (
            <div className="p-6 text-center text-dark-400 text-sm">No alert events yet. Events will appear here when alerts trigger.</div>
          ) : (
            <div className="divide-y divide-dark-700">
              {events.map((event, idx) => (
                <div key={idx} className="px-5 py-3 flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-primary-500 mt-2 shrink-0" />
                  <div>
                    <p className="text-white text-sm">{event.message}</p>
                    <p className="text-dark-500 text-xs mt-0.5">{event.timestamp}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AlertCenter;
