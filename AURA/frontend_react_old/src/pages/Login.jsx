import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Lock, Mail } from 'lucide-react';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(true);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    // Placeholder auth; auto-redirect to dashboard
    setTimeout(() => {
      setLoading(false);
      navigate('/');
    }, 600);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0b1326] via-[#0f172a] to-[#05080f] text-white flex items-center justify-center p-6">
      <div className="w-full max-w-4xl grid grid-cols-1 lg:grid-cols-2 gap-8 bg-white/5 border border-white/10 rounded-2xl shadow-2xl shadow-blue-900/20 overflow-hidden">
        <div className="p-10 space-y-8 bg-[radial-gradient(circle_at_20%_20%,rgba(75,226,119,0.08),transparent_35%),radial-gradient(circle_at_80%_30%,rgba(59,130,246,0.08),transparent_35%)]">
          <div className="flex items-center gap-3">
            <div className="bg-[#4be277] text-[#0b1326] p-3 rounded-xl shadow-lg shadow-[#4be277]/40">
              <Shield className="w-6 h-6" />
            </div>
            <div>
              <p className="text-[10px] tracking-[0.3em] uppercase text-[#8fb3ff] font-black">AURA Command</p>
              <p className="text-lg font-black text-white">Secure Access Portal</p>
            </div>
          </div>
          <div className="space-y-3 text-sm text-white/70 leading-relaxed">
            <p>Authenticate to access live drone telemetry, hazard analytics, and mission reports.</p>
            <p className="text-white/50">All activity is monitored. Use your assigned mission credentials.</p>
          </div>
          <div className="grid grid-cols-2 gap-3 text-[11px] font-mono text-white/70">
            <Badge label="TLS 1.3 Active" />
            <Badge label="SOC Link Encrypted" />
            <Badge label="Geo-Fence Enabled" />
            <Badge label="Operator ID Verified" />
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-10 space-y-6 bg-[#0d162b]">
          <div>
            <p className="text-[11px] font-black uppercase tracking-[0.25em] text-[#8fb3ff]">Mission Login</p>
            <p className="text-xl font-bold mt-1">Enter your credentials</p>
          </div>

          <label className="space-y-2 block text-sm">
            <span className="flex items-center gap-2 text-white/70"><Mail className="w-4 h-4" /> Email</span>
            <div className="relative">
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-sm focus:border-[#4be277] focus:ring-2 focus:ring-[#4be277]/30 outline-none"
                placeholder="you@aura.mission"
              />
            </div>
          </label>

          <label className="space-y-2 block text-sm">
            <span className="flex items-center gap-2 text-white/70"><Lock className="w-4 h-4" /> Password</span>
            <div className="relative">
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-sm focus:border-[#4be277] focus:ring-2 focus:ring-[#4be277]/30 outline-none"
                placeholder="••••••••"
              />
            </div>
          </label>

          <div className="flex items-center justify-between text-xs text-white/60">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
                className="h-4 w-4 rounded border-white/30 bg-white/5"
              />
              Remember device
            </label>
            <button type="button" className="text-[#93c5fd] hover:text-white transition">Forgot access?</button>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 bg-[#4be277] text-[#0b1326] font-black uppercase tracking-[0.25em] py-3 rounded-lg hover:translate-y-[-1px] hover:shadow-lg hover:shadow-[#4be277]/40 transition disabled:opacity-60"
          >
            {loading ? 'Authorizing…' : 'Enter Command'}
          </button>

          <p className="text-[11px] text-white/50 text-center">Use valid mission credentials to proceed.</p>
        </form>
      </div>
    </div>
  );
}

function Badge({ label }) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-center">
      {label}
    </div>
  );
}

export default Login;
