import type {
  DashboardKPI,
  TimelineData,
  RootCauseRequest,
  RootCauseResult,
  Verdict,
  DefectType,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_AI_API_URL ?? "http://localhost:8000";

/** /inspect/stream 실제 응답 형태 (CSV 기반, id/image_path/bbox 없음) */
export interface InspectionRecord {
  inspected_at: string;
  line_id: string;
  verdict: Verdict;
  defect_type: DefectType;
  confidence: number;
}

export interface InspectStreamResponse {
  offset: number;
  limit: number;
  total: number;
  results: InspectionRecord[];
}

export interface HourlyEntry {
  hour: number;
  total: number;
  defects: number;
  defect_rate: number;
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

export const fetchKPI = (lineId = "A") =>
  get<DashboardKPI>(`/quality/kpi?line_id=${lineId}`);

export const fetchTimeline = (lineId = "A", freq = "15min") =>
  get<TimelineData>(`/quality/timeline?line_id=${lineId}&freq=${freq}`);

export const fetchHourly = (lineId = "A") =>
  get<HourlyEntry[]>(`/quality/hourly?line_id=${lineId}`);

export const fetchInspectStream = (offset = 0, limit = 60) =>
  get<InspectStreamResponse>(`/inspect/stream?offset=${offset}&limit=${limit}`);

export const postRootCause = (req: RootCauseRequest) =>
  post<RootCauseResult>("/quality/root-cause", req);

export const fetchHealth = () =>
  get<{ status: string }>("/health");
