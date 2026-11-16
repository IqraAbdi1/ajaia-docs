const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

let currentUserId = null;
export function setCurrentUser(id) {
  currentUserId = id;
}

async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (currentUserId) headers["X-User-Id"] = String(currentUserId);
  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  let res;
  try {
    res = await fetch(`${API_URL}${path}`, { ...options, headers });
  } catch {
    throw new Error("Can't reach the server. Please try again in a moment.");
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    // FastAPI returns {detail: "..."} or a list of validation errors
    const detail = Array.isArray(data.detail)
      ? data.detail.map((d) => d.msg.replace("Value error, ", "")).join(", ")
      : data.detail;
    throw new Error(detail || `Request failed (${res.status})`);
  }
  return data;
}

export const api = {
  users: () => request("/users"),
  listDocs: () => request("/documents"),
  getDoc: (id) => request(`/documents/${id}`),
  createDoc: (title) => request("/documents", { method: "POST", body: JSON.stringify({ title }) }),
  updateDoc: (id, patch) =>
    request(`/documents/${id}`, { method: "PATCH", body: JSON.stringify(patch) }),
  shareDoc: (id, email) =>
    request(`/documents/${id}/share`, { method: "POST", body: JSON.stringify({ email }) }),
  uploadDoc: (file) => {
    const form = new FormData();
    form.append("file", file);
    return request("/documents/upload", { method: "POST", body: form });
  },
};
