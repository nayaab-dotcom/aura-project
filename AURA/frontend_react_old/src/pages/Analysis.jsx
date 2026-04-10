import React, { useEffect, useRef, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { fetchAllData, exportReport } from '../services/api';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, Tooltip } from 'recharts';
import { RefreshCw, ArrowLeft, Download } from 'lucide-react';

const COLORS = ['#22d3ee', '#fbbf24', '#f87171'];

function Analysis() {
  const [stats, setStats] = useState({});
  const [report, setReport] = useState(null);
  const [loadingStats, setLoadingStats] = useState(true);
  const [loadingReport, setLoadingReport] = useState(true);
  const location = useLocation();
  const reportRef = useRef(null);

  const loadStats = async () => {
    setLoadingStats(true);
    const data = await fetchAllData();
    setStats(data.stats || {});
    setLoadingStats(false);
  };

  const loadReport = async () => {
    setLoadingReport(true);
    const data = await exportReport();
    setReport(data);
    setLoadingReport(false);
  };

  const loadAll = async () => {
    await Promise.all([loadStats(), loadReport()]);
  };

  useEffect(() => {
    loadAll();
    const t = setInterval(loadAll, 5000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    if (location.hash === '#report' && reportRef.current) {
        reportRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [location, reportRef]);

  const riskData = [
    { name: 'High', value: stats.high_risk_cells || 0 },
    { name: 'Medium', value: stats.medium_risk_cells || 0 },
    { name: 'Safe', value: stats.safe_cells || 0 },
  ];

  const barData = [
    { name: 'Survivors', value: stats.survivors_found || 0 },
    { name: 'Coverage %', value: stats.coverage_percent || 0 },
    { name: 'Grid Cells', value: stats.total_cells || 0 },
  ];

  return (
    <div className="min-h-screen bg-[#0b1326] text-white p-8 font-['Inter'] flex flex-col gap-8">
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link to="/" className="flex items-center gap-2 px-3 py-2 bg-white/5 border border-white/10 rounded text-[10px] font-black tracking-[0.2em] hover:bg-white/10 transition-all">
            <ArrowLeft className="w-4 h-4" /> Dashboard
          </Link>
          <h1 className="text-lg font-black tracking-[0.3em] uppercase text-[#93c5fd]">Analysis + Report</h1>
        </div>
        <button onClick={loadAll} className="flex items-center gap-2 px-3 py-2 bg-[#111827] border border-white/10 rounded text-[10px] font-black uppercase tracking-[0.2em] hover:bg-white/5 transition-all">
          <RefreshCw className={`w-4 h-4 ${(loadingStats || loadingReport) ? 'animate-spin' : ''}`} /> Refresh
        </button>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <StatCard label="Coverage" value={`${stats.coverage_percent || 0}%`} hint="Grid explored" />
        <StatCard label="Survivors Found" value={stats.survivors_found || 0} hint="Detected life signs" />
        <StatCard label="High Risk Cells" value={stats.high_risk_cells || 0} hint="Temp/Gas above threshold" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-[#0f172a] border border-white/10 rounded-xl p-6 shadow-lg">
          <h3 className="text-[10px] font-black uppercase tracking-[0.25em] text-[#93c5fd] mb-4">Risk Composition</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={riskData} dataKey="value" nameKey="name" innerRadius={60} outerRadius={90} paddingAngle={3}>
                  {riskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-[#0f172a] border border-white/10 rounded-xl p-6 shadow-lg">
          <h3 className="text-[10px] font-black uppercase tracking-[0.25em] text-[#93c5fd] mb-4">Mission Snapshot</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData}>
                <XAxis dataKey="name" tick={{ fill: '#cbd5e1', fontSize: 10 }} />
                <Tooltip />
                <Bar dataKey="value" radius={[6, 6, 0, 0]} fill="#22d3ee" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div ref={reportRef} className="bg-[#0f172a] border border-white/10 rounded-xl p-6 shadow-lg space-y-4" id="report">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[10px] font-black uppercase tracking-[0.25em] text-[#f8fafc]">Mission Report</p>
            <p className="text-xs text-white/60">Live snapshot + downloadable JSON</p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={loadReport} className="flex items-center gap-2 px-3 py-2 bg-[#111827] border border-white/10 rounded text-[10px] font-black uppercase tracking-[0.2em] hover:bg-white/5 transition-all">
              <RefreshCw className={`w-4 h-4 ${loadingReport ? 'animate-spin' : ''}`} /> Refresh
            </button>
            <button
              onClick={() => downloadReport(report)}
              className="flex items-center gap-2 px-3 py-2 bg-[#4be277]/10 border border-[#4be277]/30 text-[#4be277] rounded text-[10px] font-black uppercase tracking-[0.2em] hover:bg-[#4be277]/20 transition-all"
            >
              <Download className="w-4 h-4" /> Save JSON
            </button>
          </div>
        </div>

        {loadingReport && <p className="text-sm text-white/60">Loading report...</p>}
        {!loadingReport && !report && <p className="text-sm text-red-400">Unable to load report.</p>}
        {report && (
          <>
            <div className="grid grid-cols-1 md/grid-cols-3 gap-4 text-sm font-mono">
              <Info label="Mission" value={report.mission_id || 'N/A'} />
              <Info label="Survivors Found" value={report.survivors_found || 0} />
              <Info label="Coverage %" value={report.coverage_percent || 0} />
            </div>
            <pre className="bg-black/40 border border-white/10 rounded-lg p-4 text-xs overflow-auto max-h-[50vh] whitespace-pre-wrap">
{JSON.stringify(report, null, 2)}
            </pre>
          </>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, hint }) {
  return (
    <div className="bg-gradient-to-br from-[#111827] via-[#0f172a] to-[#0b1326] border border-white/10 rounded-xl p-5 shadow-lg">
      <p className="text-[9px] uppercase tracking-[0.25em] text-[#94a3b8] mb-2">{label}</p>
      <p className="text-3xl font-black text-white">{value}</p>
      <p className="text-[10px] text-white/60 mt-1">{hint}</p>
    </div>
  );
}

function Info({ label, value }) {
  return (
    <div className="bg-white/5 rounded p-3 border border-white/10">
      <p className="text-[10px] uppercase tracking-[0.25em] text-white/50">{label}</p>
      <p className="text-lg font-black text-white mt-1">{value}</p>
    </div>
  );
}

function downloadReport(report) {
  if (!report) return;
  const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `AURA_REPORT_${report.mission_id || 'latest'}.json`;
  a.click();
}

export default Analysis;
