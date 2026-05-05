# 🟠 Day 7 — Frontend: Chat Interface (Fitur WOW)

> **Status:** ⏳ BELUM DIMULAI
> **Durasi Estimasi:** 6-8 jam
> **Goal:** Split-view chat UI — PDF viewer + Chat window side by side.
> **Prasyarat:** Day 6 selesai — Auth + Dashboard frontend berfungsi.

---

## 📋 Ringkasan

Hari ini membangun fitur utama yang membuat portfolio standout: interface chat split-view. User bisa melihat PDF di sisi kiri dan bercakap dengan AI tentang isinya di sisi kanan — mirip ChatGPT tapi dengan konteks dokumen.

---

## 📝 Task Detail

### Task 1: Setup Halaman `/chat/[id]`

Buat halaman di `src/app/chat/[id]/page.tsx` dengan layout split-view:

```
┌──────────────────────┬──────────────────────┐
│   PDF Viewer         │   Chat Window        │
│   (react-pdf)        │   (messages + input) │
│                      │                      │
│   ← Halaman PDF      │   💬 User: ...       │
│     bisa di-scroll    │   🤖 AI: ...         │
│     dan zoom          │                      │
│                      │   [Type message...]   │
└──────────────────────┴──────────────────────┘
```

---

### Task 2: Install & Setup react-pdf

```bash
cd frontend
npm install react-pdf
```

**Buat komponen `PDFViewer`:**
- Render PDF dari URL backend (`/documents/{id}/file`)
- Navigasi halaman: Previous / Next / Jump to page
- Zoom in/out
- Highlight halaman yang dikutip AI (dari source citations)

**Endpoint baru di backend (tambahkan di `routers/documents.py`):**
```python
from fastapi.responses import FileResponse

@router.get("/{document_id}/file")
def get_document_file(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Serve file PDF untuk viewer di frontend."""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
    ).first()
    if not document:
        raise HTTPException(404, "Document not found")
    return FileResponse(document.file_path, media_type="application/pdf")
```

---

### Task 3: Buat Chat Window Component

**Komponen utama:**

#### 3a. Message Bubbles
- **User bubble**: rata kanan, warna primary
- **AI bubble**: rata kiri, warna secondary/muted
- Tampilkan timestamp di bawah setiap bubble
- AI bubble support markdown rendering (code blocks, lists, bold, dll)

Install untuk markdown rendering:
```bash
npm install react-markdown remark-gfm
```

#### 3b. Chat Input
- Text input area (bisa multi-line dengan textarea)
- Tombol Send (juga bisa Enter untuk kirim, Shift+Enter untuk newline)
- Disabled saat menunggu respons AI
- Loading indicator saat AI sedang menjawab

#### 3c. Toolbar — Level Toggle
Pill buttons untuk memilih level penjelasan:
```
[Beginner] [Intermediate] [Expert]
```
- Default: Intermediate
- Kirimkan level yang dipilih bersama setiap message

---

### Task 4: Implementasi Streaming Responses (SSE)

**Ini yang membuat pengalaman chat terasa seperti ChatGPT.**

Di backend, ubah endpoint chat untuk streaming:
```python
from fastapi.responses import StreamingResponse

@router.post("/{conversation_id}/messages/stream")
async def send_message_stream(conversation_id, data, ...):
    """Stream response word by word menggunakan Server-Sent Events."""
    
    async def generate():
        # ... retrieve chunks, build prompt ...
        async for chunk in llm.astream(prompt):
            yield f"data: {chunk.content}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

Di frontend, gunakan `EventSource` atau `fetch` dengan streaming:
```typescript
const response = await fetch(`${API_BASE}/conversations/${id}/messages/stream`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({ content: message, level }),
});

const reader = response.body?.getReader();
const decoder = new TextDecoder();

while (true) {
    const { done, value } = await reader!.read();
    if (done) break;
    const text = decoder.decode(value);
    // Update AI message character by character
    setCurrentMessage(prev => prev + text);
}
```

> **💡 Jika streaming terlalu kompleks**, bisa skip dulu dan gunakan endpoint biasa (non-streaming). Streaming bisa ditambahkan di Day 9 sebagai polish.

---

### Task 5: Tampilkan Source Citations

Di bawah setiap AI response, tampilkan sumber:

```
📄 Sources: Page 4, Page 7, Page 12
```

- Parse `sources` field dari response (JSON string)
- Klik nomor halaman → PDF viewer otomatis scroll ke halaman tersebut
- Styling: badge kecil yang bisa diklik

---

### Task 6: Conversation Management

- Sidebar kiri (opsional) untuk list conversations per dokumen
- Tombol "New Conversation" untuk mulai chat baru
- Auto-scroll ke pesan terbaru
- Load pesan lama saat buka conversation yang sudah ada

---

## 🧠 Konsep yang Dipelajari

1. **Split Layout** — CSS Grid/Flexbox untuk membagi layar
2. **react-pdf** — Render PDF di browser
3. **SSE (Server-Sent Events)** — Streaming response real-time
4. **Markdown Rendering** — Render formatted text dari AI
5. **State Management** — Manage loading, messages, dan scroll position

---

## ✅ Checklist Verifikasi

- [ ] PDF viewer menampilkan dokumen dengan benar
- [ ] Navigasi halaman PDF bekerja
- [ ] Chat input bisa mengirim pesan
- [ ] AI merespons dengan jawaban relevan
- [ ] Chat bubbles ditampilkan dengan benar (user kanan, AI kiri)
- [ ] Source citations muncul di bawah respons AI
- [ ] Level toggle (Beginner/Intermediate/Expert) mempengaruhi jawaban
- [ ] Streaming response bekerja (teks muncul bertahap) — opsional
- [ ] Auto-scroll ke pesan terbaru

---

## ➡️ Preview Day 8

Besok menambahkan **fitur lanjutan**: multilingual support, quiz generator, dan landing page.
