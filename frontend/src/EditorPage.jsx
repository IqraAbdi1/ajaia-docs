import { useEffect, useState } from "react";
import { EditorContent, useEditor, useEditorState } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import { api } from "./api";

function Toolbar({ editor }) {
  const state = useEditorState({
    editor,
    selector: ({ editor: e }) => ({
      bold: e.isActive("bold"),
      italic: e.isActive("italic"),
      underline: e.isActive("underline"),
      h1: e.isActive("heading", { level: 1 }),
      h2: e.isActive("heading", { level: 2 }),
      bullet: e.isActive("bulletList"),
      ordered: e.isActive("orderedList"),
    }),
  });
  const btn = (label, active, action, title) => (
    <button
      type="button"
      title={title}
      className={active ? "tool active" : "tool"}
      onMouseDown={(ev) => ev.preventDefault()}
      onClick={action}
    >
      {label}
    </button>
  );
  const chain = () => editor.chain().focus();
  return (
    <div className="toolbar">
      {btn(<b>B</b>, state.bold, () => chain().toggleBold().run(), "Bold (Ctrl+B)")}
      {btn(<i>I</i>, state.italic, () => chain().toggleItalic().run(), "Italic (Ctrl+I)")}
      {btn(<u>U</u>, state.underline, () => chain().toggleUnderline().run(), "Underline (Ctrl+U)")}
      <span className="sep" />
      {btn("H1", state.h1, () => chain().toggleHeading({ level: 1 }).run(), "Heading 1")}
      {btn("H2", state.h2, () => chain().toggleHeading({ level: 2 }).run(), "Heading 2")}
      <span className="sep" />
      {btn("• List", state.bullet, () => chain().toggleBulletList().run(), "Bulleted list")}
      {btn("1. List", state.ordered, () => chain().toggleOrderedList().run(), "Numbered list")}
    </div>
  );
}

function SharePanel({ doc, onShared }) {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function share(e) {
    e.preventDefault();
    setError("");
    setMessage("");
    try {
      const updated = await api.shareDoc(doc.id, email);
      setMessage(`Shared with ${email}`);
      setEmail("");
      onShared(updated);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <aside className="share-panel">
      <h4>Sharing</h4>
      <p className="muted small">Owner: {doc.owner.name}</p>
      {doc.shared_with.length > 0 ? (
        <ul className="share-list">
          {doc.shared_with.map((u) => (
            <li key={u.id}>👤 {u.name}</li>
          ))}
        </ul>
      ) : (
        <p className="muted small">Not shared yet.</p>
      )}
      {doc.is_owner ? (
        <form onSubmit={share} className="share-form">
          <input
            type="email"
            placeholder="bob@ajaia.test"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <button type="submit">Share</button>
        </form>
      ) : (
        <p className="badge">Shared with you by {doc.owner.name}</p>
      )}
      {message && <p className="success small">{message}</p>}
      {error && <p className="error small">{error}</p>}
    </aside>
  );
}

export default function EditorPage({ docId, onBack }) {
  const [doc, setDoc] = useState(null);
  const [title, setTitle] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [dirty, setDirty] = useState(false);

  const editor = useEditor({
    extensions: [StarterKit.configure({ link: false })],
    content: "",
    onUpdate: () => setDirty(true),
  });

  useEffect(() => {
    api
      .getDoc(docId)
      .then((d) => {
        setDoc(d);
        setTitle(d.title);
      })
      .catch((e) => setError(e.message));
  }, [docId]);

  useEffect(() => {
    if (editor && doc && !dirty) editor.commands.setContent(doc.content || "", { emitUpdate: false });
    // only load content once per document
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [editor, doc?.id]);

  async function save() {
    if (!editor) return;
    setError("");
    setStatus("Saving…");
    try {
      const updated = await api.updateDoc(docId, { title, content: editor.getHTML() });
      setDoc(updated);
      setDirty(false);
      setStatus(`Saved at ${new Date().toLocaleTimeString()}`);
    } catch (e) {
      setStatus("");
      setError(e.message);
    }
  }

  // Ctrl+S / Cmd+S saves
  useEffect(() => {
    const onKey = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
        e.preventDefault();
        save();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  if (error && !doc) {
    return (
      <div>
        <button onClick={onBack}>← Back</button>
        <p className="error">{error}</p>
      </div>
    );
  }
  if (!doc || !editor) return <p className="muted">Loading document…</p>;

  return (
    <div className="editor-layout">
      <div className="editor-main">
        <div className="editor-header">
          <button onClick={onBack}>← Back</button>
          <input
            className="title-input"
            value={title}
            maxLength={200}
            onChange={(e) => {
              setTitle(e.target.value);
              setDirty(true);
            }}
            aria-label="Document title"
          />
          <button className="primary" onClick={save} disabled={!dirty}>
            Save
          </button>
        </div>
        <p className="muted small status">
          {dirty ? "Unsaved changes (Ctrl+S to save)" : status || "All changes saved"}
        </p>
        {error && <p className="error">{error}</p>}
        <Toolbar editor={editor} />
        <div className="page">
          <EditorContent editor={editor} />
        </div>
      </div>
      <SharePanel doc={doc} onShared={setDoc} />
    </div>
  );
}
