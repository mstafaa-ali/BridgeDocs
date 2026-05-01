# 🚀 BridgeDocs — 10-Day Sprint Plan (Solo Portfolio Build)

> **Stack:** FastAPI + LangChain + ChromaDB + Gemini API · Next.js + Tailwind + Shadcn/UI
> **Goal:** A fully working, deployed portfolio project in 10 days.

---

## 🔑 Before Day 1: Get Your API Key (30 min)

**Google AI Studio is 100% free** — your Google Pro account doesn't matter here. Anyone with a standard Google account can get a free Gemini API key.

### Steps:
1. Go to **[aistudio.google.com](https://aistudio.google.com)**
2. Sign in with your Google account
3. Click **"Get API Key"** → **"Create API key"**
4. Copy the key → save it somewhere safe (`.env` file later)

**Free tier gives you:** 15 requests/min, 1M tokens/day — **more than enough** for a portfolio project.

---

## 📁 Project Structure (Final Target)

```
BridgeDocs/
├── backend/
│   ├── main.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── documents.py
│   │   └── chat.py
│   ├── services/
│   │   ├── rag_pipeline.py
│   │   └── embeddings.py
│   ├── models.py         ← SQLAlchemy models
│   ├── database.py       ← DB connection
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── app/
│   │   ├── page.tsx          ← Landing page
│   │   ├── dashboard/page.tsx
│   │   └── chat/[id]/page.tsx
│   ├── components/
│   └── .env.local
└── docker-compose.yml        ← PostgreSQL + ChromaDB
```

---

## 📅 Day-by-Day Plan

---

### 🟦 Day 1 — Setup Everything

**Goal:** Environment working end-to-end. Zero features, but everything runs.

**Tasks:**
- [ ] Go to [aistudio.google.com](https://aistudio.google.com) → get Gemini API key
- [ ] Install tools: Python 3.11+, Node 18+, Docker Desktop
- [ ] Create project folder `d:\Ali\BridgeDocs\`
- [ ] Create `docker-compose.yml`:
  ```yaml
  version: '3.8'
  services:
    postgres:
      image: postgres:15
      environment:
        POSTGRES_DB: bridgedocs
        POSTGRES_USER: admin
        POSTGRES_PASSWORD: password
      ports:
        - "5432:5432"
    chromadb:
      image: chromadb/chroma:latest
      ports:
        - "8001:8000"
  ```
- [ ] Run `docker-compose up -d` → confirm both containers start
- [ ] Create `backend/` → install FastAPI: `pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv langchain langchain-google-genai chromadb pypdf`
- [ ] Create `frontend/` → `npx create-next-app@latest . --typescript --tailwind --app`
- [ ] Install Shadcn: `npx shadcn@latest init`
- [ ] Test: `uvicorn main:app --reload` shows FastAPI docs at `localhost:8000/docs`
- [ ] Test: `npm run dev` shows Next.js at `localhost:3000`

**✅ End of Day 1:** Both servers running, Docker up, API key ready.

---

### 🟦 Day 2 — Backend: Database + Auth

**Goal:** Users can register and login. JWT tokens work.

**Tasks:**
- [ ] Write `database.py` — SQLAlchemy connection to PostgreSQL
- [ ] Write `models.py` — `User`, `Document`, `Conversation`, `Message` tables
- [ ] Run `Base.metadata.create_all(bind=engine)` to create tables
- [ ] Write `routers/auth.py`:
  - `POST /auth/register` → hash password with `bcrypt`, save user
  - `POST /auth/login` → verify password, return JWT
  - `GET /auth/me` → protected route, returns current user
- [ ] Install: `pip install python-jose[cryptography] passlib[bcrypt]`
- [ ] Test with Postman: register a user → login → get token → call `/auth/me`

**✅ End of Day 2:** Auth system fully working.

---

### 🟦 Day 3 — Backend: Document Upload API

**Goal:** Upload a PDF, save it, trigger background ingestion.

**Tasks:**
- [ ] Write `routers/documents.py`:
  - `POST /documents/upload` → accept PDF file, save to `uploads/` folder, create DB record with `status: "processing"`
  - `GET /documents/` → list all docs for current user
  - `DELETE /documents/{id}` → delete doc + its vectors from ChromaDB
- [ ] Use FastAPI `BackgroundTasks` to call the RAG ingestion function after upload (async, non-blocking)
- [ ] Update document `status` to `"ready"` when ingestion completes, `"failed"` if error

**✅ End of Day 3:** Can upload PDFs via API. Document list works.

---

### 🟡 Day 4 — The RAG Pipeline (Most Important Day)

**Goal:** PDF is ingested into ChromaDB. Queries return relevant chunks. **This is the heart of the project.**

**Tasks:**
- [ ] Write `services/rag_pipeline.py`:
  ```python
  # Step 1: Extract text
  from langchain_community.document_loaders import PyPDFLoader

  # Step 2: Split into chunks
  from langchain.text_splitter import RecursiveCharacterTextSplitter
  splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

  # Step 3: Embed with Gemini
  from langchain_google_genai import GoogleGenerativeAIEmbeddings
  embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

  # Step 4: Store in ChromaDB
  from langchain_community.vectorstores import Chroma
  vectorstore = Chroma(collection_name=document_id, embedding_function=embeddings)
  ```
- [ ] Write a test script `test_rag.py`:
  1. Load any PDF
  2. Ingest it into ChromaDB
  3. Query: `"What is this document about?"`
  4. Print the retrieved chunks + a Gemini answer
- [ ] **Manually validate quality** — does the answer make sense? If not, adjust chunk size.

**✅ End of Day 4:** RAG pipeline works. You can ask questions about a PDF from a Python script.

---

### 🟡 Day 5 — Backend: Chat API

**Goal:** Complete Q&A endpoint. Multi-turn conversation with memory.

**Tasks:**
- [ ] Write `routers/chat.py`:
  - `POST /conversations/` → create a new conversation for a document
  - `POST /conversations/{id}/messages` → the main Q&A endpoint:
    1. Load conversation history from DB (last 6 messages for context)
    2. Embed user query → retrieve top-5 chunks from ChromaDB
    3. Build prompt with system instructions + context + history + question
    4. Call Gemini LLM → get answer
    5. Save both user message + AI response to DB
    6. Return response + source citations (chunk page numbers)
  - `GET /conversations/{id}/messages` → get full conversation history
- [ ] Add `level` parameter (beginner/intermediate/expert) with different system prompts

**✅ End of Day 5:** Full backend is complete. Every feature works via Postman.

---

### 🟠 Day 6 — Frontend: Auth + Dashboard

**Goal:** Login/Register UI + Document Dashboard working.

**Tasks:**
- [ ] Set up API client in `lib/api.ts` (fetch wrapper with JWT headers)
- [ ] Build `/login` and `/register` pages with Shadcn form components
- [ ] Add auth context + protect routes with Next.js middleware
- [ ] Build `/dashboard` page:
  - Upload button (drag & drop PDF)
  - Document cards: title, date, status badge (`processing` / `ready`)
  - Delete button per document
  - Navigate to chat when clicking a ready document

**✅ End of Day 6:** You can register, login, upload a PDF, and see it in the dashboard.

---

### 🟠 Day 7 — Frontend: Chat Interface (The WOW feature)

**Goal:** The split-view chat UI — the feature that makes portfolios stand out.

**Tasks:**
- [ ] Build `/chat/[id]` page with split layout:
  ```
  ┌──────────────────────┬──────────────────────┐
  │   PDF Viewer         │   Chat Window        │
  │   (react-pdf)        │   (messages + input) │
  └──────────────────────┴──────────────────────┘
  ```
- [ ] Install: `npm install react-pdf`
- [ ] Build chat bubbles (user vs AI, with timestamps)
- [ ] Add **streaming responses** (Server-Sent Events) so text appears word by word (like ChatGPT)
- [ ] Add the **Level Toggle** (Beginner / Intermediate / Expert) — pill buttons in the toolbar
- [ ] Show **source citations** below each AI response (e.g., "Source: Page 4, Page 7")

**✅ End of Day 7:** You can open a document and chat with it. It feels like ChatGPT with a PDF.

---

### 🔴 Day 8 — Advanced Features

**Goal:** Add the features that make this a complete product.

**Tasks:**
- [ ] **Multilingual Support:**
  - Add a language dropdown (English, Indonesian, Arabic, French, etc.)
  - Inject into system prompt: `"Respond in {language}, but keep all technical terms in English"`
- [ ] **Quiz Generator:**
  - `POST /quiz/{document_id}` → generate 5 MCQ questions from document
  - Build a quiz modal/page in the frontend
  - Show score at the end
- [ ] **Landing Page** (`/`):
  - Hero section: "Chat with any technical document"
  - Feature highlights (multilingual, level adjuster, quizzes)
  - CTA: "Get started free"

**✅ End of Day 8:** Feature-complete MVP+ with quiz and multilingual support.

---

### ⚪ Day 9 — UI Polish + Error Handling

**Goal:** Make it feel premium, not like a school project.

**Tasks:**
- [ ] Add loading skeletons everywhere (dashboard, chat, quiz)
- [ ] Handle all error states (empty PDF, API timeout, upload failure)
- [ ] Refine UI: consistent spacing, typography, color palette
- [ ] Add a dark mode toggle
- [ ] Responsive design (works on mobile too)
- [ ] Add subtle animations (Framer Motion for page transitions)

**✅ End of Day 9:** The app feels polished and production-quality.

---

### ⚪ Day 10 — Deploy & Launch

**Goal:** Live URL you can put in your portfolio/LinkedIn.

**Tasks:**
- [ ] **Frontend → Vercel** (free):
  - Push `frontend/` to GitHub
  - Connect to Vercel → auto-deploy
- [ ] **Backend → Railway** (free tier):
  - Push `backend/` to GitHub
  - Add Dockerfile for FastAPI
  - Set environment variables in Railway dashboard
- [ ] **Database → Supabase** (free PostgreSQL):
  - Create a project → get connection string
  - Run migrations
- [ ] **Vector DB → Keep ChromaDB on Railway** OR switch to Pinecone free tier
- [ ] Update `.env` files with production URLs
- [ ] Test full flow on production: register → upload → chat → quiz
- [ ] Write README with:
  - Project description
  - Screenshot / demo GIF
  - Tech stack badges
  - Live demo link

**✅ End of Day 10:** 🎉 BridgeDocs is live. Share the link.

---

## 🗓️ Visual Calendar

| Day | Focus | Key Output |
|-----|-------|------------|
| **1** | Setup | Docker + FastAPI + Next.js running |
| **2** | Backend Auth | Register / Login / JWT working |
| **3** | Document API | PDF upload endpoint |
| **4** | RAG Pipeline ⭐ | Chat with PDF via Python script |
| **5** | Chat API | Full Q&A endpoint with history |
| **6** | Frontend Auth + Dashboard | Login + upload UI |
| **7** | Chat UI ⭐ | Split-view PDF + chat interface |
| **8** | Advanced Features | Quiz + multilingual + landing page |
| **9** | Polish | Loading states, errors, dark mode |
| **10** | Deploy 🚀 | Live URL on Vercel + Railway |

---

## 🛠️ Your Full Tech Stack (Final)

| Layer | Tool | Why |
|-------|------|-----|
| **Frontend** | Next.js 14 + Tailwind + Shadcn/UI | Industry standard, portfolio-worthy |
| **Backend** | FastAPI (Python) | Best for AI/ML integrations |
| **AI Orchestration** | LangChain | Handles RAG pipeline cleanly |
| **LLM** | Gemini 1.5 Flash (via AI Studio) | Free, fast, powerful |
| **Embeddings** | Gemini `embedding-001` | Free, consistent with the LLM |
| **Vector DB** | ChromaDB (dev) → Pinecone (prod) | Free at portfolio scale |
| **Relational DB** | PostgreSQL → Supabase (prod) | Free managed hosting |
| **Deployment** | Vercel (FE) + Railway (BE) | Both free, CI/CD built-in |

---

## 💡 Key Advice

> [!IMPORTANT]
> **Day 4 is make-or-break.** Spend as much time as needed validating RAG quality before moving on. A chat interface built on a broken RAG pipeline is worthless.

> [!TIP]
> **FastAPI auto-generates interactive API docs** at `localhost:8000/docs`. Use this as your Postman — it's much faster for testing your endpoints during development.

> [!NOTE]
> **Google AI Studio is separate from Google One/Workspace.** You don't need a Pro account. Just go to [aistudio.google.com](https://aistudio.google.com) with any Gmail account and get your free API key in under 2 minutes.

> [!WARNING]
> **Don't skip the landing page.** For a portfolio project, recruiters and visitors land on `/` first. A missing or bare landing page kills first impressions even if the app itself is great.
