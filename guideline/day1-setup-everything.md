# 🟦 Day 1 — Setup Everything

> **Status:** ✅ SELESAI
> **Tanggal:** 1 Mei 2026
> **Durasi Estimasi:** 4-6 jam
> **Goal:** Environment berjalan end-to-end. Belum ada fitur, tapi semua service sudah running.

---

## 📋 Ringkasan

Day 1 fokus pada membangun fondasi infrastruktur project. Semua tools, database, backend, dan frontend harus bisa berjalan. Tidak ada fitur yang dibangun hari ini — hanya setup.

---

## 🔑 Prasyarat (Sebelum Mulai)

### 1. Dapatkan Gemini API Key (Gratis)
- Buka [aistudio.google.com](https://aistudio.google.com)
- Login dengan akun Google
- Klik **"Get API Key"** → **"Create API key"**
- Simpan key di tempat aman (akan dipakai di file `.env` nanti)
- **Free tier:** 15 requests/menit, 1M tokens/hari — lebih dari cukup

### 2. Install Tools yang Dibutuhkan
- **Python 3.11+** — `python --version` untuk cek
- **Node.js 18+** — `node --version` untuk cek
- **Docker Desktop** — Download dari [docker.com](https://www.docker.com/products/docker-desktop/)
- **Git** — `git --version` untuk cek
- **Code Editor** — VS Code (recommended)

---

## 📝 Task Detail

### Task 1: Buat Project Folder & Inisialisasi Git

```bash
mkdir BridgeDocs
cd BridgeDocs
git init
```

Buat file `.gitignore`:
```
# Python
__pycache__/
*.pyc
.env
venv/
uploads/

# Node
node_modules/
.next/
.env.local

# Docker
postgres_data/
chroma_data/

# OS
.DS_Store
Thumbs.db
```

---

### Task 2: Setup Docker — PostgreSQL + ChromaDB

Buat file `docker-compose.yml` di root project:

```yaml
services:
  postgres:
    image: postgres:15
    container_name: bridgedocs-postgres
    environment:
      POSTGRES_DB: bridgedocs
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: bridgedocs_secret
    ports:
      - "5433:5432"    # Port 5433 karena 5432 mungkin sudah dipakai lokal
    volumes:
      - postgres_data:/var/lib/postgresql/data

  chromadb:
    image: chromadb/chroma:latest
    container_name: bridgedocs-chromadb
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma

volumes:
  postgres_data:
  chroma_data:
```

**Jalankan:**
```bash
# Pastikan Docker Desktop sudah running terlebih dahulu!
docker-compose up -d
```

**Verifikasi:**
```bash
docker ps
# Harus muncul 2 container: bridgedocs-postgres dan bridgedocs-chromadb
```

> **⚠️ Potensi Masalah:** Jika port 5432 sudah dipakai (local PostgreSQL), gunakan port 5433 seperti konfigurasi di atas. Jika Docker tidak mau start, pastikan Docker Desktop sudah berjalan.

---

### Task 3: Setup Backend — FastAPI

```bash
mkdir backend
cd backend
```

**3a. Buat virtual environment:**
```bash
python -m venv venv
source venv/bin/activate    # Mac/Linux
# atau: venv\Scripts\activate  # Windows
```

**3b. Buat `requirements.txt`:**
```
# Web framework
fastapi>=0.115.0
uvicorn[standard]>=0.34.0

# Database
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
alembic>=1.15.0

# Auth
python-jose[cryptography]>=3.4.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.20

# AI / RAG
langchain>=0.3.0
langchain-google-genai>=2.1.0
langchain-community>=0.3.0
langchain-chroma>=0.2.0
chromadb>=1.0.0
pypdf>=5.0.0

# Utilities
python-dotenv>=1.0.0
pydantic[email]>=2.10.0
```

> **💡 Tips:** Gunakan `>=` (minimum version) bukan `==` (exact version) untuk menghindari conflict dependency. Contoh: ChromaDB pernah membutuhkan FastAPI versi tertentu.

**3c. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3d. Buat file `.env`:**
```env
# Database
DATABASE_URL=postgresql://admin:bridgedocs_secret@localhost:5433/bridgedocs

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8001

# Gemini API
GOOGLE_API_KEY=your-gemini-api-key-here

# JWT Auth
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# CORS
FRONTEND_URL=http://localhost:3000
```

**3e. Buat `database.py` — Koneksi Database:**
```python
"""
BridgeDocs Backend — Database Connection
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Konsep penting:**
- `engine` = koneksi pool ke PostgreSQL
- `SessionLocal` = factory untuk membuat session database per request
- `Base` = base class yang diwariskan ke semua model
- `get_db()` = dependency injection — FastAPI otomatis menyediakan session database ke setiap endpoint

**3f. Buat `models.py` — Definisi Tabel Database:**
```python
"""
BridgeDocs Backend — Database Models
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    source_url = Column(String(2000), nullable=True)
    status = Column(
        SAEnum("processing", "ready", "failed", name="document_status"),
        default="processing", nullable=False,
    )
    page_count = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="documents")
    conversations = relationship("Conversation", back_populates="document", cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(500), default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    document = relationship("Document", back_populates="conversations")
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role = Column(SAEnum("user", "assistant", name="message_role"), nullable=False)
    content = Column(Text, nullable=False)
    sources = Column(Text, nullable=True)  # JSON string of source citations
    created_at = Column(DateTime, default=datetime.utcnow)
    conversation = relationship("Conversation", back_populates="messages")
```

**Kenapa UUID bukan auto-increment?**
- UUID globally unique, tidak bisa ditebak
- Auto-increment (1, 2, 3...) membocorkan informasi jumlah data

**3g. Buat `schemas.py` — Validasi Request/Response (Pydantic):**
```python
"""
BridgeDocs Backend — Pydantic Schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


# ─── Auth Schemas ─────────────────────────────────────────
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ─── Document Schemas ────────────────────────────────────
class DocumentResponse(BaseModel):
    id: UUID
    title: str
    status: str
    page_count: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Conversation & Message Schemas ──────────────────────
class ConversationCreate(BaseModel):
    document_id: UUID

class ConversationResponse(BaseModel):
    id: UUID
    document_id: UUID
    title: str
    created_at: datetime
    model_config = {"from_attributes": True}

class MessageCreate(BaseModel):
    content: str
    level: Optional[str] = "intermediate"
    language: Optional[str] = "english"

class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    sources: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}
```

**Kenapa schemas terpisah dari models?**
- **Models** = struktur database (termasuk `password_hash`, field internal)
- **Schemas** = kontrak API (tidak pernah expose field sensitif seperti password)
- Ini best practice keamanan agar tidak pernah secara tidak sengaja mengirim password hash di response API

**3h. Buat folder router dan service (placeholder):**
```bash
mkdir routers services
touch routers/__init__.py services/__init__.py
```

**3i. Buat `main.py` — Entry Point Aplikasi:**
```python
"""
BridgeDocs Backend — Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from database import engine, Base

load_dotenv()

# Auto-create all database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BridgeDocs API",
    description="AI-powered context-aware technical tutor using RAG",
    version="0.1.0",
)

# CORS: Izinkan frontend (localhost:3000) memanggil backend (localhost:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "app": "BridgeDocs API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**Konsep penting — CORS:** Browser memblokir request antar origin yang berbeda (port dihitung sebagai origin berbeda). Tanpa CORS middleware, Next.js di `:3000` akan diblokir saat memanggil FastAPI di `:8000`.

**3j. Test backend:**
```bash
uvicorn main:app --reload
```
Buka `http://localhost:8000/docs` — harus menampilkan Swagger UI FastAPI.

---

### Task 4: Setup Frontend — Next.js + Tailwind + Shadcn/UI

```bash
cd ..   # Kembali ke root BridgeDocs
npx create-next-app@latest ./frontend --typescript --tailwind --app --src-dir
```

Jawab pertanyaan setup sesuai preferensi (recommended: Yes untuk semua).

**Install Shadcn/UI:**
```bash
cd frontend
npx shadcn@latest init -d
```

> **💡 Kenapa Shadcn/UI?** Shadcn bukan library yang di-install — dia meng-copy source code component langsung ke project kamu. Artinya kamu punya kontrol penuh untuk kustomisasi setiap button, input, dan dialog. Vercel dan Linear menggunakan pattern ini.

**Test frontend:**
```bash
npm run dev
```
Buka `http://localhost:3000` — harus menampilkan halaman default Next.js.

---

## ✅ Checklist Verifikasi Akhir

| Service | URL | Status yang Diharapkan |
|---------|-----|----------------------|
| PostgreSQL | `localhost:5433` | ✅ Running via Docker |
| ChromaDB | `localhost:8001` | ✅ Running via Docker |
| FastAPI Backend | `http://localhost:8000/docs` | ✅ Swagger UI muncul |
| Next.js Frontend | `http://localhost:3000` | ✅ Halaman default muncul |

**Test API response:**
```bash
curl http://localhost:8000/
```
Expected output:
```json
{
    "app": "BridgeDocs API",
    "version": "0.1.0",
    "status": "running",
    "docs": "/docs"
}
```

---

## 📚 Konsep yang Dipelajari Hari Ini

1. **Docker Compose** — Mendefinisikan infrastruktur dalam file YAML
2. **SQLAlchemy ORM** — Class Python yang mewakili tabel database
3. **Pydantic Schemas** — Validasi request/response yang type-safe
4. **Dependency Injection** — FastAPI otomatis menyediakan database session
5. **CORS** — Keamanan cross-origin untuk komunikasi frontend ↔ backend
6. **UUID primary keys** — Identifier yang aman dan non-sequential

---

## 🔧 Troubleshooting

| Problem | Penyebab | Solusi |
|---------|----------|--------|
| `pip install` gagal | Conflict dependency ChromaDB & FastAPI | Ubah dari exact version (`==`) ke minimum (`>=`) |
| FastAPI tidak bisa konek ke PostgreSQL | Port 5432 sudah dipakai lokal | Gunakan port **5433** di docker-compose |
| Docker tidak start | Docker Desktop belum running | Buka Docker Desktop terlebih dahulu |
| `ModuleNotFoundError` | Virtual environment belum aktif | Jalankan `source venv/bin/activate` |

---

## ➡️ Preview Day 2

Besok kita akan membangun **sistem autentikasi**: register, login, dan JWT token. User akan bisa membuat akun dan login ke BridgeDocs.
