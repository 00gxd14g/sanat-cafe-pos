# Sanat Cafe POS – Proje Dokümanı

Bu doküman, frontend + backend akışını, yazdırma (server vs QZ Tray) stratejilerini, veri modelini ve dikkat edilmesi gereken kritik noktaları özetler.

## 1) Genel Mimari
- **Frontend (Vite + React + TS)**: Masa seçimi, sipariş oluşturma, raporlar, admin (sipariş, ürün, ayar, debug).
- **Backend (FastAPI + SQLite)**: Gerçek veri kaydı, iş kuralları (sipariş/fiyat kontrolü), print job kuyruğu, raporlar.
- **Print stratejisi**:  
  - `server`: print_jobs kuyruğu + worker (Windows spooler/file).  
  - `qz`: print_jobs durumu `CLIENT_PENDING`; QZ Tray ile tarayıcıdan silent print, `/api/print/jobs/:id/ack` ile durum bildirimi.

## 2) Frontend Akışları
- **Rotalar**  
  - `/` Dashboard (masa grid, empty/occupied)  
  - `/pos` ve `/pos/:tableId` Sipariş oluşturma + yazdırma  
  - `/admin/orders` Açık/Hazır/Ödendi sipariş listesi (masa bazlı)  
  - `/admin/products` Ürün/fiyat yönetimi  
  - `/admin/settings` Print/QZ ayarları  
  - `/admin/debug` Print jobs, audit, backend log, Windows printer listesi  
  - `/admin/reports` Gün sonu raporu
- **OrderScreen**  
  - Kategorilere “Tümü (id=0)” ekler.  
  - Ürün kartı tıklanınca sepete +1.  
  - “Nakit tahsil edildi” → `payment_status=PAID`; değilse `PENDING`.  
  - “Onayla ve Yazdır” → `POST /api/orders`; `print_strategy=qz` ise dönen `print_jobs` QZ ile tetiklenir.

## 3) Backend Kuralları
- **Veri modeli**  
  - `tables(id, name, is_active)`  
  - `categories(id, name, sort_order, is_active)`  
  - `products(id, category_id, name, price, is_active, image_url, sku)`  
  - `orders(id, table_id NULL, status, subtotal, total, payment_status, created_at, paid_at)`  
  - `order_items(id, order_id, product_id, name_snapshot, unit_price_snapshot, qty, line_total, category_id_snapshot)`  
  - `print_jobs(id, order_id, job_type, printer_name, payload_raw, status, attempts, last_error, created_at, printed_at)`  
  - `settings(key, value)` (print/QZ ayarları)
- **Sipariş oluşturma (`POST /api/orders`)**  
  - `table_id=0` ⇒ DB’de `NULL` (paket/tezgah), `>0` ⇒ masa doğrulaması.  
  - Ürün doğrulaması: aktif, fiyatı >0, qty>0.  
  - **Fiyat güvenliği**: `unit_price = product.price` (client fiyatına güvenilmez).  
  - Snapshot: `name_snapshot`, `unit_price_snapshot`, `category_id_snapshot`.  
  - `payment_status=PAID` ise `paid_at` set, rapora girer.  
  - 2 print job: `KITCHEN` + `CUSTOMER`; `server` ise `PENDING`, `qz` ise `CLIENT_PENDING`.
- **Masa durumu (`GET /api/tables`)**  
  - `occupied` = masada `payment_status=PENDING` sipariş var.  
  - `total_amount` = açık sipariş toplamı.  
  - Frontend yalnızca `empty|occupied` bekler.
- **Raporlar**  
  - `/api/reports/daily/stats` → `total_revenue` (PAID), `total_orders`, `total_items`.  
  - `/api/reports/daily/sales` → kategori bazlı PAID satış toplamı.

## 4) Yazdırma Stratejileri
- **Server mode** (`print_strategy=server`)  
  - Print job’lar `PENDING`; worker (`workers/print_worker.py`) sıradaki işi `PRINTING`→`PRINTED/FAILED` yapar.  
  - `PRINT_MODE`: `file` (varsayılan, `backend/prints`), `spooler` (Windows RAW), `noop`.
- **QZ mode** (`print_strategy=qz`)  
  - Print job’lar `CLIENT_PENDING`; worker bu modda basmaz.  
  - Frontend `services/qz.ts` → `initQZ()` (cert + sign), `printFromJobId(jobId)` ile `/api/print/payload` alır, `qz.print` çağırır, `/api/print/jobs/:id/ack` ile durum günceller.
- **QZ güvenlik endpointleri**  
  - `GET /api/qz/cert` → public cert (PEM).  
  - `POST /api/qz/sign { toSign }` → private key ile imza (base64).  
  - Private key yalnızca backend’de tutulur (`backend/keys/private-key.pem`).

## 5) Seed ve Ayarlar
- Seed kategoriler: Tost Çeşitleri, Sandviçler, İçecekler.  
- Seed ürünler: Karışık Tost, Sucuklu Tost, Sosisli Patso, Çay, Türk Kahvesi (fiyat >0).  
- Varsayılan ayarlar: `PRINT_STRATEGY=server`, `PRINT_MODE=file`, `PRINT_OUTPUT_DIR=backend/prints`, `QZ_ENCODING=CP857`, fiyat gösterimi müşteri için açık, mutfak için kapalı.

## 6) Admin/Debug Ekranları
- **Admin Orders**: Açık/Hazır/Ödendi sipariş listesi; masa bazlı gruplanır; toplam tutar görünür; “Hazır” ve “Ödendi” aksiyonları.  
- **Admin Products**: Ürün/fiyat/Kategori güncelleme, SKU/Resim opsiyonel, aktif/pasif.  
- **Admin Settings**: print_strategy, print_mode, encoding, yazıcı adları, fiyat gösterimi; QZ bağlantı testi (Windows printer listesi).  
- **Admin Debug**: print_jobs listesi (+retry), audit log, backend log tail, Windows printer listesi (pywin32).

## 7) Çalıştırma (localhost)
- `./run-local.ps1` → frontend (Vite) + backend (FastAPI) aynı anda.  
- Frontend: `http://127.0.0.1:3000/#/`  
- Backend health: `http://127.0.0.1:8000/api/health`

## 8) QZ Tray Notları / Sorun Giderme
- Windows’a yazıcı driver’ını kurup test page basın; aynı PC’de QZ Tray açık olmalı.  
- QZ Tray ilk bağlantıda güvenlik uyarısı çıkar; “localhost” için izin verin.  
- “Failed to sign request” hatası:  
  1) Backend çalışıyor ve `backend/keys/*.pem` mevcut olmalı (gerekirse `python backend/scripts/generate_qz_keys.py`).  
  2) Tarayıcı URL’si `localhost`/`127.0.0.1` olmalı (CORS/sertifika uyumu).  
  3) QZ Tray’de izin penceresini kabul edin; Windows firewall portlarını (8181/8182) engellemiyor olmalı.  
- USB termal yazıcı için `print_mode=spooler` (server) ya da `print_strategy=qz` (client) tercih edin; ikisini aynı anda kullanmayın.

## 9) Kritik Dikkat Notları
- Client’ın gönderdiği `price` kullanılmaz; DB fiyatı esas.  
- Yazdırmayı request içinde bekletmeyin; print_jobs + worker/QZ kullanın.  
- SQLite: WAL + kısa transaction; çoklu sekme kullanımında kilitlenmeyi azaltır.  
- Fiyatı olmayan ürünleri listelemeyin (frontend `number` bekler, 0 TL riski).  
- `table_id=0` paket/tezgah; DB’de `NULL` saklanır.
