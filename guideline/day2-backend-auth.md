# 🟦 Day 2 — Backend: Database + Auth

> **Status:** ⏳ BELUM DIMULAI
> **Durasi Estimasi:** 4-6 jam
> **Goal:** User bisa register dan login. JWT token berfungsi.
> **Prasyarat:** Day 1 selesai — Docker, FastAPI, dan Next.js sudah running.

---

## 📋 Ringkasan

Hari ini kamu akan membangun sistem autentikasi lengkap: registrasi user, login, dan proteksi route menggunakan JWT (JSON Web Token). Di akhir hari, kamu bisa mendaftar user baru, login, mendapat token, dan mengakses protected route.

---

## 📝 Task Detail

### Task 1: Pastikan Services Day 1 Masih Running

```bash
# Cek Docker containers
docker ps
# Harus muncul bridgedocs-postgres dan bridgedocs-chromadb

# Aktifkan virtual environment
cd backend
source venv/bin/activate

# Cek FastAPI masih bisa jalan
uvicorn main:app --reload
# Buka http://localhost:8000/docs → harus muncul
```

---

### Task 2: Buat File `routers/auth.py` — Endpoint Autentikasi

File ini berisi 3 endpoint utama:

#### 2a. `POST /auth/register` — Registrasi User Baru

**Alur:**
1. Terima data `email`, `password`, `full_name` dari request body
2. Cek apakah email sudah terdaftar → jika ya, return error 400
3. Hash password menggunakan `bcrypt` (JANGAN simpan password plain text!)
4. Buat record `User` baru di database
5. Return data user (tanpa password)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os

from database import get_db
from models import User
from schemas import UserRegister, UserLogin, UserResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT config
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 jam


def create_access_token(data: dict):
    """Buat JWT token dengan expiration time."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Dependency: Extract dan validasi user dari JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Registrasi user baru.
    
    Flow:
    1. Cek apakah email sudah terdaftar
    2. Hash password dengan bcrypt
    3. Simpan user ke database
    4. Return user data (tanpa password)
    """
    # Cek duplicate email
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password — JANGAN pernah simpan plain text!
    hashed = pwd_context.hash(user_data.password)
    
    # Buat user baru
    new_user = User(
        email=user_data.email,
        password_hash=hashed,
        full_name=user_data.full_name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Refresh untuk mendapatkan id dan created_at
    
    return new_user
```

#### 2b. `POST /auth/login` — Login dan Dapatkan Token

**Alur:**
1. Terima `email` dan `password`
2. Cari user berdasarkan email
3. Verifikasi password dengan `bcrypt` → bandingkan hash
4. Jika valid, buat JWT token
5. Return token

```python
@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login user dan return JWT token.
    
    Flow:
    1. Cari user berdasarkan email
    2. Verifikasi password dengan bcrypt
    3. Buat JWT token dengan user_id sebagai subject
    4. Return access_token
    """
    user = db.query(User).filter(User.email == user_data.email).first()
    
    # Cek user exists DAN password benar
    if not user or not pwd_context.verify(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Buat JWT token — "sub" (subject) berisi user ID
    token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(access_token=token)
```

#### 2c. `GET /auth/me` — Protected Route (Butuh Token)

**Alur:**
1. Extract JWT token dari header `Authorization: Bearer <token>`
2. Decode token → ambil `user_id`
3. Cari user di database
4. Return user data

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Protected route — return data user yang sedang login.
    
    Dependency `get_current_user` otomatis:
    1. Extract token dari header Authorization
    2. Decode JWT
    3. Query user dari database
    4. Return user object
    
    Jika token invalid/expired → auto return 401
    """
    return current_user
```

> **💡 Konsep Penting — OAuth2PasswordBearer:** Ini memberitahu FastAPI bahwa endpoint ini membutuhkan token Bearer. Di Swagger UI (`/docs`), akan muncul tombol "Authorize" di mana kamu bisa paste token.

---

### Task 3: Register Router di `main.py`

Tambahkan import dan include router di `main.py`:

```python
# Tambahkan di bagian import
from routers.auth import router as auth_router

# Tambahkan setelah CORS middleware
app.include_router(auth_router)
```

Sekarang endpoint `/auth/register`, `/auth/login`, dan `/auth/me` sudah terdaftar.

---

### Task 4: Testing dengan Swagger UI / Postman

FastAPI otomatis generate interactive API docs di `http://localhost:8000/docs`.

#### Test Flow:

**Step 1: Register user baru**
```
POST /auth/register
Body:
{
    "email": "ali@example.com",
    "password": "password123",
    "full_name": "Ali"
}
```
Expected response (201):
```json
{
    "id": "550e8400-e29b-41d4-...",
    "email": "ali@example.com",
    "full_name": "Ali",
    "created_at": "2026-05-02T..."
}
```

**Step 2: Login**
```
POST /auth/login
Body:
{
    "email": "ali@example.com",
    "password": "password123"
}
```
Expected response (200):
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```

**Step 3: Akses protected route**
```
GET /auth/me
Header: Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```
Expected response (200):
```json
{
    "id": "550e8400-e29b-41d4-...",
    "email": "ali@example.com",
    "full_name": "Ali",
    "created_at": "2026-05-02T..."
}
```

**Step 4: Test error cases**
- Register dengan email yang sama → 400 "Email already registered"
- Login dengan password salah → 401 "Invalid email or password"
- Akses `/auth/me` tanpa token → 401 "Not authenticated"
- Akses `/auth/me` dengan token invalid → 401 "Invalid token"

---

## 🧠 Konsep yang Dipelajari

### 1. Password Hashing (bcrypt)
- JANGAN pernah simpan password plain text di database
- `bcrypt` menghasilkan hash yang berbeda setiap kali (karena salt random)
- Verifikasi: `pwd_context.verify("plain_password", hashed_password)` → True/False

### 2. JWT (JSON Web Token)
- Token berisi payload (data) yang di-encode, bukan dienkripsi
- Siapapun bisa membaca isi JWT (decode di jwt.io), tapi tidak bisa memodifikasi tanpa secret key
- Token punya expiration time (`exp`) — setelah expired, token tidak valid
- `sub` (subject) biasanya berisi user identifier

### 3. Dependency Injection di FastAPI
- `Depends(get_db)` → otomatis buat & tutup database session
- `Depends(get_current_user)` → otomatis validasi token & ambil user
- Bisa di-chain: `get_current_user` sendiri depends on `oauth2_scheme` dan `get_db`

### 4. HTTP Status Codes
- `201 Created` → resource berhasil dibuat (register)
- `200 OK` → request berhasil (login, get me)
- `400 Bad Request` → input salah (duplicate email)
- `401 Unauthorized` → tidak punya akses (token invalid/missing)

---

## ✅ Checklist Verifikasi Akhir

- [ ] `POST /auth/register` → berhasil buat user baru
- [ ] `POST /auth/register` dengan email duplikat → return 400
- [ ] `POST /auth/login` → return JWT token
- [ ] `POST /auth/login` dengan password salah → return 401
- [ ] `GET /auth/me` dengan valid token → return user data
- [ ] `GET /auth/me` tanpa token → return 401
- [ ] Password tersimpan sebagai hash di database (bukan plain text)
- [ ] Cek database langsung: `docker exec -it bridgedocs-postgres psql -U admin -d bridgedocs -c "SELECT id, email, password_hash FROM users;"`

---

## 🔧 Troubleshooting

| Problem | Penyebab | Solusi |
|---------|----------|--------|
| `ModuleNotFoundError: passlib` | Belum install dependencies | `pip install passlib[bcrypt] python-jose[cryptography]` |
| `relation "users" does not exist` | Tabel belum dibuat | Pastikan `Base.metadata.create_all(bind=engine)` ada di `main.py` |
| `jwt.JWTError` saat login | Secret key berubah | Pastikan `JWT_SECRET_KEY` di `.env` konsisten |
| `422 Unprocessable Entity` | Format request body salah | Cek format JSON sesuai schema Pydantic |

---

## ➡️ Preview Day 3

Besok kita akan membangun **Document Upload API**: endpoint untuk upload PDF, menyimpan file, dan membuat record di database dengan status tracking.
