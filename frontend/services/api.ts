import axios from "axios";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 120000, // 2 minutes for agent inference and code generation
});

// Response interceptor for clear debugging
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      "Unknown API Error";
    console.error(`[API Error] ${error.config?.url}:`, message);
    return Promise.reject(error);
  }
);
