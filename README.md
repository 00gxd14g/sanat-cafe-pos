<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Sanat Cafe POS (SimplePOS)

Vite + React frontend ve FastAPI + SQLite backend ile çalışan, Windows üzerinde USB termal yazıcı/QZ Tray entegrasyonuna hazır POS uygulaması.

## Localhost

Tek komutla başlat:

```powershell
.\run-local.ps1
```

Durdur:

```powershell
.\stop-local.ps1
```

URL’ler:
- Frontend: `http://127.0.0.1:3000/#/`
- Backend health: `http://127.0.0.1:8000/api/health`

## Yazdırma

- Varsayılan: `server` (print_jobs + worker, `PRINT_MODE=file` → `backend/prints/`).
- QZ Tray için `print_strategy=qz` ayarlayın; admin ayar ekranından bağlantı testini çalıştırın.

## Dokümantasyon

Detaylı mimari ve dikkat notları: `PROJE_DOKUMANI.md`
