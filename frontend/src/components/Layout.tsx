import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

interface LayoutProps { children: React.ReactNode; }

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const handleLogout = () => { localStorage.removeItem('token'); navigate('/login'); };

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/search', label: 'Search', icon: '🔍' },
    { path: '/alerts', label: 'Alerts', icon: '🔔' },
  ];

  return (
    <div className="min-h-screen bg-dark-900 flex">
      <aside className="w-64 bg-dark-800 border-r border-dark-700 p-4 flex flex-col">
        <div className="text-primary-400 text-xl font-bold mb-8">🔬 LifeSci</div>
        <nav className="flex-1 space-y-1">
          {navItems.map(item => (
            <button key={item.path} onClick={() => navigate(item.path)}
              className={`w-full text-left px-3 py-2 rounded-lg font-medium transition-colors ${
                location.pathname === item.path ? 'bg-primary-600/20 text-primary-300' : 'text-dark-300 hover:bg-dark-700'
              }`}>
              {item.icon} {item.label}
            </button>
          ))}
        </nav>
        <button onClick={handleLogout} className="px-3 py-2 text-dark-400 hover:text-white transition-colors">Logout</button>
      </aside>
      <main className="flex-1 p-6 overflow-y-auto">{children}</main>
    </div>
  );
};

export default Layout;
