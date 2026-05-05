# 🟠 Day 6 — Frontend: Auth + Dashboard

> **Status:** ⏳ BELUM DIMULAI
> **Durasi Estimasi:** 6-7 jam
> **Goal:** Login/Register UI + Document Dashboard berfungsi.
> **Prasyarat:** Day 5 selesai — Seluruh backend API sudah working.

---

## 📋 Ringkasan

Hari ini mulai membangun frontend. Fokus pada: halaman login/register, autentikasi context (simpan token), proteksi route, dan dashboard dokumen dengan fitur upload dan manajemen PDF.

---

## 📝 Task Detail

### Task 1: Setup API Client — `lib/api.ts`

Buat wrapper untuk semua API calls ke backend:

```typescript
// src/lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAPI(endpoint: string, options: RequestInit = {}) {
    const token = localStorage.getItem("token");
    const headers: HeadersInit = {
        ...options.headers,
    };
    
    // Tambahkan Authorization header jika ada token
    if (token) {
        (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
    }
    
    // Tambahkan Content-Type untuk JSON (kecuali FormData)
    if (!(options.body instanceof FormData)) {
        (headers as Record<string, string>)["Content-Type"] = "application/json";
    }
    
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
    });
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || "Something went wrong");
    }
    
    // Handle 204 No Content
    if (response.status === 204) return null;
    
    return response.json();
}

// Auth API
export const authAPI = {
    register: (data: { email: string; password: string; full_name?: string }) =>
        fetchAPI("/auth/register", { method: "POST", body: JSON.stringify(data) }),
    login: (data: { email: string; password: string }) =>
        fetchAPI("/auth/login", { method: "POST", body: JSON.stringify(data) }),
    me: () => fetchAPI("/auth/me"),
};

// Documents API
export const documentsAPI = {
    list: () => fetchAPI("/documents/"),
    upload: (file: File) => {
        const formData = new FormData();
        formData.append("file", file);
        return fetchAPI("/documents/upload", { method: "POST", body: formData });
    },
    delete: (id: string) => fetchAPI(`/documents/${id}`, { method: "DELETE" }),
};
```

**Tambahkan `.env.local` di frontend:**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

### Task 2: Buat Auth Context — `contexts/AuthContext.tsx`

```typescript
// src/contexts/AuthContext.tsx
"use client";
import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { authAPI } from "@/lib/api";

interface User {
    id: string;
    email: string;
    full_name: string | null;
}

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, password: string, fullName?: string) => Promise<void>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    // Cek token saat app load
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (token) {
            authAPI.me()
                .then(setUser)
                .catch(() => localStorage.removeItem("token"))
                .finally(() => setLoading(false));
        } else {
            setLoading(false);
        }
    }, []);

    const login = async (email: string, password: string) => {
        const data = await authAPI.login({ email, password });
        localStorage.setItem("token", data.access_token);
        const userData = await authAPI.me();
        setUser(userData);
    };

    const register = async (email: string, password: string, fullName?: string) => {
        await authAPI.register({ email, password, full_name: fullName });
        await login(email, password); // Auto-login setelah register
    };

    const logout = () => {
        localStorage.removeItem("token");
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) throw new Error("useAuth must be used within AuthProvider");
    return context;
};
```

---

### Task 3: Buat Halaman Login & Register

Install Shadcn components yang dibutuhkan:
```bash
npx shadcn@latest add button input label card
```

Buat halaman `/login` dan `/register` dengan form Shadcn:
- Form fields: Email, Password, Full Name (register only)
- Error handling: tampilkan pesan error dari API
- Redirect ke `/dashboard` setelah berhasil
- Link navigasi antara login ↔ register

---

### Task 4: Proteksi Route dengan Middleware

Buat middleware Next.js untuk redirect user yang belum login:
- `/dashboard`, `/chat/*` → redirect ke `/login` jika belum login
- `/login`, `/register` → redirect ke `/dashboard` jika sudah login

---

### Task 5: Buat Halaman Dashboard — `/dashboard`

Dashboard berisi:

#### 5a. Upload Button (Drag & Drop)
- Area drag & drop untuk upload PDF
- Juga ada button "Choose File" sebagai alternatif
- Validasi: hanya terima `.pdf`
- Show progress/loading saat upload

#### 5b. Document Cards Grid
Setiap card menampilkan:
- **Title** dokumen
- **Date** uploaded (formatted)
- **Status badge**: 
  - 🟡 `processing` (kuning, dengan spinner)
  - 🟢 `ready` (hijau)
  - 🔴 `failed` (merah)
- **Delete button** dengan konfirmasi dialog
- **Click card** → navigate ke `/chat/[document_id]` (jika status `ready`)

#### 5c. Empty State
Jika belum ada dokumen: tampilkan ilustrasi + pesan "Upload your first document to get started"

---

### Task 6: Testing

| Test | Expected |
|------|----------|
| Register akun baru | Berhasil, redirect ke dashboard |
| Login | Berhasil, redirect ke dashboard |
| Logout | Kembali ke login |
| Akses dashboard tanpa login | Redirect ke login |
| Upload PDF | Card muncul di dashboard |
| Delete dokumen | Card hilang dari dashboard |
| Refresh halaman | Tetap login (token tersimpan) |

---

## 🧠 Konsep yang Dipelajari

1. **Auth Context (React)** — Global state untuk autentikasi
2. **localStorage Token** — Menyimpan JWT token di browser
3. **Route Protection** — Middleware Next.js untuk guard halaman
4. **Shadcn/UI Components** — Copy-paste component yang bisa dikustomisasi
5. **Optimistic UI** — Update UI sebelum API selesai (UX lebih responsif)

---

## ✅ Checklist Verifikasi

- [ ] Register → auto-login → redirect ke dashboard
- [ ] Login → redirect ke dashboard
- [ ] Logout → redirect ke login
- [ ] Dashboard menampilkan list dokumen
- [ ] Upload PDF → card muncul
- [ ] Delete → card hilang
- [ ] Status badge sesuai (processing/ready/failed)
- [ ] Click card ready → navigate ke chat page
- [ ] Protected routes bekerja

---

## ➡️ Preview Day 7

Besok membangun **Chat Interface** — split-view PDF viewer + chat window. Ini fitur WOW yang membuat portfolio standout.
