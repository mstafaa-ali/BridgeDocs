"""
BridgeDocs Backend — Security Utilities (auth_utils.py)

Modul ini memusatkan semua logika keamanan:
  - Password hashing & verifikasi menggunakan bcrypt (via passlib)
  - Pembuatan JWT access token menggunakan python-jose

Cara import di router:
    from auth_utils import pwd_context, create_access_token, get_current_user
"""

import os
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
from models import User

# ---------------------------------------------------------------------------
# 1. Password Hashing — CryptContext dengan bcrypt
# ---------------------------------------------------------------------------

# Skema bcrypt dipilih karena:
#   - Menghasilkan hash unik setiap eksekusi (salt random otomatis)
#   - Tahan terhadap brute-force (cost factor bisa dinaikkan)
#   - deprecated="auto" → passlib otomatis upgrade hash lama jika diperlukan
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash password plain text menggunakan bcrypt.

    Args:
        plain_password: Password asli dari user.

    Returns:
        String hash yang aman untuk disimpan di database.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Bandingkan password plain text dengan hash yang tersimpan di database.

    Args:
        plain_password: Password yang diinput user saat login.
        hashed_password: Hash yang tersimpan di kolom ``password_hash``.

    Returns:
        True jika cocok, False jika tidak cocok.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# 2. JWT Configuration — baca dari environment variables
# ---------------------------------------------------------------------------

# Nilai default hanya untuk development lokal.
# Di production, WAJIB set semua variabel ini via .env / secrets manager.
SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "fallback-secret-key-change-in-production")
ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # default 24 jam


# ---------------------------------------------------------------------------
# 3. JWT Token — fungsi create & decode
# ---------------------------------------------------------------------------

def create_access_token(data: dict) -> str:
    """Buat JWT access token dengan expiration time.

    Menambahkan klaim ``exp`` (expiration) ke payload sebelum di-encode.

    Args:
        data: Payload yang akan di-encode ke dalam token.
              Biasanya berisi ``{"sub": str(user.id)}``.

    Returns:
        String JWT yang siap dikirim ke client.

    Example::

        token = create_access_token(data={"sub": str(user.id)})
        return TokenResponse(access_token=token)
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ---------------------------------------------------------------------------
# 4. OAuth2 Scheme — untuk protected routes
# ---------------------------------------------------------------------------

# FastAPI akan mengekstrak token dari header:  Authorization: Bearer <token>
# tokenUrl digunakan oleh Swagger UI untuk menampilkan tombol "Authorize".
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Dependency: Validasi JWT token dan kembalikan user yang sedang login.

    Digunakan sebagai FastAPI dependency injection pada protected routes::

        @router.get("/me", response_model=UserResponse)
        def get_me(current_user: User = Depends(get_current_user)):
            return current_user

    Args:
        token: Bearer token yang diekstrak otomatis dari header Authorization.
        db: Database session dari dependency ``get_db``.

    Returns:
        Object ``User`` yang valid dari database.

    Raises:
        HTTPException 401: Jika token tidak valid, expired, atau user tidak ditemukan.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user
