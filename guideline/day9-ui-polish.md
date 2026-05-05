# ⚪ Day 9 — UI Polish + Error Handling

> **Status:** ⏳ BELUM DIMULAI
> **Durasi Estimasi:** 5-6 jam
> **Goal:** Buat aplikasi terasa premium, bukan seperti tugas sekolah.
> **Prasyarat:** Day 8 selesai — Semua fitur sudah diimplementasi.

---

## 📋 Ringkasan

Hari ini fokus pada polish: loading states, error handling, dark mode, animasi, dan responsive design. Perbedaan antara "demo project" dan "portfolio-worthy app" ada di detail-detail ini.

---

## 📝 Task Detail

### Task 1: Loading Skeletons (Everywhere)

Tambahkan skeleton loading di semua tempat yang memuat data:

#### Dashboard:
- Document cards → skeleton cards (3-4 placeholder cards dengan animasi pulse)
- Upload area → loading spinner + progress bar saat upload

#### Chat Page:
- PDF viewer → skeleton placeholder sampai PDF dimuat
- Chat messages → typing indicator ("AI is thinking...")
- Initial load → skeleton bubbles

#### Quiz:
- Generate quiz → loading dengan pesan "Generating questions..."

**Install:**
```bash
npx shadcn@latest add skeleton
```

**Pattern:**
```tsx
{loading ? (
    <div className="space-y-4">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
    </div>
) : (
    <DocumentGrid documents={documents} />
)}
```

---

### Task 2: Error Handling (Semua Edge Cases)

| Scenario | UI Response |
|----------|-------------|
| Upload PDF kosong/corrupt | Toast: "This PDF could not be processed" |
| API timeout | Toast: "Server is taking too long. Please try again." |
| Upload gagal (network) | Toast: "Upload failed. Check your connection." |
| Document ingestion failed | Status badge merah + tooltip "Processing failed" |
| Chat saat document masih processing | Disable input + "Document is still processing..." |
| Token expired | Auto-redirect ke login + toast "Session expired" |
| Server down | Full-page error state dengan retry button |

**Install toast notification:**
```bash
npx shadcn@latest add toast sonner
```

**Pattern:**
```tsx
import { toast } from "sonner";

try {
    await documentsAPI.upload(file);
    toast.success("Document uploaded successfully!");
} catch (error) {
    toast.error(error.message || "Upload failed");
}
```

---

### Task 3: Dark Mode Toggle

**Setup Shadcn dark mode:**

1. Sudah built-in di Shadcn/UI jika menggunakan CSS variables
2. Tambahkan theme provider dan toggle button

```bash
npx shadcn@latest add dropdown-menu
```

**Buat `ThemeProvider` dan `ThemeToggle` component:**
- Simpan preferensi di localStorage
- 3 mode: Light / Dark / System
- Toggle button di navbar/header

**CSS:**
```css
:root {
    --background: 0 0% 100%;
    --foreground: 240 10% 3.9%;
    /* ... light mode colors */
}

.dark {
    --background: 240 10% 3.9%;
    --foreground: 0 0% 98%;
    /* ... dark mode colors */
}
```

---

### Task 4: Responsive Design

Test dan fix untuk semua breakpoints:

| Breakpoint | Layout |
|-----------|--------|
| Desktop (>1024px) | Split view: PDF kiri + Chat kanan |
| Tablet (768-1024px) | Tab view: toggle antara PDF dan Chat |
| Mobile (<768px) | Full-width: Chat only, PDF di modal/drawer |

**Key areas yang harus responsive:**
- Navbar/header
- Dashboard grid (3 kolom → 2 → 1)
- Chat split view → stacked/tab view
- Landing page sections
- Forms (login/register)

---

### Task 5: Animasi Subtle (Framer Motion)

```bash
npm install framer-motion
```

**Animasi yang direkomendasikan:**

#### Page Transitions:
```tsx
import { motion } from "framer-motion";

<motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.3 }}
>
    {children}
</motion.div>
```

#### Chat Bubbles (muncul dari bawah):
```tsx
<motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.2 }}
>
    <ChatBubble message={message} />
</motion.div>
```

#### Document Cards (stagger animation):
```tsx
{documents.map((doc, i) => (
    <motion.div
        key={doc.id}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: i * 0.1 }}
    >
        <DocumentCard document={doc} />
    </motion.div>
))}
```

#### Hover Effects:
- Document cards: slight scale up + shadow
- Buttons: subtle color transition
- Navigation links: underline slide-in

---

### Task 6: UI Refinements

#### Typography:
- Import font dari Google Fonts (Inter atau Outfit)
- Consistent heading sizes (h1: 2.5rem, h2: 2rem, h3: 1.5rem)
- Body text: 1rem, line-height: 1.6

#### Spacing:
- Consistent padding/margin (menggunakan 4px grid: 4, 8, 12, 16, 24, 32, 48)
- Adequate whitespace antar sections

#### Color Palette:
- Primary: biru/indigo (profesional)
- Accent: teal/emerald (energi)
- Destructive: merah untuk delete actions
- Muted: abu-abu untuk secondary text

---

## ✅ Checklist Verifikasi

- [ ] Loading skeletons di dashboard, chat, dan quiz
- [ ] Toast notifications untuk success/error
- [ ] Error states: empty, offline, timeout, expired token
- [ ] Dark mode toggle berfungsi + preferensi tersimpan
- [ ] Responsive: desktop, tablet, mobile
- [ ] Animasi subtle pada page transitions dan cards
- [ ] Typography dan spacing konsisten
- [ ] Hover effects pada interactive elements
- [ ] **Aplikasi terasa premium dan polished!**

---

## ➡️ Preview Day 10

Besok adalah hari terakhir — **Deploy & Launch**: Vercel, Railway, Supabase, dan README.
