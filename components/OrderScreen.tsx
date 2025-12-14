import React, { useEffect, useMemo, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ChevronLeft, Plus, Minus, Trash2, Printer, Search } from 'lucide-react';
import { ApiService } from '../services/api';
import { Category, Product, CartItem } from '../types';
import Modal from './Modal';
import { printFromJobId } from '../services/qz';

const OrderScreen: React.FC = () => {
  const { tableId } = useParams<{ tableId: string }>();
  const navigate = useNavigate();

  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loadingProducts, setLoadingProducts] = useState(false);

  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [isPaid, setIsPaid] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [printStrategy, setPrintStrategy] = useState<'server' | 'qz'>('server');

  const [modalState, setModalState] = useState<{ open: boolean; type: 'success' | 'error'; message: string }>({
    open: false,
    type: 'success',
    message: '',
  });

  useEffect(() => {
    const init = async () => {
      try {
        const cats = await ApiService.getCategories();
        const allCategory: Category = { id: 0, name: 'Tümü' };
        setCategories([allCategory, ...cats]);
        setSelectedCategory(0);
      } catch (e) {
        console.error('Init failed', e);
      }
    };
    init();
  }, []);

  useEffect(() => {
    ApiService.getAppSettings()
      .then((s) => setPrintStrategy((String(s.print_strategy).toLowerCase() as any) === 'qz' ? 'qz' : 'server'))
      .catch(() => null);
  }, []);

  useEffect(() => {
    if (selectedCategory !== null) {
      setLoadingProducts(true);
      ApiService.getProducts(selectedCategory === 0 ? undefined : selectedCategory).then((data) => {
        setProducts(data);
        setLoadingProducts(false);
      });
    }
  }, [selectedCategory]);

  const cartTotal = useMemo(() => cart.reduce((sum, item) => sum + item.price * item.quantity, 0), [cart]);

  const filteredProducts = products.filter((p) => p.name.toLowerCase().includes(searchTerm.toLowerCase()));

  const addToCart = (product: Product) => {
    setCart((prev) => {
      const existing = prev.find((item) => item.id === product.id);
      if (existing) {
        return prev.map((item) => (item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item));
      }
      return [...prev, { ...product, quantity: 1 }];
    });
  };

  const removeFromCart = (productId: number) => {
    setCart((prev) => prev.filter((item) => item.id !== productId));
  };

  const updateQuantity = (productId: number, delta: number) => {
    setCart((prev) =>
      prev.map((item) => {
        if (item.id === productId) {
          const newQty = item.quantity + delta;
          return newQty > 0 ? { ...item, quantity: newQty } : item;
        }
        return item;
      }),
    );
  };

  const handleSubmit = async () => {
    if (cart.length === 0) return;

    setIsSubmitting(true);
    try {
      const result = await ApiService.submitOrder({
        table_id: tableId ? Number(tableId) : 0,
        payment_status: isPaid ? 'PAID' : 'PENDING',
        items: cart.map((i) => ({ product_id: i.id, quantity: i.quantity, price: i.price })),
      });

      setModalState({
        open: true,
        type: 'success',
        message: 'Sipariş başarıyla oluşturuldu. Fiş yazdırılıyor...',
      });

      if (printStrategy === 'qz') {
        const printJobs = result.print_jobs || [];
        for (const job of printJobs) {
          printFromJobId(job.id).catch(() => null);
        }
      }

      setTimeout(() => {
        navigate('/');
      }, 2000);
    } catch (error) {
      setModalState({
        open: true,
        type: 'error',
        message: 'Sunucu hatası! Lütfen bağlantınızı kontrol edin.',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-gray-100">
      <Modal
        isOpen={modalState.open}
        type={modalState.type}
        title={modalState.type === 'success' ? 'Başarılı' : 'Hata'}
        message={modalState.message}
        onClose={() => setModalState({ ...modalState, open: false })}
        autoClose={modalState.type === 'success' ? 2000 : undefined}
      />

      {/* LEFT SIDE: MENU */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <div className="bg-white p-4 shadow-sm flex items-center justify-between shrink-0">
          <div className="flex items-center gap-4">
            <Link to="/" className="p-2 hover:bg-gray-100 rounded-full transition-colors">
              <ChevronLeft className="w-6 h-6 text-gray-600" />
            </Link>
            <h1 className="text-xl font-bold text-gray-800">Menü Seçimi</h1>
          </div>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Ürün ara..."
              className="pl-10 pr-4 py-2 bg-gray-100 rounded-full focus:outline-none focus:ring-2 focus:ring-orange-500 w-64 transition-all"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div className="bg-white border-b overflow-x-auto scrollbar-hide shrink-0">
          <div className="flex px-4 py-2 gap-2 min-w-max">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`px-6 py-3 rounded-full text-sm font-semibold transition-all whitespace-nowrap ${
                  selectedCategory === cat.id
                    ? 'bg-orange-600 text-white shadow-md transform scale-105'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {cat.name}
              </button>
            ))}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 bg-gray-100">
          {loadingProducts ? (
            <div className="flex items-center justify-center h-full text-gray-400">Yükleniyor...</div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 pb-24">
              {filteredProducts.map((product) => (
                <div
                  key={product.id}
                  onClick={() => addToCart(product)}
                  className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md cursor-pointer transition-all active:scale-95 flex flex-col items-center text-center border border-transparent hover:border-orange-200"
                >
                  <img
                    src={product.image}
                    alt={product.name}
                    className="w-24 h-24 rounded-full object-cover mb-3 bg-gray-200"
                  />
                  <h3 className="font-semibold text-gray-800 mb-1 line-clamp-2">{product.name}</h3>
                  <span className="text-orange-600 font-bold">{product.price} TL</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* RIGHT SIDE: CART */}
      <div className="w-96 bg-white shadow-2xl flex flex-col h-full border-l border-gray-200 shrink-0 z-20">
        <div className="p-5 border-b bg-gray-50 flex justify-between items-center">
          <div>
            <h2 className="text-lg font-bold text-gray-800">Sipariş Özeti</h2>
            <span className="text-sm text-gray-500">{tableId ? `Masa ${tableId}` : 'Paket Servis'}</span>
          </div>
          <span className="bg-orange-100 text-orange-700 px-3 py-1 rounded-full text-xs font-bold">{cart.length} Ürün</span>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {cart.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-400">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <Search className="w-8 h-8 opacity-50" />
              </div>
              <p>Sepetiniz boş.</p>
              <p className="text-sm">Menüden ürün ekleyin.</p>
            </div>
          ) : (
            cart.map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-100 hover:border-orange-200 transition-colors shadow-sm"
              >
                <div className="flex-1 min-w-0 pr-4">
                  <h4 className="font-medium text-gray-800 truncate">{item.name}</h4>
                  <div className="text-xs text-gray-500">{item.price} TL</div>
                </div>

                <div className="flex items-center gap-3">
                  <button
                    onClick={() => (item.quantity > 1 ? updateQuantity(item.id, -1) : removeFromCart(item.id))}
                    className="w-8 h-8 rounded-full bg-gray-100 hover:bg-red-100 hover:text-red-600 flex items-center justify-center transition-colors"
                  >
                    {item.quantity === 1 ? <Trash2 className="w-4 h-4" /> : <Minus className="w-4 h-4" />}
                  </button>
                  <span className="font-bold w-6 text-center">{item.quantity}</span>
                  <button
                    onClick={() => updateQuantity(item.id, 1)}
                    className="w-8 h-8 rounded-full bg-gray-100 hover:bg-green-100 hover:text-green-600 flex items-center justify-center transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
                <div className="w-16 text-right font-semibold text-gray-700">{item.price * item.quantity} TL</div>
              </div>
            ))
          )}
        </div>

        <div className="p-5 bg-gray-50 border-t border-gray-200">
          <div className="flex justify-between items-center mb-4">
            <span className="text-gray-600">Toplam Tutar</span>
            <span className="text-3xl font-bold text-gray-900">{cartTotal} TL</span>
          </div>

          <div className="flex items-center justify-between mb-6 bg-white p-3 rounded-lg border border-gray-200">
            <span className="text-sm font-medium text-gray-700">Nakit Tahsil Edildi</span>
            <button
              onClick={() => setIsPaid(!isPaid)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                isPaid ? 'bg-green-500' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  isPaid ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          <button
            onClick={handleSubmit}
            disabled={cart.length === 0 || isSubmitting}
            className={`w-full py-4 rounded-xl flex items-center justify-center gap-2 text-lg font-bold shadow-lg transition-all ${
              cart.length === 0 || isSubmitting
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-green-600 text-white hover:bg-green-700 active:scale-95 hover:shadow-xl'
            }`}
          >
            {isSubmitting ? (
              <span className="animate-pulse">Yükleniyor...</span>
            ) : (
              <>
                <Printer className="w-6 h-6" />
                <span>Onayla ve Yazdır</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default OrderScreen;
