import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Plus, Save, RefreshCw } from 'lucide-react';
import { ApiService } from '../services/api';
import { CategoryAdmin, ProductAdmin } from '../types';

const AdminProductsScreen: React.FC = () => {
  const [categories, setCategories] = useState<CategoryAdmin[]>([]);
  const [products, setProducts] = useState<ProductAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingId, setSavingId] = useState<number | null>(null);
  const [filterCategory, setFilterCategory] = useState<number | 'all'>('all');

  const [newProduct, setNewProduct] = useState({
    category_id: 1,
    name: '',
    price: 0,
    is_active: true,
    image_url: '',
    sku: '',
  });

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [cats, prods] = await Promise.all([ApiService.adminListCategories(), ApiService.adminListProducts()]);
      setCategories(cats);
      setProducts(prods);
      if (cats.length && newProduct.category_id === 1) {
        setNewProduct((p) => ({ ...p, category_id: cats[0].id }));
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const filtered = useMemo(() => {
    if (filterCategory === 'all') return products;
    return products.filter((p) => p.category_id === filterCategory);
  }, [products, filterCategory]);

  const updateLocal = (id: number, patch: Partial<ProductAdmin>) => {
    setProducts((prev) => prev.map((p) => (p.id === id ? { ...p, ...patch } : p)));
  };

  const saveProduct = async (p: ProductAdmin) => {
    setSavingId(p.id);
    try {
      const saved = await ApiService.adminUpdateProduct(p.id, {
        category_id: p.category_id,
        name: p.name,
        price: Number(p.price),
        is_active: p.is_active,
        image_url: p.image_url ?? null,
        sku: p.sku ?? null,
      });
      updateLocal(p.id, saved);
    } finally {
      setSavingId(null);
    }
  };

  const createProduct = async () => {
    if (!newProduct.name.trim()) return;
    const created = await ApiService.adminCreateProduct({
      category_id: newProduct.category_id,
      name: newProduct.name.trim(),
      price: Number(newProduct.price),
      is_active: newProduct.is_active,
      image_url: newProduct.image_url ? newProduct.image_url : null,
      sku: newProduct.sku ? newProduct.sku : null,
    });
    setProducts((prev) => [created, ...prev]);
    setNewProduct((p) => ({ ...p, name: '', price: 0, sku: '', image_url: '' }));
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
              <h1 className="text-2xl font-bold text-gray-800">Ürün ve Fiyat Yönetimi</h1>
              <p className="text-sm text-gray-500">Kategori/ürün güncelle</p>
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

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-white border border-gray-200 rounded-2xl p-5">
            <h2 className="text-lg font-bold text-gray-800 mb-4">Yeni Ürün</h2>
            <div className="space-y-3">
              <select
                value={newProduct.category_id}
                onChange={(e) => setNewProduct((p) => ({ ...p, category_id: Number(e.target.value) }))}
                className="w-full px-3 py-2 rounded-lg border border-gray-200"
              >
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
              <input
                value={newProduct.name}
                onChange={(e) => setNewProduct((p) => ({ ...p, name: e.target.value }))}
                placeholder="Ürün adı"
                className="w-full px-3 py-2 rounded-lg border border-gray-200"
              />
              <input
                value={newProduct.price}
                onChange={(e) => setNewProduct((p) => ({ ...p, price: Number(e.target.value) }))}
                type="number"
                min={0}
                step={0.01}
                placeholder="Fiyat"
                className="w-full px-3 py-2 rounded-lg border border-gray-200"
              />
              <input
                value={newProduct.sku}
                onChange={(e) => setNewProduct((p) => ({ ...p, sku: e.target.value }))}
                placeholder="SKU (opsiyonel)"
                className="w-full px-3 py-2 rounded-lg border border-gray-200"
              />
              <input
                value={newProduct.image_url}
                onChange={(e) => setNewProduct((p) => ({ ...p, image_url: e.target.value }))}
                placeholder="Resim URL (opsiyonel)"
                className="w-full px-3 py-2 rounded-lg border border-gray-200"
              />
              <label className="flex items-center gap-2 text-sm text-gray-700">
                <input
                  type="checkbox"
                  checked={newProduct.is_active}
                  onChange={(e) => setNewProduct((p) => ({ ...p, is_active: e.target.checked }))}
                />
                Aktif
              </label>
              <button
                onClick={createProduct}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-orange-600 text-white font-semibold hover:bg-orange-700 transition-colors"
              >
                <Plus className="w-5 h-5" />
                Ekle
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 bg-white border border-gray-200 rounded-2xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-gray-800">Ürünler</h2>
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value === 'all' ? 'all' : Number(e.target.value))}
                className="px-3 py-2 rounded-lg border border-gray-200"
              >
                <option value="all">Tümü</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            {loading ? (
              <div className="text-gray-400">Yükleniyor...</div>
            ) : (
              <div className="space-y-3">
                {filtered.map((p) => (
                  <div key={p.id} className="border border-gray-100 rounded-xl p-4">
                    <div className="grid grid-cols-1 md:grid-cols-6 gap-3 items-center">
                      <div className="md:col-span-2">
                        <input
                          value={p.name}
                          onChange={(e) => updateLocal(p.id, { name: e.target.value })}
                          className="w-full px-3 py-2 rounded-lg border border-gray-200"
                        />
                        <div className="text-xs text-gray-400 mt-1">ID: {p.id}</div>
                      </div>
                      <div>
                        <input
                          value={p.price}
                          onChange={(e) => updateLocal(p.id, { price: Number(e.target.value) })}
                          type="number"
                          min={0}
                          step={0.01}
                          className="w-full px-3 py-2 rounded-lg border border-gray-200"
                        />
                        <div className="text-xs text-gray-400 mt-1">Fiyat (TL)</div>
                      </div>
                      <div>
                        <select
                          value={p.category_id}
                          onChange={(e) => updateLocal(p.id, { category_id: Number(e.target.value) })}
                          className="w-full px-3 py-2 rounded-lg border border-gray-200"
                        >
                          {categories.map((c) => (
                            <option key={c.id} value={c.id}>
                              {c.name}
                            </option>
                          ))}
                        </select>
                        <div className="text-xs text-gray-400 mt-1">Kategori</div>
                      </div>
                      <div>
                        <input
                          value={p.sku || ''}
                          onChange={(e) => updateLocal(p.id, { sku: e.target.value })}
                          className="w-full px-3 py-2 rounded-lg border border-gray-200"
                          placeholder="SKU"
                        />
                      </div>
                      <div>
                        <label className="flex items-center gap-2 text-sm text-gray-700">
                          <input
                            type="checkbox"
                            checked={p.is_active}
                            onChange={(e) => updateLocal(p.id, { is_active: e.target.checked })}
                          />
                          Aktif
                        </label>
                      </div>
                      <div className="text-right">
                        <button
                          onClick={() => saveProduct(p)}
                          disabled={savingId === p.id}
                          className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-semibold transition-colors ${
                            savingId === p.id
                              ? 'bg-gray-200 text-gray-500'
                              : 'bg-orange-600 text-white hover:bg-orange-700'
                          }`}
                        >
                          <Save className="w-4 h-4" />
                          Kaydet
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminProductsScreen;
