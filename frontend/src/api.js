import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api"
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("vc_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// FastAPI error responses come in two shapes: a plain string detail (e.g.
// HTTPException(detail="Email already registered")) or, for validation
// errors (422), an array of objects like {type, loc, msg, ...}. Rendering
// that array directly as JSX crashes the page, so this always returns a
// plain string either way.
export function extractError(e, fallback = "Something went wrong") {
  const detail = e?.response?.data?.detail;
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map(d => (typeof d === "string" ? d : d.msg || JSON.stringify(d)))
      .join(" ");
  }
  return fallback;
}

// Certificates come back as a PDF file rather than JSON, so they're
// downloaded as a blob and handed to the browser as a normal file save.
export async function downloadCertificate(applicationId, fileName) {
  const response = await api.get(`/applications/${applicationId}/certificate`, {
    responseType: "blob"
  });
  const url = window.URL.createObjectURL(new Blob([response.data], { type: "application/pdf" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = `${fileName || "certificate"}.pdf`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export default api;