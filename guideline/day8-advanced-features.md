# 🔴 Day 8 — Advanced Features

> **Status:** ⏳ BELUM DIMULAI
> **Durasi Estimasi:** 6-7 jam
> **Goal:** Multilingual support, Quiz generator, dan Landing page.
> **Prasyarat:** Day 7 selesai — Chat interface split-view berfungsi.

---

## 📋 Ringkasan

Hari ini menambahkan fitur-fitur yang mengubah BridgeDocs dari demo menjadi produk nyata: support multi-bahasa, quiz generator dari konten dokumen, dan landing page profesional untuk impresi pertama.

---

## 📝 Task Detail

### Task 1: Multilingual Support

#### 1a. Backend — Update System Prompt

Di `routers/chat.py`, tambahkan logic bahasa ke prompt:

```python
# Daftar bahasa yang didukung
SUPPORTED_LANGUAGES = {
    "english": "English",
    "indonesian": "Indonesian (Bahasa Indonesia)",
    "arabic": "Arabic",
    "french": "French",
    "spanish": "Spanish",
    "japanese": "Japanese",
    "korean": "Korean",
    "chinese": "Chinese (Simplified)",
}

# Inject ke system prompt:
if language != "english":
    language_instruction = (
        f"Respond in {SUPPORTED_LANGUAGES.get(language, language)}, "
        f"but keep all technical terms, code snippets, and proper nouns in English "
        f"for professional accuracy."
    )
    system_prompt += f"\n\n{language_instruction}"
```

**Contoh output:**
- Query: "What is dependency injection?" (language: indonesian)
- AI: "Dependency Injection adalah sebuah design pattern di mana object menerima dependensi-nya dari luar, bukan membuat sendiri. Ini mengikuti prinsip Inversion of Control..."

#### 1b. Frontend — Language Dropdown

Tambahkan dropdown di toolbar chat (sebelah level toggle):

```
[🌐 English ▼] [Beginner] [Intermediate] [Expert]
```

- Default: English
- Kirimkan `language` bersama setiap message ke API
- Simpan preferensi di localStorage

---

### Task 2: Quiz Generator

#### 2a. Backend — `POST /quiz/{document_id}`

Buat endpoint baru untuk generate quiz dari dokumen:

```python
# Di routers/chat.py atau buat routers/quiz.py baru

@router.post("/quiz/{document_id}")
def generate_quiz(
    document_id: uuid.UUID,
    num_questions: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate MCQ quiz dari konten dokumen.
    
    Alur:
    1. Ambil random chunks dari ChromaDB
    2. Kirim ke Gemini dengan prompt khusus quiz
    3. Parse response menjadi list pertanyaan
    4. Return quiz data
    """
```

**Quiz Prompt Template:**
```python
QUIZ_PROMPT = """Based on the following document content, generate exactly {num} 
multiple-choice questions to test understanding.

CONTENT:
{context}

FORMAT your response as a JSON array:
[
  {{
    "question": "What is...?",
    "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
    "correct": "A",
    "explanation": "The answer is A because..."
  }}
]

Rules:
- Questions should test understanding, not just recall
- All options should be plausible
- Include a brief explanation for the correct answer
- Cover different parts of the content
"""
```

**Response Schema:**
```python
class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct: str  # "A", "B", "C", atau "D"
    explanation: str

class QuizResponse(BaseModel):
    document_id: UUID
    questions: List[QuizQuestion]
```

#### 2b. Frontend — Quiz Modal/Page

- Tombol "📝 Take Quiz" di dashboard atau chat page
- Modal atau halaman baru yang menampilkan quiz
- Satu pertanyaan per layar, navigasi Next/Previous
- Pilih jawaban → highlight benar/salah setelah submit
- Show penjelasan untuk jawaban salah
- Score di akhir: "You got 4/5! 🎉"
- Tombol "Retry" untuk coba lagi

---

### Task 3: Landing Page (`/`)

**Ini WAJIB untuk portfolio project!** Recruiter dan visitor landing di halaman ini pertama kali.

#### Struktur Landing Page:

**Hero Section:**
```
╔══════════════════════════════════════════════════╗
║                                                  ║
║     🌉 BridgeDocs                                ║
║                                                  ║
║     Chat with any technical document             ║
║     AI-powered tutor that understands your PDFs  ║
║                                                  ║
║     [Get Started Free →]    [Watch Demo]         ║
║                                                  ║
╚══════════════════════════════════════════════════╝
```

**Features Section (3-4 cards):**
1. 📄 **Smart Document Chat** — Upload PDF, ask questions, get precise answers
2. 🎯 **Level Adjuster** — Beginner to Expert explanations
3. 🌐 **Multilingual** — Learn in your language, keep terms in English
4. 📝 **Quiz Generator** — Test your understanding automatically

**How It Works Section:**
```
Upload PDF → AI Processes → Ask Questions → Learn Faster
   (1)           (2)            (3)            (4)
```

**Tech Stack Section (opsional):**
Badge/icons: Next.js, FastAPI, LangChain, Gemini, ChromaDB, PostgreSQL

**CTA Section:**
```
Ready to learn faster?
[Create Free Account →]
```

**Desain Tips:**
- Gunakan gradient background (dark theme recommended)
- Animasi subtle (fade-in saat scroll)
- Responsive (works on mobile)
- Professional typography (Inter atau Outfit dari Google Fonts)

---

## 🧠 Konsep yang Dipelajari

1. **Multilingual Prompt Engineering** — Instruksi bahasa dalam system prompt
2. **Structured Output from LLM** — Meminta LLM output JSON yang bisa di-parse
3. **Landing Page Design** — Hero, features, how-it-works, CTA pattern
4. **JSON Parsing dari LLM** — Handle case di mana LLM output bukan valid JSON

---

## ✅ Checklist Verifikasi

- [ ] Chat dalam bahasa Indonesia → AI jawab dalam Bahasa Indonesia
- [ ] Technical terms tetap dalam English di semua bahasa
- [ ] Quiz generate 5 pertanyaan MCQ dari dokumen
- [ ] Quiz UI menampilkan pertanyaan, pilihan, dan score
- [ ] Landing page terlihat profesional
- [ ] Landing page responsive (mobile + desktop)
- [ ] CTA buttons navigate ke login/register
- [ ] **Feature-complete MVP!** 🎉

---

## ➡️ Preview Day 9

Besok fokus **UI polish**: loading states, error handling, dark mode, animasi, dan responsive design.
