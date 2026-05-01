import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { auth } from '../services/api';

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const res = await auth.login(username, password);
      localStorage.setItem('token', res.data.access_token);
      navigate('/search');
    } catch {
      setError('Invalid credentials');
    }
  };

  return (
    <div className="min-h-screen bg-dark-900 flex items-center justify-center">
      <div className="bg-dark-800 p-8 rounded-xl w-96 border border-dark-700">
        <div className="text-center mb-6">
          <div className="text-3xl mb-2">🔬</div>
          <h1 className="text-white text-xl font-semibold">Life Science Data</h1>
          <p className="text-dark-400 text-sm">Sign in to continue</p>
        </div>
        {error && <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-3 py-2 rounded-lg text-sm mb-4">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div><input type="text" placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} className="w-full bg-dark-900 border border-dark-600 rounded-lg px-3 py-2 text-white placeholder-dark-400 focus:border-primary-500 focus:outline-none" /></div>
          <div><input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} className="w-full bg-dark-900 border border-dark-600 rounded-lg px-3 py-2 text-white placeholder-dark-400 focus:border-primary-500 focus:outline-none" /></div>
          <button type="submit" className="w-full bg-primary-600 hover:bg-primary-500 text-white font-medium py-2 rounded-lg transition-colors">Sign In</button>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;
