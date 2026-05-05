# 🟡 Day 4 — The RAG Pipeline (Hari Paling Penting)

> **Status:** ⏳ BELUM DIMULAI
> **Durasi Estimasi:** 6-8 jam (ambil waktu ekstra jika perlu!)
> **Goal:** PDF di-ingest ke ChromaDB. Query mengembalikan chunks yang relevan.
> **Prasyarat:** Day 3 selesai — Document upload API berfungsi.

---

## 📋 Ringkasan

Ini adalah **jantung dari BridgeDocs**. Hari ini kamu membangun pipeline RAG (Retrieval-Augmented Generation) lengkap:

```
PDF → Extract Text → Split Chunks → Embed dengan Gemini → Simpan ke ChromaDB → Query → Generate Answer
```

> ⚠️ **PENTING:** Jangan rush hari ini. Kualitas RAG pipeline menentukan kualitas seluruh aplikasi. Chat interface yang bagus di atas RAG yang buruk = tidak berguna.

---

## 📝 Task Detail

### Task 1: Buat `services/rag_pipeline.py`

File ini adalah inti dari seluruh project. Ada 4 tahap:

#### Tahap 1: Extract Text dari PDF
```python
from langchain_community.document_loaders import PyPDFLoader

# PyPDFLoader membaca PDF dan menghasilkan list of Document objects
# Setiap Document = 1 halaman PDF dengan content + metadata (page number)
loader = PyPDFLoader("path/to/file.pdf")
pages = loader.load()  # List[Document] — setiap item = 1 halaman
```

#### Tahap 2: Split Text ke Chunks
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Kenapa split? Karena:
# 1. LLM punya batas context window
# 2. Chunks kecil = retrieval lebih presisi
# 3. Embedding lebih akurat untuk teks pendek
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # Maksimal 500 karakter per chunk
    chunk_overlap=50,    # Overlap 50 karakter antar chunk (agar konteks tidak terpotong)
    separators=["\n\n", "\n", ". ", " ", ""]  # Prioritas pemisahan
)
chunks = splitter.split_documents(pages)
```

**Tips tuning `chunk_size`:**
- Terlalu kecil (100-200): konteks hilang, jawaban tidak nyambung
- Terlalu besar (1000+): retrieval kurang presisi, banyak noise
- **500 adalah sweet spot** untuk kebanyakan dokumen teknis

#### Tahap 3: Embed dengan Gemini
```python
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Embedding = mengubah teks menjadi vektor numerik (list of floats)
# Teks yang semantik mirip → vektor yang berdekatan
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
```

#### Tahap 4: Simpan ke ChromaDB
```python
from langchain_chroma import Chroma
import chromadb

# Setiap dokumen punya collection sendiri di ChromaDB
# collection_name = document_id (UUID)
chroma_client = chromadb.HttpClient(
    host=os.getenv("CHROMA_HOST", "localhost"),
    port=int(os.getenv("CHROMA_PORT", "8001"))
)

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name=str(document_id),
    client=chroma_client,
)
```

#### Fungsi Lengkap `ingest_document()`:
```python
def ingest_document(document_id: str, file_path: str):
    """
    Full ingestion pipeline:
    1. Load PDF → extract text per halaman
    2. Split ke chunks (500 chars, 50 overlap)
    3. Embed setiap chunk dengan Gemini embedding-001
    4. Simpan vectors ke ChromaDB (1 collection per document)
    """
    # Step 1: Load PDF
    loader = PyPDFLoader(file_path)
    pages = loader.load()

    # Step 2: Split ke chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(pages)

    # Tambahkan metadata ke setiap chunk
    for i, chunk in enumerate(chunks):
        chunk.metadata["document_id"] = document_id
        chunk.metadata["chunk_index"] = i

    # Step 3 & 4: Embed + Store
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=document_id,
        client=chroma_client,
    )
    return len(chunks)
```

#### Fungsi `query_document()`:
```python
def query_document(document_id: str, query: str, top_k: int = 5):
    """
    Cari chunks yang paling relevan dengan query user.
    
    Returns: List of (content, metadata) tuples
    """
    vectorstore = Chroma(
        collection_name=document_id,
        embedding_function=embeddings,
        client=chroma_client,
    )
    results = vectorstore.similarity_search(query, k=top_k)
    return results
```

#### Fungsi `delete_collection()`:
```python
def delete_collection(document_id: str):
    """Hapus collection dari ChromaDB saat dokumen dihapus."""
    try:
        chroma_client.delete_collection(name=document_id)
    except Exception:
        pass  # Collection mungkin tidak ada
```

---

### Task 2: Hubungkan Pipeline ke Document Upload (Update Day 3)

Update `routers/documents.py` untuk memanggil `ingest_document` via BackgroundTasks:

```python
from services.rag_pipeline import ingest_document, delete_collection

# Di endpoint upload, ganti placeholder dengan:
def process_document(document_id: str, file_path: str, db_url: str):
    """Background task: ingest document dan update status."""
    from database import SessionLocal
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        ingest_document(str(document_id), file_path)
        doc.status = "ready"
        db.commit()
    except Exception as e:
        doc.status = "failed"
        db.commit()
        print(f"Ingestion failed: {e}")
    finally:
        db.close()

# Di endpoint upload:
background_tasks.add_task(process_document, str(document.id), file_path, "")
```

---

### Task 3: Buat Test Script `test_rag.py`

```python
"""
Test RAG pipeline secara mandiri (tanpa API).
Jalankan: python test_rag.py
"""
from services.rag_pipeline import ingest_document, query_document

# Step 1: Ingest sebuah PDF
print("📄 Ingesting PDF...")
num_chunks = ingest_document("test-doc-001", "uploads/sample.pdf")
print(f"✅ Ingested {num_chunks} chunks")

# Step 2: Query
print("\n🔍 Querying...")
results = query_document("test-doc-001", "What is this document about?")
for i, doc in enumerate(results):
    print(f"\n--- Chunk {i+1} (Page {doc.metadata.get('page', '?')}) ---")
    print(doc.page_content[:200])

print("\n✅ RAG pipeline working!")
```

**Jalankan:**
```bash
cd backend
python test_rag.py
```

---

### Task 4: Validasi Kualitas RAG

Ini langkah paling penting. Coba beberapa query dan evaluasi:

| Query | Apakah chunks yang dikembalikan relevan? |
|-------|------------------------------------------|
| "What is the main topic?" | Harus return intro/abstrak |
| "How to install?" | Harus return bagian installation |
| Pertanyaan spesifik dari isi PDF | Harus return bagian yang tepat |

**Jika hasilnya buruk**, coba adjust:
- `chunk_size`: naikkan ke 700-1000
- `chunk_overlap`: naikkan ke 100
- `top_k`: naikkan ke 7-10

---

## 🧠 Konsep yang Dipelajari

1. **RAG (Retrieval-Augmented Generation)** — LLM menjawab berdasarkan dokumen, bukan "hafalan"
2. **Text Splitting** — Memecah dokumen besar ke chunk kecil untuk retrieval presisi
3. **Embeddings** — Representasi numerik dari makna teks (semantic similarity)
4. **Vector Database** — Database khusus untuk menyimpan dan mencari vektor
5. **Similarity Search** — Mencari chunks yang semantik paling mirip dengan query

---

## ✅ Checklist Verifikasi

- [ ] `ingest_document()` berhasil memproses PDF tanpa error
- [ ] Chunks tersimpan di ChromaDB (cek via `http://localhost:8001`)
- [ ] `query_document()` mengembalikan chunks yang relevan
- [ ] Upload PDF via API → status berubah dari `processing` ke `ready`
- [ ] Delete document → collection di ChromaDB juga terhapus
- [ ] Test dengan minimal 2 PDF berbeda

---

## ➡️ Preview Day 5

Besok membangun **Chat API** — endpoint Q&A lengkap dengan conversation history dan multi-turn memory.
