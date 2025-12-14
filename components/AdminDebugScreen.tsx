import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, RefreshCw, Bug, Printer } from 'lucide-react';
import { ApiService } from '../services/api';

type AuditRow = {
  id: number;
  created_at: string;
  action: string;
  entity: string;
  entity_id: string;
  message: string;
  payload_json?: string | null;
};

type PrintJobRow = {
  id: number;
  order_id: number;
  job_type: string;
  printer_name: string;
  status: string;
  attempts: number;
  last_error?: string | null;
};

const AdminDebugScreen: React.FC = () => {
  const [tab, setTab] = useState<'print' | 'audit' | 'logs' | 'printers'>('print');
  const [loading, setLoading] = useState(true);

  const [printJobs, setPrintJobs] = useState<PrintJobRow[]>([]);
  const [audit, setAudit] = useState<AuditRow[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [logPath, setLogPath] = useState<string>('');
  const [printers, setPrinters] = useState<any>(null);

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [pj, au, lg, pr] = await Promise.all([
        fetch('/api/print-jobs').then((r) => r.json()),
        fetch('/api/admin/audit?limit=200').then((r) => r.json()),
        fetch('/api/admin/logs?lines=200').then((r) => r.json()),
        fetch('/api/admin/printers').then((r) => r.json()),
      ]);
      setPrintJobs((pj?.value ?? pj) as PrintJobRow[]);
      setAudit(au as AuditRow[]);
      setLogs((lg?.lines ?? []) as string[]);
      setLogPath(String(lg?.path ?? ''));
      setPrinters(pr);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const retryJob = async (id: number) => {
    await fetch(`/api/print-jobs/${id}/retry`, { method: 'POST' });
    fetchAll();
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <Link to="/" className="p-2 bg-white rounded-full shadow-sm hover:bg-gray-100 transition-colors">
              <ArrowLeft className="w-6 h-6 text-gray-700" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Debug</h1>
              <p className="text-sm text-gray-500">Yazıcı/DB işlemleri ve loglar</p>
            </div>
          </div>
          <button
            onClick={fetchAll}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white border border-gray-200 hover:bg-gray-100 transition-colors"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            Yenile
          </button>
        </div>

        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setTab('print')}
            className={`px-4 py-2 rounded-lg text-sm font-semibold ${
              tab === 'print' ? 'bg-gray-800 text-white' : 'bg-white border border-gray-200 text-gray-700'
            }`}
          >
            <span className="inline-flex items-center gap-2">
              <Printer className="w-4 h-4" /> Print Jobs
            </span>
          </button>
          <button
            onClick={() => setTab('audit')}
            className={`px-4 py-2 rounded-lg text-sm font-semibold ${
              tab === 'audit' ? 'bg-gray-800 text-white' : 'bg-white border border-gray-200 text-gray-700'
            }`}
          >
            <span className="inline-flex items-center gap-2">
              <Bug className="w-4 h-4" /> Audit
            </span>
          </button>
          <button
            onClick={() => setTab('logs')}
            className={`px-4 py-2 rounded-lg text-sm font-semibold ${
              tab === 'logs' ? 'bg-gray-800 text-white' : 'bg-white border border-gray-200 text-gray-700'
            }`}
          >
            Backend Logs
          </button>
          <button
            onClick={() => setTab('printers')}
            className={`px-4 py-2 rounded-lg text-sm font-semibold ${
              tab === 'printers' ? 'bg-gray-800 text-white' : 'bg-white border border-gray-200 text-gray-700'
            }`}
          >
            Windows Printers
          </button>
        </div>

        {tab === 'print' && (
          <div className="bg-white border border-gray-200 rounded-2xl p-5 overflow-auto">
            <div className="text-sm text-gray-500 mb-3">/api/print-jobs (son 200)</div>
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500">
                  <th className="py-2">ID</th>
                  <th>Order</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Attempts</th>
                  <th className="w-1/3">Last Error</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {printJobs.map((j) => (
                  <tr key={j.id} className="border-t">
                    <td className="py-2 font-semibold">{j.id}</td>
                    <td>#{j.order_id}</td>
                    <td>{j.job_type}</td>
                    <td>{j.status}</td>
                    <td>{j.attempts}</td>
                    <td className="text-red-700 truncate">{j.last_error || ''}</td>
                    <td className="text-right">
                      <button
                        onClick={() => retryJob(j.id)}
                        className="px-3 py-1 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-800"
                      >
                        Retry
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {tab === 'audit' && (
          <div className="bg-white border border-gray-200 rounded-2xl p-5 overflow-auto">
            <div className="text-sm text-gray-500 mb-3">/api/admin/audit (son 200)</div>
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500">
                  <th className="py-2">ID</th>
                  <th>Time</th>
                  <th>Action</th>
                  <th>Entity</th>
                  <th>Entity ID</th>
                  <th>Message</th>
                </tr>
              </thead>
              <tbody>
                {audit.map((a) => (
                  <tr key={a.id} className="border-t align-top">
                    <td className="py-2 font-semibold">{a.id}</td>
                    <td className="whitespace-nowrap">{a.created_at}</td>
                    <td>{a.action}</td>
                    <td>{a.entity}</td>
                    <td>{a.entity_id}</td>
                    <td className="text-gray-800">
                      <div>{a.message}</div>
                      {a.payload_json ? (
                        <pre className="mt-2 text-xs text-gray-500 whitespace-pre-wrap">{a.payload_json}</pre>
                      ) : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {tab === 'logs' && (
          <div className="bg-white border border-gray-200 rounded-2xl p-5">
            <div className="text-sm text-gray-500 mb-2">{`${
              logPath || 'backend/logs/app.log'
            }`} son 200 satır</div>
            <pre className="text-xs bg-gray-50 border border-gray-200 rounded-xl p-4 max-h-[70vh] overflow-auto">
              {logs.join('\n')}
            </pre>
          </div>
        )}

        {tab === 'printers' && (
          <div className="bg-white border border-gray-200 rounded-2xl p-5">
            <div className="text-sm text-gray-500 mb-3">Windows spooler printer list (pywin32)</div>
            <pre className="text-xs bg-gray-50 border border-gray-200 rounded-xl p-4 overflow-auto">
              {JSON.stringify(printers, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDebugScreen;
