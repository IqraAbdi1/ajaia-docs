import { useEffect, useState } from "react";
import { api, setCurrentUser } from "./api";
import Dashboard from "./Dashboard";
import EditorPage from "./EditorPage";

export default function App() {
  const [users, setUsers] = useState([]);
  const [userId, setUserId] = useState(() => Number(localStorage.getItem("userId")) || null);
  const [openDocId, setOpenDocId] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.users().then(setUsers).catch((e) => setError(e.message));
  }, []);

  setCurrentUser(userId);

  function switchUser(id) {
    const value = Number(id) || null;
    localStorage.setItem("userId", value ?? "");
    setCurrentUser(value);
    setUserId(value);
    setOpenDocId(null);
  }

  const user = users.find((u) => u.id === userId);

  return (
    <div className="app">
      <header className="topbar">
        <button className="brand" onClick={() => setOpenDocId(null)}>
          📝 Ajaia Docs
        </button>
        <label className="user-picker">
          Signed in as{" "}
          <select value={userId ?? ""} onChange={(e) => switchUser(e.target.value)}>
            <option value="">Choose a demo user…</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>
                {u.name} ({u.email})
              </option>
            ))}
          </select>
        </label>
      </header>

      <main className="content">
        {error && <p className="error">{error}</p>}
        {!user ? (
          <div className="empty">
            <h2>Welcome to Ajaia Docs</h2>
            <p>Choose a demo user at the top right to start. Switch users to test sharing.</p>
          </div>
        ) : openDocId ? (
          <EditorPage key={openDocId} docId={openDocId} onBack={() => setOpenDocId(null)} />
        ) : (
          <Dashboard key={userId} user={user} onOpen={setOpenDocId} />
        )}
      </main>
    </div>
  );
}
