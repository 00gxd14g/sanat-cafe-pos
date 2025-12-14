import { Table, TableStatus, Category, Product, ReportStats, SalesData } from './types';

export const MOCK_TABLES: Table[] = Array.from({ length: 20 }, (_, i) => ({
  id: i + 1,
  name: `Masa ${i + 1}`,
  status: Math.random() > 0.7 ? TableStatus.OCCUPIED : TableStatus.EMPTY,
  total_amount: Math.random() > 0.7 ? Math.floor(Math.random() * 500) + 50 : 0,
}));

export const MOCK_CATEGORIES: Category[] = [
  { id: 1, name: 'Tost Çeşitleri' },
  { id: 2, name: 'Sandviçler' },
  { id: 3, name: 'İçecekler' },
];

export const MOCK_PRODUCTS: Product[] = [
  // Tost Çeşitleri
  {
    id: 101,
    category_id: 1,
    name: 'Karışık Tost',
    price: 120,
    image: 'https://images.unsplash.com/photo-1584771145729-0bd9fda6529b?auto=format&fit=crop&w=300&q=80',
  },
  {
    id: 102,
    category_id: 1,
    name: 'Sucuklu Tost',
    price: 100,
    image: 'https://images.unsplash.com/photo-1626078297492-b7c125d0452d?auto=format&fit=crop&w=300&q=80',
  },

  // Sandviçler
  {
    id: 201,
    category_id: 2,
    name: 'Sosisli Patso',
    price: 140,
    image: 'https://images.unsplash.com/photo-1627308595229-7830a5c91f9f?auto=format&fit=crop&w=300&q=80',
  },
  {
    id: 202,
    category_id: 2,
    name: 'Köfte Ekmek',
    price: 200,
    image: 'https://images.unsplash.com/photo-1521390188846-e2a3a97453a0?auto=format&fit=crop&w=300&q=80',
  },

  // İçecekler
  {
    id: 301,
    category_id: 3,
    name: 'Çay',
    price: 20,
    image: 'https://images.unsplash.com/photo-1597318181409-cf64d0b5d8a2?auto=format&fit=crop&w=300&q=80',
  },
  {
    id: 302,
    category_id: 3,
    name: 'Türk Kahvesi',
    price: 50,
    image: 'https://images.unsplash.com/photo-1570188467977-16057a66710b?auto=format&fit=crop&w=300&q=80',
  },
  {
    id: 303,
    category_id: 3,
    name: 'Ayran',
    price: 40,
    image: 'https://images.unsplash.com/photo-1626127885440-69022c422c54?auto=format&fit=crop&w=300&q=80',
  },
];

export const MOCK_STATS: ReportStats = {
  total_revenue: 12540,
  total_orders: 48,
  total_items: 156,
};

export const MOCK_SALES_DATA: SalesData[] = [
  { name: 'Tostlar', value: 4500 },
  { name: 'İçecekler', value: 2400 },
  { name: 'Sandviçler', value: 1800 },
];
