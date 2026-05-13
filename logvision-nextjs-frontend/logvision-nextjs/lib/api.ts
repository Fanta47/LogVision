const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("logvision_token") : null;
  const headers = new Headers(options.headers);
  if (token && !headers.has("Authorization")) headers.set("Authorization", `Bearer ${token}`);
  const res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers, cache: "no-store" });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.json();
}

export type DashboardSummary = {
  total_events: number;
  total_uploads: number;
  total_anomalies: number;
  high_risk_anomalies: number;
  latest_model?: string;
  health_score?: number;
};

export type UploadItem = {
  upload_uid: string;
  original_file_name: string;
  stored_file_name?: string;
  stored_path?: string;
  application_key: string;
  component_name: string;
  status: string;
  uploaded_at?: string;
  total_lines?: number;
  parsed_events?: number;
  failed_events?: number;
};

export type AnomalyItem = {
  sequence_uid: string;
  application_key: string;
  component_name: string;
  start_timestamp: string;
  end_timestamp: string;
  anomaly_score: number;
  anomaly_label: string;
  model_name?: string;
  model_version?: string;
};

export type RecentEvent = {
  id: number;
  event_timestamp: string;
  application_key: string;
  component_name: string;
  log_level?: string;
  log_family?: string;
  event_type?: string;
  details?: string;
};

export async function uploadLogFile(params: { file: File; applicationKey: string; componentName: string; }) {
  const form = new FormData();
  form.append("file", params.file);
  form.append("application_key", params.applicationKey);
  form.append("component_name", params.componentName);
  return request<UploadItem>("/api/logs/upload", { method: "POST", body: form });
}
export const getUploads = () => request<UploadItem[]>("/api/logs/uploads");
export const getDashboardSummary = () => request<DashboardSummary>("/api/dashboard/summary");
export const getRecentEvents = () => request<RecentEvent[]>("/api/dashboard/recent-events");
export const getAnomalies = () => request<AnomalyItem[]>("/api/ml/anomalies");
export const getModelComparison = () => request<any[]>("/api/ml/model-comparison");
export const runMLScoring = () => request<{ status: string; message?: string }>("/api/ml/score", { method: "POST" });
