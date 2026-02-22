# Dropbox

A simplified Dropbox-like file storage application with a **FastAPI** backend and **Next.js** frontend. Users authenticate via **Supabase Auth** and store files in **Supabase Storage**, with presigned URLs for upload and download.

## Features

- **Authentication** — Supabase Auth (JWT) with Bearer token validation via JWKS
- **File upload** — Presigned upload URL, then confirm or fail the upload
- **File listing** — Paginated list of the current user’s files
- **Download** — Presigned download URL (e.g. 1-hour validity)
- **Delete** — Remove file from storage and database

## Tech stack

| Layer     | Stack |
|----------|--------|
| Backend  | Python 3, FastAPI, Uvicorn, Supabase (Storage + Auth JWKS), Pydantic |
| Frontend | Next.js 16, React 19, TypeScript, Mantine UI, Supabase JS (auth) |

## Project structure

```
dropbox/
├── backend/                 # FastAPI app
│   ├── app/
│   │   ├── api/             # Routes and dependencies
│   │   ├── core/            # Config, security (JWT), DB, storage
│   │   ├── facades/         # File business logic
│   │   ├── models/          # Schemas and enums
│   │   ├── repositories/    # Data access
│   │   └── utils/           # Logger, exceptions, singleton
│   └── requirements.txt
├── frontend/                # Next.js app
│   ├── app/                 # App router pages (login, auth error, main)
│   ├── components/          # UI (e.g. files table)
│   ├── lib/                 # Backend API client
│   └── package.json
└── README.md
```

## Prerequisites

- **Python 3.10+** (backend)
- **Node.js 18+** and npm (frontend)
- **Supabase** project with:
  - Auth enabled
  - A storage bucket (name used in env)
  - `user_files` (or equivalent) table for file metadata, if used by the backend

## Environment variables

### Backend (`backend/.env`)

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Supabase project URL (e.g. `https://xxx.supabase.co`) |
| `SUPABASE_KEY` | Supabase service/key with storage and DB access |
| `SUPABASE_STORAGE_BUCKET` | Storage bucket name for files |
| `PORT` | Server port (default: `8080`) |
| `ENVIRONMENT` | e.g. `development` or `production` |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins (e.g. `http://localhost:3000`) |

### Frontend (`frontend/.env` or `.env.local`)

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend base URL (e.g. `http://localhost:8080`) |
| Supabase env vars | As required by `@supabase/supabase-js` (e.g. `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`) |

## Running the project

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Set env vars (e.g. copy .env.example to .env and fill values)
uvicorn app.main:app --reload --port 8080
```

Or run the module:

```bash
python -m app.main
```

API docs: **http://localhost:8080/docs** (Swagger).

### Frontend

```bash
cd frontend
npm install
# Set NEXT_PUBLIC_API_URL and Supabase env vars
npm run dev
```

App: **http://localhost:3000**.

## API overview

All file endpoints require a valid Supabase JWT in the `Authorization: Bearer <token>` header.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/files/upload-url` | Get presigned upload URL |
| `PATCH` | `/api/v1/files/{file_id}/confirm` | Confirm or fail an upload |
| `GET`  | `/api/v1/files` | List user files (query: `skip`, `limit`) |
| `GET`  | `/api/v1/files/{file_id}/download-url` | Get presigned download URL |
| `DELETE` | `/api/v1/files/{file_id}` | Delete a file |

## License

Private / internal use unless otherwise specified.
