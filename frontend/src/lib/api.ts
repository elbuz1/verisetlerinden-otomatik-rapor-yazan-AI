import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Sadece /auth/me veya korumalı endpointlerde 401 alırsa çıkış yap
    // Login/register sırasındaki 401'leri yoksay (onlar zaten formdaki hata olarak gösterilir)
    const url = error.config?.url || "";
    const isAuthEndpoint = url.includes("/auth/login") || url.includes("/auth/register");

    if (
      error.response?.status === 401 &&
      typeof window !== "undefined" &&
      !isAuthEndpoint &&
      url.includes("/auth/me")
    ) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/";
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data: { email: string; username: string; password: string; full_name: string }) =>
    api.post("/auth/register", data),
  login: (data: { username: string; password: string }) => {
    const formData = new URLSearchParams();
    formData.append("username", data.username);
    formData.append("password", data.password);
    return api.post("/auth/login", formData, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },
  me: () => api.get("/auth/me"),
};

export const uploadAPI = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/upload/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });
  },
  list: () => api.get("/upload/datasets"),
  get: (id: number) => api.get(`/upload/datasets/${id}`),
};

export const analysisAPI = {
  run: (datasetId: number) => api.post(`/analysis/${datasetId}`),
  get: (datasetId: number) => api.get(`/analysis/${datasetId}`),
};

export const reportAPI = {
  generate: (datasetId: number, format: string = "pdf") =>
    api.post(`/reports/generate/${datasetId}?format=${format}`),
  list: () => api.get("/reports/"),
  download: (reportId: number) =>
    api.get(`/reports/download/${reportId}`, { responseType: "blob" }),
};

export const dashboardAPI = {
  stats: () => api.get("/dashboard/stats"),
  recentDatasets: () => api.get("/dashboard/recent-datasets"),
  recentReports: () => api.get("/dashboard/recent-reports"),
  workflows: () => api.get("/dashboard/workflows"),
  workflowStatus: (datasetId: number) => api.get(`/dashboard/workflow-status/${datasetId}`),
};

export default api;
