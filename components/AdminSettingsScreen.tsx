import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Save, RefreshCw, PlugZap } from 'lucide-react';
import { ApiService } from '../services/api';
import { AppSettings } from '../types';
import { initQZ } from '../services/qz';
import qz from 'qz-tray';

const AdminSettingsScreen: React.FC = () => {
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [qzStatus, setQzStatus] = useState<'idle' | 'connected' | 'error'>('idle');
  const [printers, setPrinters] = useState<any>(null);
  const [qzError, setQzError] = useState<string | null>(null);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      const s = await ApiService.getAppSettings();
      setSettings(s);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const isQz = (settings?.print_strategy || '').toLowerCase() === 'qz';

  const connectQz = async () => {
    setQzError(null);
    try {
      await initQZ();
      await qz.printers.getDefault(); // bağlantı testi
      const pr = await fetch('/api/admin/printers').then((r) => r.json());
      setPrinters(pr);
      setQzStatus('connected');
    } catch (e) {
      setQzStatus('error');
      setQzError(e instanceof Error ? e.message : String(e));
    }
  };

  const save = async () => {
    if (!settings) return;
    setSaving(true);
    try {
      const saved = await ApiService.updateAppSettings(settings);
      setSettings(saved);
    } finally {
      setSaving(false);
    }
  };

  const printModeOptions = useMemo(() => ['file', 'spooler', 'noop'], []);
  const printStrategyOptions = useMemo(() => ['server', 'qz'], []);

  if (loading || !settings) {
    return <div className="min-h-screen flex items-center justify-center text-gray-400">Yükleniyor...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <Link to="/" className="p-2 bg-white rounded-full shadow-sm hover:bg-gray-100 transition-colors">
              <ArrowLeft className="w-6 h-6 text-gray-700" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Ayarlar</h1>
              <p className="text-sm text-gray-500">Yazıcı, QZ Tray ve çıktı ayarları</p>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={fetchSettings}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white border border-gray-200 hover:bg-gray-100 transition-colors"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              Yenile
            </button>
            <button
              onClick={save}
              disabled={saving}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${
                saving ? 'bg-gray-200 text-gray-500' : 'bg-gray-800 text-white hover:bg-gray-700'
              }`}
            >
              <Save className="w-5 h-5" />
              Kaydet
            </button>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-2xl p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-semibold text-gray-700">Print Strategy</label>
              <select
                value={settings.print_strategy}
                onChange={(e) => setSettings((s) => ({ ...(s as AppSettings), print_strategy: e.target.value }))}
                className="mt-2 w-full px-3 py-2 rounded-lg border border-gray-200"
              >
                {printStrategyOptions.map((o) => (
                  <option key={o} value={o}>
                    {o}
                  </option>
                ))}
              </select>
              <p className="text-xs text-gray-500 mt-2">
                <span className="font-semibold">server</span>: print_jobs + worker.{' '}
                <span className="font-semibold">qz</span>: tarayıcıda QZ Tray ile silent print.
              </p>
            </div>

            <div>
              <label className="text-sm font-semibold text-gray-700">Print Mode (server)</label>
              <select
                value={settings.print_mode}
                onChange={(e) => setSettings((s) => ({ ...(s as AppSettings), print_mode: e.target.value }))}
                className="mt-2 w-full px-3 py-2 rounded-lg border border-gray-200"
              >
                {printModeOptions.map((o) => (
                  <option key={o} value={o}>
                    {o}
                  </option>
                ))}
              </select>
              <p className="text-xs text-gray-500 mt-2">file: çıktıyı dosyaya, spooler: Windows RAW, noop: kapalı.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-semibold text-gray-700">Mutfak Yazıcı Adı</label>
              <input
                value={settings.printer_kitchen_name}
                onChange={(e) => setSettings((s) => ({ ...(s as AppSettings), printer_kitchen_name: e.target.value }))}
                className="mt-2 w-full px-3 py-2 rounded-lg border border-gray-200"
                placeholder="Örn: POS-58"
              />
            </div>
            <div>
              <label className="text-sm font-semibold text-gray-700">Müşteri Yazıcı Adı</label>
              <input
                value={settings.printer_customer_name}
                onChange={(e) => setSettings((s) => ({ ...(s as AppSettings), printer_customer_name: e.target.value }))}
                className="mt-2 w-full px-3 py-2 rounded-lg border border-gray-200"
                placeholder="Örn: POS-58"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label className="flex items-center gap-3 text-sm text-gray-700">
              <input
                type="checkbox"
                checked={settings.kitchen_show_prices}
                onChange={(e) => setSettings((s) => ({ ...(s as AppSettings), kitchen_show_prices: e.target.checked }))}
              />
              Mutfak fişinde fiyat göster
            </label>
            <label className="flex items-center gap-3 text-sm text-gray-700">
              <input
                type="checkbox"
                checked={settings.customer_show_prices}
                onChange={(e) => setSettings((s) => ({ ...(s as AppSettings), customer_show_prices: e.target.checked }))}
              />
              Müşteri fişinde fiyat/toplam göster
            </label>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-semibold text-gray-700">QZ Encoding</label>
              <input
                value={settings.qz_encoding}
                onChange={(e) => setSettings((s) => ({ ...(s as AppSettings), qz_encoding: e.target.value }))}
                className="mt-2 w-full px-3 py-2 rounded-lg border border-gray-200"
                placeholder="CP857"
              />
            </div>

            <div>
              <label className="text-sm font-semibold text-gray-700">Server Output Dir (file mode)</label>
              <input
                value={settings.print_output_dir}
                onChange={(e) => setSettings((s) => ({ ...(s as AppSettings), print_output_dir: e.target.value }))}
                className="mt-2 w-full px-3 py-2 rounded-lg border border-gray-200"
              />
            </div>
          </div>
        </div>

        {isQz && (
          <div className="mt-6 bg-white border border-gray-200 rounded-2xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-gray-800">QZ Tray</h2>
                <p className="text-sm text-gray-500">Tarayıcıda silent print için bağlantı testi</p>
              </div>
              <button
                onClick={connectQz}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-orange-600 text-white font-semibold hover:bg-orange-700 transition-colors"
              >
                <PlugZap className="w-5 h-5" />
                Bağlan ve Yazıcıları Getir
              </button>
            </div>

            <div className="mt-4 text-sm">
              Durum:{' '}
              <span
                className={`font-bold ${
                  qzStatus === 'connected' ? 'text-green-700' : qzStatus === 'error' ? 'text-red-700' : 'text-gray-700'
                }`}
              >
                {qzStatus}
              </span>
              {qzError && <div className="mt-2 text-red-700">{qzError}</div>}
            </div>

            <div className="mt-4">
              <div className="text-sm font-semibold text-gray-700 mb-2">Bulunan Yazıcılar</div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {printers?.printers?.length ? (
                  printers.printers.map((p: string) => (
                    <button
                      key={p}
                      onClick={() =>
                        setSettings((s) => ({ ...(s as AppSettings), printer_customer_name: p, printer_kitchen_name: p }))
                      }
                      className="text-left px-3 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                    >
                      {p}
                    </button>
                  ))
                ) : (
                  <div className="text-gray-400">Henüz listelenmedi.</div>
                )}
              </div>
              <p className="text-xs text-gray-500 mt-3">
                Bir yazıcıya tıkladığında mutfak + müşteri yazıcı adı otomatik doldurulur.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminSettingsScreen;
