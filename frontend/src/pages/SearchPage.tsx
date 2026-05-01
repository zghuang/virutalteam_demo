import React, { useState } from 'react';
import { search as searchAPI } from '../services/api';

interface SearchResult {
  id: number;
  title: string;
  content: string;
  source_name: string;
  category: string;
  source_weight: number;
  published_at: string;
  similarity?: number;
}

const SearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState<'keyword' | 'semantic'>('keyword');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({ category: '', source: '', date_from: '', date_to: '' });

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = mode === 'keyword'
        ? await searchAPI.keyword({ q: query, ...filters })
        : await searchAPI.semantic(query);
      setResults(res.data.results || res.data || []);
    } catch { /* ignore */ }
    setLoading(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => { if (e.key === 'Enter') handleSearch(); };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Search bar */}
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-white mb-4">Search Life Science Data</h1>
        <div className="flex gap-2">
          <input type="text" value={query} onChange={e => setQuery(e.target.value)} onKeyDown={handleKeyDown}
            placeholder="Search news, financial data, products..." autoFocus
            className="flex-1 bg-dark-800 border border-dark-600 rounded-lg px-4 py-3 text-white placeholder-dark-400 focus:border-primary-500 focus:outline-none text-lg" />
          <button onClick={handleSearch} disabled={loading}
            className="bg-primary-600 hover:bg-primary-500 text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50">
            {loading ? '...' : 'Search'}
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-6 flex-wrap">
        <select value={mode} onChange={e => setMode(e.target.value as any)} className="bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-white">
          <option value="keyword">🔍 Keyword</option>
          <option value="semantic">🧠 Semantic</option>
        </select>
        <input type="text" placeholder="Category" value={filters.category} onChange={e => setFilters({ ...filters, category: e.target.value })}
          className="bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-white placeholder-dark-400 w-32 focus:border-primary-500 focus:outline-none" />
        <input type="date" value={filters.date_from} onChange={e => setFilters({ ...filters, date_from: e.target.value })}
          className="bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-white" />
        <input type="date" value={filters.date_to} onChange={e => setFilters({ ...filters, date_to: e.target.value })}
          className="bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-white" />
      </div>

      {/* Results */}
      <div className="space-y-3">
        {results.map((r, i) => (
          <div key={r.id || i} className="bg-dark-800 border border-dark-700 rounded-lg p-4 hover:border-dark-500 transition-colors">
            <div className="flex items-start justify-between mb-2">
              <h3 className="text-white font-medium">{r.title}</h3>
              <span className="text-xs px-2 py-0.5 rounded bg-dark-700 text-dark-300">{r.category}</span>
            </div>
            <p className="text-dark-400 text-sm mb-2 line-clamp-2">{r.content}</p>
            <div className="flex items-center gap-3 text-xs text-dark-500">
              <span>📰 {r.source_name}</span>
              <span>⭐ {r.source_weight}/10</span>
              <span>{r.published_at}</span>
              {r.similarity && <span>🎯 {(r.similarity * 100).toFixed(0)}%</span>}
            </div>
          </div>
        ))}
        {!loading && results.length === 0 && query && <p className="text-dark-500 text-center py-8">No results found.</p>}
      </div>
    </div>
  );
};

export default SearchPage;
