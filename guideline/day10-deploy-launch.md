# ⚪ Day 10 — Deploy & Launch 🚀

> **Status:** ⏳ BELUM DIMULAI
> **Durasi Estimasi:** 5-6 jam
> **Goal:** BridgeDocs live di internet. URL yang bisa dimasukkan ke portfolio/LinkedIn.
> **Prasyarat:** Day 9 selesai — Aplikasi polished dan siap production.

---

## 📋 Ringkasan

Hari terakhir! Deploy semua ke cloud: Frontend ke Vercel, Backend ke Railway, Database ke Supabase, dan (opsional) Vector DB ke Pinecone. Tulis README profesional dan test full flow di production.

---

## 📝 Task Detail

### Task 1: Frontend → Vercel (Gratis)

#### 1a. Push ke GitHub
```bash
cd frontend
# Pastikan .env.local TIDAK masuk ke git
echo ".env.local" >> .gitignore

# Push ke GitHub (buat repo baru di github.com dulu)
git init
git add .
git commit -m "BridgeDocs Frontend - ready for deployment"
git remote add origin https://github.com/USERNAME/bridgedocs-frontend.git
git push -u origin main
```

#### 1b. Deploy di Vercel
1. Buka [vercel.com](https://vercel.com) → Sign in dengan GitHub
2. Klik "New Project" → Import repository `bridgedocs-frontend`
3. Framework: **Next.js** (auto-detected)
4. Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   ```
5. Klik "Deploy" → tunggu build selesai
6. Dapatkan URL: `https://bridgedocs.vercel.app` (atau custom domain)

---

### Task 2: Database → Supabase (Gratis)

#### 2a. Buat Project di Supabase
1. Buka [supabase.com](https://supabase.com) → Buat akun/Sign in
2. Klik "New Project"
3. Pilih region terdekat (Singapore untuk Indonesia)
4. Set database password (simpan ini!)
5. Tunggu provisioning selesai

#### 2b. Dapatkan Connection String
```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

#### 2c. Migrasi Data
- Update `DATABASE_URL` di backend `.env` dengan URL Supabase
- Jalankan backend sekali → `Base.metadata.create_all()` akan buat semua tabel
- Atau gunakan Alembic untuk migration yang proper:
```bash
alembic init alembic
alembic revision --autogenerate -m "initial migration"
alembic upgrade head
```

---

### Task 3: Backend → Railway (Gratis)

#### 3a. Buat Dockerfile untuk FastAPI
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Buat folder uploads
RUN mkdir -p uploads

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 3b. Push ke GitHub
```bash
cd backend
git init
git add .
git commit -m "BridgeDocs Backend - ready for deployment"
git remote add origin https://github.com/USERNAME/bridgedocs-backend.git
git push -u origin main
```

#### 3c. Deploy di Railway
1. Buka [railway.app](https://railway.app) → Sign in dengan GitHub
2. "New Project" → "Deploy from GitHub repo"
3. Pilih repository `bridgedocs-backend`
4. Railway auto-detect Dockerfile
5. Set Environment Variables:
   ```
   DATABASE_URL=postgresql://... (dari Supabase)
   GOOGLE_API_KEY=your-gemini-api-key
   JWT_SECRET_KEY=generate-a-strong-secret-here
   JWT_ALGORITHM=HS256
   JWT_EXPIRE_MINUTES=1440
   CHROMA_HOST=your-chroma-host
   CHROMA_PORT=8000
   FRONTEND_URL=https://bridgedocs.vercel.app
   ```
6. Deploy → dapatkan URL: `https://bridgedocs-backend.railway.app`

---

### Task 4: Vector DB — ChromaDB di Railway ATAU Pinecone

**Opsi A: ChromaDB di Railway**
- Deploy ChromaDB sebagai service terpisah di Railway
- Gunakan Docker image `chromadb/chroma:latest`
- Update `CHROMA_HOST` dan `CHROMA_PORT` di backend env vars

**Opsi B: Pindah ke Pinecone (Free Tier)**
1. Buat akun di [pinecone.io](https://pinecone.io)
2. Buat index baru (dimension: 768 untuk Gemini embedding-001)
3. Install: `pip install pinecone-client langchain-pinecone`
4. Update `rag_pipeline.py` untuk menggunakan Pinecone
5. Pinecone free tier: 1 index, 100K vectors — cukup untuk portfolio

---

### Task 5: Update Environment Variables Production

**Frontend `.env.local` (Vercel):**
```
NEXT_PUBLIC_API_URL=https://bridgedocs-backend.railway.app
```

**Backend `.env` (Railway):**
```
DATABASE_URL=postgresql://... (Supabase production)
GOOGLE_API_KEY=your-production-gemini-key
JWT_SECRET_KEY=strong-random-secret-for-production
FRONTEND_URL=https://bridgedocs.vercel.app
CHROMA_HOST=your-chroma-host
CHROMA_PORT=8000
```

> ⚠️ **PENTING:** Pastikan `FRONTEND_URL` di backend CORS sesuai dengan URL Vercel. Jika tidak, frontend tidak bisa memanggil API.

---

### Task 6: Test Full Flow di Production

Buka `https://bridgedocs.vercel.app` dan test:

| Step | Expected |
|------|----------|
| 1. Register akun baru | Berhasil, redirect ke dashboard |
| 2. Login | Berhasil |
| 3. Upload PDF | Upload berhasil, status → ready |
| 4. Chat dengan dokumen | AI menjawab relevan |
| 5. Ganti level ke Beginner | Jawaban lebih sederhana |
| 6. Chat dalam Bahasa Indonesia | AI jawab dalam Bahasa Indonesia |
| 7. Generate Quiz | 5 pertanyaan MCQ muncul |
| 8. Dark mode | Toggle bekerja |
| 9. Mobile view | Responsive |

---

### Task 7: Tulis README Profesional

Buat `README.md` di root project:

```markdown
# 🌉 BridgeDocs — AI-Powered Technical Document Tutor

> Chat with any technical document. Get explanations at your level, in your language.

![BridgeDocs Demo](screenshot.gif)

## ✨ Features

- 📄 **Smart Document Chat** — Upload PDF, ask questions, get precise answers with source citations
- 🎯 **Level Adjuster** — Toggle between Beginner, Intermediate, and Expert explanations
- 🌐 **Multilingual** — Learn in your language while keeping technical terms in English
- 📝 **Quiz Generator** — Auto-generate MCQ quizzes from document content
- 👁️ **Split-View Interface** — PDF viewer side-by-side with chat

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, Tailwind CSS, Shadcn/UI |
| Backend | FastAPI (Python) |
| AI/RAG | LangChain, Gemini 1.5 Flash |
| Embeddings | Gemini embedding-001 |
| Vector DB | ChromaDB / Pinecone |
| Database | PostgreSQL (Supabase) |
| Deployment | Vercel + Railway |

## 🚀 Live Demo

**[→ Try BridgeDocs](https://bridgedocs.vercel.app)**

## 📸 Screenshots

[Tambahkan 3-4 screenshot: Landing, Dashboard, Chat, Quiz]

## 🏗️ Architecture

[Tambahkan diagram RAG pipeline]

## 🏃 Run Locally

[Instruksi setup lokal]

## 📝 License

MIT
```

**Buat demo GIF/video:**
- Record screen saat menggunakan app (upload → chat → quiz)
- Convert ke GIF atau upload ke YouTube
- Embed di README

---

## ✅ Checklist Final

- [ ] Frontend deployed di Vercel
- [ ] Backend deployed di Railway
- [ ] Database di Supabase
- [ ] Vector DB accessible dari production
- [ ] CORS dikonfigurasi dengan benar
- [ ] Full flow berfungsi di production
- [ ] README dengan screenshot/demo
- [ ] GitHub repo publik
- [ ] **🎉 BridgeDocs is LIVE! Share the link!**

---

## 🎉 Selamat!

Kamu telah menyelesaikan BridgeDocs dalam 10 hari! Project ini menunjukkan kemampuan:
- **Full-Stack Development** (Next.js + FastAPI)
- **AI/ML Integration** (RAG pipeline, LangChain, Gemini)
- **Database Design** (PostgreSQL + Vector DB)
- **Cloud Deployment** (Vercel + Railway + Supabase)
- **Product Thinking** (UX, multilingual, quiz, level adjuster)

Share di LinkedIn, portfolio, dan GitHub! 🚀
