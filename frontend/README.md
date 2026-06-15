# Melolo Partner Gateway Frontend

Frontend statis modern untuk demo partner/sister site yang mengonsumsi Melolo API Aggregator.

## Fitur UI/UX

- Hero cinematic dengan premium content positioning.
- Catalog cards responsif untuk tier `free`, `premium`, dan `exclusive`.
- Search/filter client-side untuk preview katalog.
- API console untuk mencoba endpoint backend dengan `X-API-Key`.
- Visual system custom: glassmorphism, editorial typography, gradient art cards, dan layout responsive.

## Menjalankan Lokal

Dari root repository:

```bash
python -m http.server 4173 --directory frontend
```

Buka:

```text
http://localhost:4173
```

Untuk backend lokal, jalankan FastAPI di `http://localhost:8000`, lalu gunakan console di halaman frontend untuk memanggil `/api/v1/series`, `/api/v1/exclusive`, atau `/api/v1/genres`.
