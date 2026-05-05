# 🟦 Day 3 — Backend: Document Upload API

> **Status:** ⏳ BELUM DIMULAI
> **Durasi Estimasi:** 4-5 jam
> **Goal:** Upload PDF, simpan file, trigger background ingestion.
> **Prasyarat:** Day 2 selesai — Auth system sudah berfungsi.

---

## 📋 Ringkasan

Hari ini membangun API untuk mengelola dokumen: upload PDF, list dokumen user, dan hapus dokumen. File PDF disimpan ke folder `uploads/`, record masuk database dengan status tracking (`processing` → `ready` / `failed`).

---

## 📝 Task Detail

### Task 1: Buat Folder `uploads/`

```bash
cd backend
mkdir uploads
```

Tambahkan `uploads/` ke `.gitignore`.

---

### Task 2: Buat `routers/documents.py`

File ini berisi 3 endpoint:

#### 2a. `POST /documents/upload` — Upload PDF
**Alur:**
1. Terima file PDF (multipart form-data), validasi tipe file
2. Generate unique filename: `{uuid4}_{original_name}.pdf`
3. Simpan ke `uploads/`
4. Buat record `Document` di DB dengan `status: "processing"`
5. Trigger background task untuk RAG ingestion (placeholder dulu, Day 4 baru real)
6. Return document data

**Hal penting:**
- Gunakan `UploadFile` + `shutil.copyfileobj()` untuk streaming (hemat memory)
- Validasi: cek `.pdf` extension DAN `content_type == "application/pdf"`
- Gunakan `FastAPI BackgroundTasks` agar user tidak menunggu ingestion

#### 2b. `GET /documents/` — List Semua Dokumen User
- Filter by `user_id` yang sedang login
- Urutkan dari terbaru (`order_by(created_at.desc())`)

#### 2c. `DELETE /documents/{document_id}` — Hapus Dokumen
**Alur:**
1. Cari dokumen (pastikan milik user yang login)
2. Hapus file fisik dari `uploads/`
3. Hapus vectors dari ChromaDB (placeholder, Day 4)
4. Hapus record DB (cascade otomatis hapus conversations & messages)

---

### Task 3: Register Router di `main.py`

```python
from routers.documents import router as documents_router
app.include_router(documents_router)
```

---

### Task 4: Testing dengan Swagger UI

| Test | Expected |
|------|----------|
| Upload PDF valid + token | 201 + document data |
| Upload non-PDF | 400 "Only PDF files are allowed" |
| List documents | 200 + array dokumen |
| Delete document | 204 No Content |
| Delete doc milik user lain | 404 |

**Verifikasi file tersimpan:**
```bash
ls -la backend/uploads/
```

---

## 🧠 Konsep yang Dipelajari

1. **File Upload di FastAPI** — `UploadFile` + streaming save
2. **Background Tasks** — Proses async setelah response terkirim
3. **Status Tracking Pattern** — `processing` → `ready` / `failed`
4. **Cascade Delete** — Hapus parent otomatis hapus children
5. **Unique Filename** — UUID prefix mencegah collision

---

## ✅ Checklist Verifikasi

- [ ] Upload PDF berhasil, file ada di `uploads/`
- [ ] Record ada di database dengan status `ready`
- [ ] List dokumen hanya tampilkan milik user yang login
- [ ] Delete hapus file fisik + record database
- [ ] Error handling: non-PDF, tanpa login, dokumen tidak ditemukan

---

## ➡️ Preview Day 4

Besok adalah **hari paling penting** — membangun **RAG Pipeline**: Extract text dari PDF → split chunks → embed dengan Gemini → simpan ke ChromaDB.
