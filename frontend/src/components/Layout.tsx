import React from 'react';
import { useNavigate } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-dark-900 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-dark-800 border-r border-dark-700 p-4 flex flex-col">
        <div className="text-primary-400 text-xl font-bold mb-8">🔬 LifeSci</div>
        <nav className="flex-1 space-y-2">
          <button onClick={() => navigate('/search')} className="w-full text-left px-3 py-2 rounded-lg bg-primary-600/20 text-primary-300 font-medium">Search</button>
        </nav>
        <button onClick={handleLogout} className="px-3 py-2 text-dark-400 hover:text-white transition-colors">Logout</button>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-6 overflow-y-auto">{children}</main>
    </div>
  );
};

export default Layout;
