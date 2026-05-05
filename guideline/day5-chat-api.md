# 🟡 Day 5 — Backend: Chat API

> **Status:** ⏳ BELUM DIMULAI
> **Durasi Estimasi:** 5-6 jam
> **Goal:** Endpoint Q&A lengkap. Multi-turn conversation dengan memory.
> **Prasyarat:** Day 4 selesai — RAG pipeline berfungsi (ingest + query).

---

## 📋 Ringkasan

Hari ini membangun endpoint chat yang menjadi fitur utama BridgeDocs. User bisa bertanya tentang dokumen, AI menjawab berdasarkan isi dokumen, dan percakapan tersimpan. Termasuk fitur level adjuster (beginner/intermediate/expert) dan source citations.

---

## 📝 Task Detail

### Task 1: Buat `routers/chat.py`

#### 1a. `POST /conversations/` — Buat Conversation Baru

```python
router = APIRouter(prefix="/conversations", tags=["Chat"])

@router.post("/", response_model=ConversationResponse, status_code=201)
def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Buat conversation baru untuk sebuah dokumen.
    1. Validasi dokumen ada dan milik user
    2. Buat record Conversation
    """
    document = db.query(Document).filter(
        Document.id == data.document_id,
        Document.user_id == current_user.id,
        Document.status == "ready"
    ).first()
    
    if not document:
        raise HTTPException(404, "Document not found or not ready")
    
    conversation = Conversation(
        document_id=data.document_id,
        user_id=current_user.id,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation
```

#### 1b. `POST /conversations/{id}/messages` — Endpoint Q&A Utama

**Ini adalah endpoint paling penting di seluruh project.**

**Alur lengkap:**
1. Load conversation history dari DB (6 pesan terakhir untuk konteks)
2. Embed user query → retrieve top-5 chunks dari ChromaDB
3. Bangun prompt dengan: system instructions + context chunks + history + pertanyaan
4. Panggil Gemini LLM → dapatkan jawaban
5. Simpan pesan user + respons AI ke database
6. Return respons + source citations (nomor halaman chunk)

**System Prompt berdasarkan Level:**
```python
LEVEL_PROMPTS = {
    "beginner": """You are a patient tutor explaining to a complete beginner.
Use simple language, analogies, and step-by-step explanations.
Avoid jargon unless you explain it first.""",
    
    "intermediate": """You are a knowledgeable tutor explaining to someone 
with basic understanding. Use technical terms but explain complex concepts.
Provide examples where helpful.""",
    
    "expert": """You are a peer expert having a technical discussion.
Use precise technical language. Focus on nuances, edge cases, 
and advanced implications.""",
}
```

**Membangun Prompt:**
```python
def build_prompt(context_chunks, history, question, level, language):
    system = LEVEL_PROMPTS.get(level, LEVEL_PROMPTS["intermediate"])
    
    if language != "english":
        system += f"\n\nRespond in {language}, but keep all technical terms in English."
    
    context = "\n\n".join([
        f"[Page {c.metadata.get('page', '?')}]: {c.page_content}"
        for c in context_chunks
    ])
    
    history_text = "\n".join([
        f"{msg.role}: {msg.content}" for msg in history
    ])
    
    return f"""{system}

CONTEXT FROM DOCUMENT:
{context}

CONVERSATION HISTORY:
{history_text}

USER QUESTION: {question}

Answer based ONLY on the context provided. If the answer is not in the context, 
say so. Always cite which page(s) your answer comes from."""
```

**Memanggil Gemini LLM:**
```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.3,  # Rendah = lebih fokus dan konsisten
)

response = llm.invoke(prompt)
answer = response.content
```

**Extract Source Citations:**
```python
import json

def extract_sources(context_chunks):
    """Extract nomor halaman dari chunks yang digunakan."""
    pages = list(set([
        str(c.metadata.get("page", "unknown"))
        for c in context_chunks
    ]))
    return json.dumps({"pages": sorted(pages)})
```

#### 1c. `GET /conversations/{id}/messages` — Ambil History

```python
@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
def get_messages(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return semua pesan dalam conversation, urut dari terlama."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id,
    ).first()
    
    if not conversation:
        raise HTTPException(404, "Conversation not found")
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()
    
    return messages
```

---

### Task 2: Register Router di `main.py`

```python
from routers.chat import router as chat_router
app.include_router(chat_router)
```

---

### Task 3: Testing End-to-End

**Full Flow Test:**
1. Register + Login → dapatkan token
2. Upload PDF → tunggu status `ready`
3. Buat conversation → `POST /conversations/`
4. Kirim pertanyaan → `POST /conversations/{id}/messages`
5. Cek jawaban relevan dengan isi PDF
6. Kirim follow-up question → cek AI ingat konteks sebelumnya
7. Coba ganti level ke `beginner` → jawaban harus lebih sederhana
8. Coba ganti level ke `expert` → jawaban harus lebih teknis

---

## 🧠 Konsep yang Dipelajari

1. **Multi-turn Conversation** — AI mengingat pesan sebelumnya via history
2. **Prompt Engineering** — Membangun prompt yang efektif (system + context + history + question)
3. **Level Adjuster** — System prompt berbeda menghasilkan gaya jawaban berbeda
4. **Source Citations** — Traceability: user tahu jawaban berasal dari halaman mana
5. **Temperature** — Mengontrol kreativitas vs konsistensi LLM (0 = deterministik, 1 = kreatif)

---

## ✅ Checklist Verifikasi

- [ ] Buat conversation berhasil
- [ ] Kirim pertanyaan → dapat jawaban yang relevan dari PDF
- [ ] Source citations (halaman) muncul di response
- [ ] Follow-up question → AI ingat konteks sebelumnya
- [ ] Level beginner → jawaban sederhana
- [ ] Level expert → jawaban teknis
- [ ] Get messages → return history lengkap
- [ ] **Full backend selesai!** Semua fitur bisa di-test via Swagger/Postman

---

## ➡️ Preview Day 6

Besok mulai **frontend**: Login/Register UI + Document Dashboard dengan Next.js, Tailwind, dan Shadcn/UI.
