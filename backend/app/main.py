import html
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

import markdown as md
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine, get_db
from .models import Document, DocumentShare, User
from .schemas import (
    DocumentCreate,
    DocumentList,
    DocumentOut,
    DocumentSummary,
    DocumentUpdate,
    ShareRequest,
    UserOut,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ajaia-docs")

ALLOWED_UPLOAD_TYPES = {".txt", ".md"}
MAX_UPLOAD_BYTES = 1_000_000  # 1 MB

SEED_USERS = [
    ("Alice Owner", "alice@ajaia.test"),
    ("Bob Reviewer", "bob@ajaia.test"),
    ("Carol Editor", "carol@ajaia.test"),
]




def init_db() -> None:
    """Create tables and seed demo users (mocked auth, see README)."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for name, email in SEED_USERS:
            if not db.scalar(select(User).where(User.email == email)):
                db.add(User(name=name, email=email))
        db.commit()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Ajaia Docs API", lifespan=lifespan)

origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Mocked authentication ----------
# The frontend sends the selected demo user's id in the X-User-Id header.
# This is intentionally simple: real auth (passwords/OAuth/JWT) is out of scope.
def current_user(
    x_user_id: int | None = Header(default=None), db: Session = Depends(get_db)
) -> User:
    if x_user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Select a user first")
    user = db.get(User, x_user_id)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unknown user")
    return user


# ---------- Access rules (the core of the sharing model) ----------
def can_access(doc: Document, user: User) -> bool:
    return doc.owner_id == user.id or any(s.user_id == user.id for s in doc.shares)


def get_accessible_doc(doc_id: int, user: User, db: Session) -> Document:
    doc = db.get(Document, doc_id)
    # Return 404 (not 403) for documents the user can't see, so we don't reveal they exist.
    if not doc or not can_access(doc, user):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    return doc


def to_out(doc: Document, user: User) -> DocumentOut:
    return DocumentOut(
        id=doc.id,
        title=doc.title,
        content=doc.content,
        owner=UserOut.model_validate(doc.owner),
        updated_at=doc.updated_at,
        is_owner=doc.owner_id == user.id,
        shared_with=[UserOut.model_validate(s.user) for s in doc.shares],
    )


# ---------- Endpoints ----------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.scalars(select(User).order_by(User.id)).all()


@app.get("/documents", response_model=DocumentList)
def list_documents(user: User = Depends(current_user), db: Session = Depends(get_db)):
    owned = db.scalars(
        select(Document).where(Document.owner_id == user.id).order_by(Document.updated_at.desc())
    ).all()
    shared = db.scalars(
        select(Document)
        .join(DocumentShare, DocumentShare.document_id == Document.id)
        .where(DocumentShare.user_id == user.id)
        .order_by(Document.updated_at.desc())
    ).all()
    return DocumentList(
        owned=[DocumentSummary.model_validate(d) for d in owned],
        shared=[DocumentSummary.model_validate(d) for d in shared],
    )


@app.post("/documents", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def create_document(
    body: DocumentCreate, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    doc = Document(title=body.title, content="", owner_id=user.id)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    log.info("User %s created document %s", user.id, doc.id)
    return to_out(doc, user)


@app.get("/documents/{doc_id}", response_model=DocumentOut)
def get_document(doc_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return to_out(get_accessible_doc(doc_id, user, db), user)


@app.patch("/documents/{doc_id}", response_model=DocumentOut)
def update_document(
    doc_id: int,
    body: DocumentUpdate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    doc = get_accessible_doc(doc_id, user, db)
    if body.title is not None:
        doc.title = body.title
    if body.content is not None:
        doc.content = body.content
    db.commit()
    db.refresh(doc)
    return to_out(doc, user)


@app.post("/documents/{doc_id}/share", response_model=DocumentOut)
def share_document(
    doc_id: int,
    body: ShareRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    doc = get_accessible_doc(doc_id, user, db)
    if doc.owner_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the owner can share this document")
    target = db.scalar(select(User).where(User.email == body.email.lower()))
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No user with that email")
    if target.id == user.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You already own this document")
    if not any(s.user_id == target.id for s in doc.shares):
        doc.shares.append(DocumentShare(user_id=target.id))
        db.commit()
        db.refresh(doc)
        log.info("Document %s shared with user %s", doc.id, target.id)
    return to_out(doc, user)


def file_to_html(filename: str, raw: bytes) -> str:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "File must be UTF-8 text")
    if filename.lower().endswith(".md"):
        return md.markdown(text, extensions=["extra"])
    # Plain text: escape it and keep each paragraph (blank-line separated).
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return "".join(f"<p>{html.escape(p).replace(chr(10), '<br>')}</p>" for p in paragraphs)


@app.post("/documents/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    name = file.filename or "upload.txt"
    ext = Path(name).suffix.lower()
    if ext not in ALLOWED_UPLOAD_TYPES:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Only .txt and .md files are supported"
        )
    raw = await file.read()
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "File is larger than 1 MB")
    doc = Document(
        title=(Path(name).stem or "Imported document")[:200],
        content=file_to_html(name, raw),
        owner_id=user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    log.info("User %s imported %s as document %s", user.id, name, doc.id)
    return to_out(doc, user)
