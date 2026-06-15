# Melolo API Aggregator

Backend REST API aggregator berbasis **Python/FastAPI** untuk menyajikan data konten video internal Melolo dalam format JSON kepada website partner/sister site.

## Struktur Folder

```text
app/
  api/v1/routes.py        # Endpoint REST API
  core/config.py          # Konfigurasi environment
  core/security.py        # API key hashing, tier access, signed URL
  core/rate_limit.py      # Rate limiting per API key (in-memory)
  db/session.py           # Koneksi PostgreSQL async
  models/content.py       # Model SQLAlchemy untuk series, episode, API key, request log
  schemas/content.py      # Pydantic response schema
  services/cache.py       # Redis cache dengan fallback in-memory
  main.py                 # FastAPI app, CORS, logging, Swagger
migrations/001_initial_schema.sql
```

## Menjalankan Aplikasi

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
export MELOLO_DATABASE_URL='postgresql+asyncpg://melolo:melolo@localhost:5432/melolo'
export MELOLO_SIGNING_SECRET='ganti-dengan-secret-minimal-16-char'
uvicorn app.main:app --reload
```

Swagger/OpenAPI tersedia di `GET /api/v1/docs` dan JSON schema di `GET /api/v1/openapi.json`.

## Environment Variable

| Variable | Fungsi |
| --- | --- |
| `MELOLO_DATABASE_URL` | DSN PostgreSQL async SQLAlchemy |
| `MELOLO_REDIS_URL` | Opsional, mengaktifkan Redis cache |
| `MELOLO_SIGNING_SECRET` | Secret HMAC untuk signed video URL |
| `MELOLO_SIGNED_URL_TTL_SECONDS` | Expiry signed URL, default 600 detik |
| `MELOLO_ALLOWED_ORIGINS` | Daftar origin CORS global |
| `MELOLO_VIDEO_CDN_BASE_URL` | Base URL CDN/proxy video |

## Autentikasi dan Tier Akses

Semua endpoint `/api/v1/*` membutuhkan header:

```http
X-API-Key: <partner-api-key>
```

API key disimpan sebagai SHA-256 hash pada tabel `partner_api_keys.api_key_hash`. Kolom `allowed_access_level` menentukan tier maksimum partner: `free < premium < exclusive`. Partner tetap bisa melihat metadata konten, tetapi `video_url` hanya dikembalikan ketika tier API key mencukupi.

## Signed URL Konten Eksklusif

`app/core/security.py` membuat signed URL berbasis HMAC-SHA256 dari `video_path`, `partner_id`, dan timestamp expiry. URL yang dihasilkan berisi query `partner`, `expires`, dan `sig`, sehingga layer CDN/proxy dapat memvalidasi akses sebelum melayani file video.

## Endpoint Ringkas

| Method | Path | Deskripsi |
| --- | --- | --- |
| GET | `/api/v1/series?page=1&page_size=20&access_level=premium` | List series dengan pagination dan filter tier |
| GET | `/api/v1/series/{id}` | Detail series beserta episode, termasuk metadata exclusive |
| GET | `/api/v1/episodes/{id}` | Detail episode dan `video_url` jika tier API key cukup |
| GET | `/api/v1/search?q=action` | Pencarian berdasarkan judul atau genre |
| GET | `/api/v1/genres` | Daftar kategori/genre |
| GET | `/api/v1/exclusive` | List konten premium dan exclusive |

## Frontend Partner Gateway

Frontend statis tersedia di folder `frontend/` dengan desain modern/premium untuk demo partner site. Jalankan dengan:

```bash
python -m http.server 4173 --directory frontend
```

Buka `http://localhost:4173`, lalu gunakan API console untuk menghubungkan halaman ke backend FastAPI lokal atau staging.

## Database

Gunakan `migrations/001_initial_schema.sql` untuk membuat schema PostgreSQL awal. Schema mencakup tabel `series`, `episodes`, `partner_api_keys`, dan `request_logs`.
