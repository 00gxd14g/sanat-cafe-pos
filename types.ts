export enum TableStatus {
  EMPTY = 'empty',
  OCCUPIED = 'occupied'
}

export interface Table {
  id: number;
  name: string;
  status: TableStatus;
  total_amount?: number; // if occupied
}

export interface Category {
  id: number;
  name: string;
}

export interface Product {
  id: number;
  category_id: number;
  name: string;
  price: number;
  image?: string;
}

export interface CartItem extends Product {
  quantity: number;
}

export interface OrderPayload {
  table_id: number;
  payment_status: 'PAID' | 'PENDING';
  items: {
    product_id: number;
    quantity: number;
    price: number;
  }[];
}

export interface ReportStats {
  total_revenue: number;
  total_orders: number;
  total_items: number;
}

export interface SalesData {
  name: string;
  value: number;
}

export interface OrderItemView {
  product_id: number;
  name: string;
  quantity: number;
  unit_price: number;
  line_total: number;
}

export interface OrderView {
  id: number;
  table_id: number | null;
  status: string;
  payment_status: 'PAID' | 'PENDING';
  total: number;
  created_at: string;
  paid_at?: string | null;
  items: OrderItemView[];
}

export interface AppSettings {
  print_strategy: 'server' | 'qz' | string;
  print_mode: 'file' | 'spooler' | 'noop' | string;
  print_output_dir: string;
  printer_kitchen_name: string;
  printer_customer_name: string;
  kitchen_show_prices: boolean;
  customer_show_prices: boolean;
  qz_encoding: string;
}

export interface CategoryAdmin extends Category {
  sort_order: number;
  is_active: boolean;
}

export interface ProductAdmin {
  id: number;
  category_id: number;
  name: string;
  price: number;
  is_active: boolean;
  image_url?: string | null;
  sku?: string | null;
}
