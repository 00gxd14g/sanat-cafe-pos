# Sanat Cafe POS

Sanat Cafe POS; masa, siparis, urun, tahsilat, raporlama ve termal yazici
islevlerini tek bir yerel uygulamada birlestiren cafe satis noktasi sistemidir.

Frontend React ve TypeScript ile, API ise FastAPI ve SQLAlchemy ile
gelistirilmistir. Yerel kurulum varsayilan olarak SQLite kullanir.

## Ozellikler

- Masa ve paket siparis yonetimi
- Kategori, urun ve fiyat yonetimi
- Nakit tahsilat ve siparis durumu takibi
- Gunluk satis ve kategori raporlari
- Mutfak ve musteri fisi icin yazdirma kuyrugu
- QZ Tray veya Windows yazdirma kuyrugu destegi
- Admin hata ayiklama ve yazici kontrol ekranlari

## Teknoloji

| Katman | Teknoloji |
| --- | --- |
| Frontend | React 19, TypeScript, Vite |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Veritabani | SQLite; MySQL surucusu opsiyonel |
| Yazdirma | QZ Tray veya Windows spooler |

## Dizin Yapisi

```text
.
├── backend/          FastAPI uygulamasi, veri modeli ve yazdirma servisi
├── components/       POS ve admin ekranlari
├── services/         API ve QZ Tray istemcileri
├── App.tsx           Uygulama rotalari
├── run-local.ps1     Yerel gelistirme baslaticisi
└── PROJE_DOKUMANI.md Mimari ve is kurallari
```

## Kurulum

Gereksinimler:

- Node.js 20+
- Python 3.11+
- Windows PowerShell
- Fiziksel yazdirma icin QZ Tray veya uyumlu Windows yazici surucusu

Backend ayarlarini olusturun:

```powershell
Copy-Item backend/.env.example backend/.env
```

Ardindan uygulamayi tek komutla baslatin:

```powershell
.\run-local.ps1
```

Servis adresleri:

- Frontend: `http://127.0.0.1:3000/#/`
- API saglik kontrolu: `http://127.0.0.1:8000/api/health`
- OpenAPI: `http://127.0.0.1:8000/docs`

Uygulamayi durdurmak icin:

```powershell
.\stop-local.ps1
```

## Yazdirma Modlari

### Server

Siparisler backend yazdirma kuyruguna eklenir. `PRINT_MODE=file` gelistirme
ortaminda ciktiyi dosyaya yazar; `spooler` modu Windows yazicisini kullanir.

### QZ Tray

Tarayici, yazdirma verisini API'den alip QZ Tray uzerinden istemci yazicisina
gonderir. Sertifika ve ozel anahtar dosyalari repoya eklenmemelidir.

## Veri ve Guvenlik

- Fiyatlar istemciden degil, backend veritabanindan dogrulanir.
- `.env`, veritabani, log, yazdirma ciktisi ve anahtar dosyalari Git tarafindan
  izlenmez.
- Uretim ortamina gecmeden once CORS, kimlik dogrulama, yedekleme ve anahtar
  yonetimi ayrica ele alinmalidir.

## Dokumantasyon

Veri modeli, API akislari, raporlama ve yazdirma ayrintilari icin
[PROJE_DOKUMANI.md](PROJE_DOKUMANI.md) dosyasina bakin.

## Lisans

Bu repo icin bir acik kaynak lisansi tanimlanmamistir.
