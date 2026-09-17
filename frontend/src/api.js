import axios from "axios";

const configured = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");
export const API_BASE = configured || "/api";

export const api = axios.create({ baseURL: API_BASE, timeout: 15000 });
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("taskflow_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("taskflow_token");
      localStorage.removeItem("taskflow_user");
    }
    return Promise.reject(error);
  },
);
