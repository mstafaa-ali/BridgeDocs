"""
BridgeDocs Backend — Pydantic Schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ─── Auth Schemas ─────────────────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ─── Document Schemas ────────────────────────────────────

class DocumentResponse(BaseModel):
    id: UUID
    title: str
    status: str
    page_count: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Conversation Schemas ────────────────────────────────

class ConversationCreate(BaseModel):
    document_id: UUID


class ConversationResponse(BaseModel):
    id: UUID
    document_id: UUID
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Message Schemas ─────────────────────────────────────

class MessageCreate(BaseModel):
    content: str
    level: Optional[str] = "intermediate"  # beginner, intermediate, expert
    language: Optional[str] = "english"


class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    sources: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
