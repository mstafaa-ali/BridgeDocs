"""
BridgeDocs Backend — Authentication Router (routers/auth.py)

Endpoint yang tersedia:
  POST /auth/register  → Registrasi user baru
  POST /auth/login     → Login dan dapatkan JWT token
  GET  /auth/me        → Protected route — data user yang sedang login

Semua logika keamanan (hashing, JWT) di-import dari auth_utils.py.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserRegister, UserLogin, UserResponse, TokenResponse
from auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ---------------------------------------------------------------------------
# POST /auth/register — Registrasi User Baru
# ---------------------------------------------------------------------------

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrasi user baru",
    description=(
        "Menerima email, password, dan full_name. "
        "Password di-hash dengan bcrypt sebelum disimpan. "
        "Mengembalikan data user tanpa password."
    ),
)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Flow:
    1. Cek apakah email sudah terdaftar → 400 jika duplikat
    2. Hash password dengan bcrypt (JANGAN simpan plain text!)
    3. Buat record User baru di database
    4. Return data user (tanpa password)
    """
    # Langkah 1 — Cek duplikat email
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Langkah 2 — Hash password sebelum disimpan
    hashed = hash_password(user_data.password)

    # Langkah 3 — Buat user baru
    new_user = User(
        email=user_data.email,
        password_hash=hashed,
        full_name=user_data.full_name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Refresh agar mendapatkan id & created_at dari DB

    # Langkah 4 — Return user (Pydantic otomatis exclude password_hash)
    return new_user


# ---------------------------------------------------------------------------
# POST /auth/login — Login dan Dapatkan JWT Token
# ---------------------------------------------------------------------------

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
    description=(
        "Verifikasi email dan password, lalu kembalikan JWT access token. "
        "Gunakan token ini di header Authorization: Bearer <token> untuk "
        "mengakses protected routes."
    ),
)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Flow:
    1. Cari user berdasarkan email
    2. Verifikasi password dengan bcrypt
    3. Buat JWT token dengan user_id sebagai subject ("sub")
    4. Return access_token
    """
    # Langkah 1 — Cari user berdasarkan email
    user = db.query(User).filter(User.email == user_data.email).first()

    # Langkah 2 — Verifikasi user & password (cek keduanya sekaligus untuk
    # menghindari user enumeration attack)
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Langkah 3 — Buat JWT token; "sub" berisi user ID (sebagai string)
    token = create_access_token(data={"sub": str(user.id)})

    # Langkah 4 — Return token
    return TokenResponse(access_token=token)


# ---------------------------------------------------------------------------
# GET /auth/me — Protected Route (Butuh Token)
# ---------------------------------------------------------------------------

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Data user yang sedang login",
    description=(
        "Protected route — membutuhkan header Authorization: Bearer <token>. "
        "Dependency get_current_user otomatis decode JWT dan query user dari DB."
    ),
)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Flow (ditangani otomatis oleh dependency get_current_user):
    1. Extract token dari header Authorization
    2. Decode JWT dan ambil user_id dari klaim "sub"
    3. Query user dari database
    4. Return user object

    Jika token invalid/expired → otomatis return 401 Unauthorized
    """
    return current_user
