import { useEffect, useRef, useState } from "react";
import { api } from "./api";

function DocList({ title, docs, onOpen, showOwner, emptyText }) {
  return (
    <section className="doc-section">
      <h3>{title}</h3>
      {docs.length === 0 ? (
        <p className="muted">{emptyText}</p>
      ) : (
        <ul className="doc-list">
          {docs.map((d) => (
            <li key={d.id}>
              <button className="doc-item" onClick={() => onOpen(d.id)}>
                <span className="doc-title">{d.title}</span>
                <span className="muted">
                  {showOwner ? `Owner: ${d.owner.name} · ` : ""}
                  Updated {new Date(d.updated_at).toLocaleString()}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default function Dashboard({ user, onOpen }) {
  const [docs, setDocs] = useState({ owned: [], shared: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const fileInput = useRef(null);

  useEffect(() => {
    api
      .listDocs()
      .then(setDocs)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  async function createDoc() {
    try {
      const doc = await api.createDoc("Untitled document");
      onOpen(doc.id);
    } catch (e) {
      setError(e.message);
    }
  }

  async function uploadFile(e) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    setError("");
    try {
      const doc = await api.uploadDoc(file);
      onOpen(doc.id);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <div className="dash-header">
        <h2>Hi, {user.name.split(" ")[0]}</h2>
        <div className="actions">
          <button className="primary" onClick={createDoc}>
            + New document
          </button>
          <button onClick={() => fileInput.current?.click()}>⬆ Import file</button>
          <input
            ref={fileInput}
            type="file"
            accept=".txt,.md"
            hidden
            onChange={uploadFile}
          />
        </div>
      </div>
      <p className="muted small">Import supports .txt and .md files (max 1 MB). Each file becomes a new editable document.</p>
      {error && <p className="error">{error}</p>}
      {loading ? (
        <p className="muted">Loading documents…</p>
      ) : (
        <>
          <DocList
            title="My documents"
            docs={docs.owned}
            onOpen={onOpen}
            emptyText="No documents yet. Create one or import a file."
          />
          <DocList
            title="Shared with me"
            docs={docs.shared}
            onOpen={onOpen}
            showOwner
            emptyText="Nothing has been shared with you yet."
          />
        </>
      )}
    </div>
  );
}
