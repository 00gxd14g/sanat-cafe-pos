import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, RefreshCw, Check, CreditCard } from 'lucide-react';
import { ApiService } from '../services/api';
import { OrderView } from '../types';

function tableLabel(tableId: number | null) {
  return tableId ? `Masa ${tableId}` : 'Paket Servis';
}

const AdminOrdersScreen: React.FC = () => {
  const [orders, setOrders] = useState<OrderView[]>([]);
  const [loading, setLoading] = useState(true);
  const [polling, setPolling] = useState(true);
  const [view, setView] = useState<'PENDING' | 'READY' | 'PAID'>('PENDING');

  const fetchOrders = async () => {
    setLoading(true);
    try {
      if (view === 'PAID') {
        const data = await ApiService.getOrders('PAID');
        setOrders(data);
      } else {
        const data = await ApiService.getOrders('PENDING');
        setOrders(view === 'READY' ? data.filter((o) => o.status === 'READY') : data);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, [view]);

  useEffect(() => {
    if (!polling) return;
    if (view === 'PAID') return;
    const t = setInterval(fetchOrders, 3000);
    return () => clearInterval(t);
  }, [polling, view]);

  const grouped = useMemo(() => {
    const map = new Map<string, OrderView[]>();
    for (const o of orders) {
      const key = String(o.table_id ?? 'takeaway');
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(o);
    }
    return Array.from(map.entries()).sort((a, b) => {
      const ak = a[0] === 'takeaway' ? 999999 : Number(a[0]);
      const bk = b[0] === 'takeaway' ? 999999 : Number(b[0]);
      return ak - bk;
    });
  }, [orders]);

  const markReady = async (orderId: number) => {
    await ApiService.updateOrder(orderId, { status: 'READY' });
    fetchOrders();
  };

  const markPaid = async (orderId: number) => {
    await ApiService.updateOrder(orderId, { payment_status: 'PAID' });
    fetchOrders();
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
              <h1 className="text-2xl font-bold text-gray-800">Açık Siparişler</h1>
              <p className="text-sm text-gray-500">Masaya göre anlık liste</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex bg-white border border-gray-200 rounded-lg overflow-hidden">
              <button
                onClick={() => setView('PENDING')}
                className={`px-4 py-2 text-sm font-semibold ${
                  view === 'PENDING' ? 'bg-gray-800 text-white' : 'text-gray-700'
                }`}
              >
                Açık
              </button>
              <button
                onClick={() => setView('READY')}
                className={`px-4 py-2 text-sm font-semibold ${
                  view === 'READY' ? 'bg-gray-800 text-white' : 'text-gray-700'
                }`}
              >
                Hazır
              </button>
              <button
                onClick={() => setView('PAID')}
                className={`px-4 py-2 text-sm font-semibold ${
                  view === 'PAID' ? 'bg-gray-800 text-white' : 'text-gray-700'
                }`}
              >
                Ödendi
              </button>
            </div>
            <button
              onClick={() => setPolling(!polling)}
              className={`px-4 py-2 rounded-lg text-sm font-semibold border transition-colors ${
                polling ? 'bg-green-50 text-green-700 border-green-200' : 'bg-white text-gray-700 border-gray-200'
              }`}
            >
              Otomatik yenile: {polling ? 'Açık' : 'Kapalı'}
            </button>
            <button
              onClick={fetchOrders}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white border border-gray-200 hover:bg-gray-100 transition-colors"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              Yenile
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-gray-400">Yükleniyor...</div>
        ) : orders.length === 0 ? (
          <div className="bg-white border border-gray-200 rounded-2xl p-8 text-center text-gray-500">
            Açık sipariş yok.
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {grouped.map(([key, list]) => {
              const tableId = key === 'takeaway' ? null : Number(key);
              const total = list.reduce((s, o) => s + o.total, 0);
              return (
                <div key={key} className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden">
                  <div className="p-5 border-b bg-gray-50 flex items-center justify-between">
                    <div>
                      <div className="text-lg font-bold text-gray-800">{tableLabel(tableId)}</div>
                      <div className="text-sm text-gray-500">{list.length} adisyon</div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-gray-500">Toplam</div>
                      <div className="text-xl font-bold text-gray-900">{total} TL</div>
                    </div>
                  </div>

                  <div className="p-4 space-y-4">
                    {list.map((o) => (
                      <div key={o.id} className="border border-gray-100 rounded-xl p-4">
                        <div className="flex items-center justify-between">
                          <div className="font-semibold text-gray-800">Adisyon #{o.id}</div>
                          <div className="text-xs font-bold px-2 py-1 rounded-full bg-orange-100 text-orange-700">
                            {o.status}
                          </div>
                        </div>

                        <div className="mt-3 space-y-2">
                          {o.items.map((it, idx) => (
                            <div key={`${o.id}-${idx}`} className="flex items-center justify-between text-sm">
                              <div className="text-gray-700 truncate pr-3">
                                {it.quantity}x {it.name}
                              </div>
                              <div className="font-medium text-gray-800">{it.line_total} TL</div>
                            </div>
                          ))}
                        </div>

                        <div className="mt-4 flex items-center justify-between">
                          <div className="text-sm text-gray-600">
                            Tutar: <span className="font-bold text-gray-900">{o.total} TL</span>
                          </div>
                          <div className="flex gap-2">
                            <button
                              onClick={() => markReady(o.id)}
                              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 transition-colors"
                            >
                              <Check className="w-4 h-4" />
                              Hazır
                            </button>
                            <button
                              onClick={() => markPaid(o.id)}
                              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-green-600 text-white text-sm font-semibold hover:bg-green-700 transition-colors"
                            >
                              <CreditCard className="w-4 h-4" />
                              Ödendi
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminOrdersScreen;
