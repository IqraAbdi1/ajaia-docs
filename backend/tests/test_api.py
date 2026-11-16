import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app, init_db

ALICE, BOB, CAROL = {"X-User-Id": "1"}, {"X-User-Id": "2"}, {"X-User-Id": "3"}


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    init_db()
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


def test_sharing_controls_access(client):
    # Alice creates a document with formatted content
    doc = client.post("/documents", json={"title": "Plan"}, headers=ALICE).json()
    client.patch(f"/documents/{doc['id']}", json={"content": "<p><strong>Hi</strong></p>"}, headers=ALICE)

    # Bob cannot see it before it is shared
    assert client.get(f"/documents/{doc['id']}", headers=BOB).status_code == 404

    # Bob cannot share a document he does not own
    r = client.post(f"/documents/{doc['id']}/share", json={"email": "carol@ajaia.test"}, headers=BOB)
    assert r.status_code == 404

    # Alice shares with Bob
    r = client.post(f"/documents/{doc['id']}/share", json={"email": "bob@ajaia.test"}, headers=ALICE)
    assert r.status_code == 200

    # Bob now sees it under "shared", with formatting preserved, and is not the owner
    lists = client.get("/documents", headers=BOB).json()
    assert [d["id"] for d in lists["shared"]] == [doc["id"]]
    assert lists["owned"] == []
    opened = client.get(f"/documents/{doc['id']}", headers=BOB).json()
    assert opened["content"] == "<p><strong>Hi</strong></p>"
    assert opened["is_owner"] is False

    # Carol still cannot access it
    assert client.get(f"/documents/{doc['id']}", headers=CAROL).status_code == 404


def test_upload_markdown_creates_document(client):
    r = client.post(
        "/documents/upload",
        files={"file": ("notes.md", b"# Title\n\n- one\n- two", "text/markdown")},
        headers=ALICE,
    )
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "notes"
    assert "<h1>Title</h1>" in body["content"] and "<li>one</li>" in body["content"]


def test_upload_rejects_unsupported_type(client):
    r = client.post(
        "/documents/upload",
        files={"file": ("photo.png", b"\x89PNG", "image/png")},
        headers=ALICE,
    )
    assert r.status_code == 400


def test_requires_user_and_valid_title(client):
    assert client.get("/documents").status_code == 401
    assert client.post("/documents", json={"title": "   "}, headers=ALICE).status_code == 422
