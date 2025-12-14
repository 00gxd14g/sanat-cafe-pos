import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { User, Receipt, ChartBar, RefreshCw, ShoppingBag, ListOrdered, Settings, Tags, Bug } from 'lucide-react';
import { ApiService } from '../services/api';
import { Table, TableStatus } from '../types';

const DashboardScreen: React.FC = () => {
  const [tables, setTables] = useState<Table[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchTables = async () => {
    setLoading(true);
    try {
      const data = await ApiService.getTables();
      setTables(data);
    } catch (error) {
      console.error('Failed to fetch tables', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTables();
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-orange-600 p-2 rounded-lg">
              <Receipt className="text-white w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">
              Özlüce Sanat <span className="text-orange-600">POS</span>
            </h1>
          </div>
          <div className="flex gap-3">
            <Link
              to="/pos"
              className="flex items-center gap-2 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors shadow-sm"
            >
              <ShoppingBag className="w-5 h-5" />
              <span className="hidden sm:inline">Hızlı Sipariş</span>
            </Link>
            <Link
              to="/admin/orders"
              className="flex items-center gap-2 bg-white border border-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors shadow-sm"
            >
              <ListOrdered className="w-5 h-5" />
              <span className="hidden sm:inline">Siparişler</span>
            </Link>
            <Link
              to="/admin/products"
              className="flex items-center gap-2 bg-white border border-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors shadow-sm"
            >
              <Tags className="w-5 h-5" />
              <span className="hidden sm:inline">Ürünler</span>
            </Link>
            <Link
              to="/admin/settings"
              className="flex items-center gap-2 bg-white border border-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors shadow-sm"
            >
              <Settings className="w-5 h-5" />
              <span className="hidden sm:inline">Ayarlar</span>
            </Link>
            <Link
              to="/admin/debug"
              className="flex items-center gap-2 bg-white border border-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors shadow-sm"
            >
              <Bug className="w-5 h-5" />
              <span className="hidden sm:inline">Debug</span>
            </Link>
            <button
              onClick={fetchTables}
              className="p-2 text-gray-500 hover:text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
              title="Yenile"
            >
              <RefreshCw className={`w-6 h-6 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <Link
              to="/admin/reports"
              className="flex items-center gap-2 bg-gray-800 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors shadow-sm"
            >
              <ChartBar className="w-5 h-5" />
              <span className="hidden sm:inline">Raporlar</span>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto w-full p-4 sm:p-6 lg:p-8">
        <div className="mb-6 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-gray-700">Masa Durumları</h2>
          <div className="flex gap-4 text-sm">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-green-500"></span>
              <span className="text-gray-600">Boş</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-red-500"></span>
              <span className="text-gray-600">Dolu</span>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 animate-pulse">
            {[...Array(10)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-xl"></div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 sm:gap-6">
            {tables.map((table) => (
              <Link
                key={table.id}
                to={`/pos/${table.id}`}
                className={`relative group flex flex-col items-center justify-center h-32 sm:h-40 rounded-xl border-2 transition-all duration-200 shadow-sm hover:shadow-md active:scale-95 ${
                  table.status === TableStatus.EMPTY
                    ? 'bg-white border-green-200 hover:border-green-400'
                    : 'bg-red-50 border-red-200 hover:border-red-400'
                }`}
              >
                <div
                  className={`p-3 rounded-full mb-2 ${
                    table.status === TableStatus.EMPTY ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'
                  }`}
                >
                  {table.status === TableStatus.EMPTY ? <User className="w-6 h-6" /> : <Receipt className="w-6 h-6" />}
                </div>
                <span className="font-bold text-gray-800 text-lg">{table.name}</span>
                {table.status === TableStatus.OCCUPIED && (
                  <span className="text-sm font-medium text-red-600 mt-1">{table.total_amount} TL</span>
                )}
                {table.status === TableStatus.EMPTY && (
                  <span className="text-xs text-green-600 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    Sipariş Oluştur
                  </span>
                )}
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default DashboardScreen;
