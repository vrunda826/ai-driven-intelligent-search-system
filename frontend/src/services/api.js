import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:3001/api",
  timeout: 10000,
});

export async function login(credentials) {
  const response = await api.post("/auth/login", credentials);
  return response.data;
}

export async function getDashboardData() {
  const response = await api.get("/dashboard");
  return response.data;
}

export async function getUploads() {
  const response = await api.get("/uploads");
  return response.data;
}

export async function createUpload(payload) {
  const response = await api.post("/uploads", payload);
  return response.data;
}
