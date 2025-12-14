import { AppSettings, Category, CategoryAdmin, Product, ProductAdmin, Table, OrderPayload, OrderView, ReportStats, SalesData } from '../types';

type ApiError = Error & { status?: number; payload?: unknown };

const API_BASE = '/api';

export type OrderCreateResponse = {
  success: boolean;
  message: string;
  order_id?: number;
  total?: number;
  print_jobs?: { id: number; type: string; status: string }[];
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  });

  const contentType = res.headers.get('content-type') || '';
  const isJson = contentType.includes('application/json');
  const payload = isJson ? await res.json().catch(() => null) : await res.text().catch(() => null);

  if (!res.ok) {
    const err: ApiError = new Error(typeof payload === 'string' ? payload : 'API request failed');
    err.status = res.status;
    err.payload = payload;
    throw err;
  }

  return payload as T;
}

export const ApiService = {
  getTables: async (): Promise<Table[]> => request<Table[]>('/tables'),

  getCategories: async (): Promise<Category[]> => request<Category[]>('/categories'),

  getProducts: async (categoryId?: number): Promise<Product[]> => {
    const query = categoryId ? `?category_id=${encodeURIComponent(String(categoryId))}` : '';
    return request<Product[]>(`/products${query}`);
  },

  submitOrder: async (payload: OrderPayload): Promise<OrderCreateResponse> =>
    request<OrderCreateResponse>('/orders', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  getDailyStats: async (): Promise<ReportStats> => request<ReportStats>('/reports/daily/stats'),

  getSalesData: async (): Promise<SalesData[]> => request<SalesData[]>('/reports/daily/sales'),

  getOrders: async (paymentStatus?: 'PAID' | 'PENDING'): Promise<OrderView[]> => {
    const q = paymentStatus ? `?payment_status=${encodeURIComponent(paymentStatus)}` : '';
    return request<OrderView[]>(`/orders${q}`);
  },

  updateOrder: async (orderId: number, patch: { status?: string; payment_status?: 'PAID' | 'PENDING' }): Promise<OrderView> =>
    request<OrderView>(`/orders/${orderId}`, { method: 'PATCH', body: JSON.stringify(patch) }),

  getAppSettings: async (): Promise<AppSettings> => request<AppSettings>('/settings/app'),

  updateAppSettings: async (payload: AppSettings): Promise<AppSettings> =>
    request<AppSettings>('/settings/app', { method: 'PUT', body: JSON.stringify(payload) }),

  adminListCategories: async (): Promise<CategoryAdmin[]> => request<CategoryAdmin[]>('/admin/categories'),

  adminCreateCategory: async (payload: { name: string; sort_order: number; is_active: boolean }): Promise<CategoryAdmin> =>
    request<CategoryAdmin>('/admin/categories', { method: 'POST', body: JSON.stringify(payload) }),

  adminUpdateCategory: async (
    categoryId: number,
    payload: { name: string; sort_order: number; is_active: boolean }
  ): Promise<CategoryAdmin> => request<CategoryAdmin>(`/admin/categories/${categoryId}`, { method: 'PUT', body: JSON.stringify(payload) }),

  adminListProducts: async (): Promise<ProductAdmin[]> => request<ProductAdmin[]>('/admin/products'),

  adminCreateProduct: async (payload: {
    category_id: number;
    name: string;
    price: number;
    is_active: boolean;
    image_url?: string | null;
    sku?: string | null;
  }): Promise<ProductAdmin> => request<ProductAdmin>('/admin/products', { method: 'POST', body: JSON.stringify(payload) }),

  adminUpdateProduct: async (
    productId: number,
    payload: {
      category_id: number;
      name: string;
      price: number;
      is_active: boolean;
      image_url?: string | null;
      sku?: string | null;
    }
  ): Promise<ProductAdmin> => request<ProductAdmin>(`/admin/products/${productId}`, { method: 'PUT', body: JSON.stringify(payload) }),
};
