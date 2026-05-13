/**
 * PunchLine Shared Types
 * SHARED_CONTEXT_punchline.md 기반, AI Server ↔ Dashboard 공유 타입.
 */

// === 검사 결과 (정환 Vision → DB → Dashboard) ===

export type Verdict = "ok" | "defect";

export type DefectType =
  | "crack"
  | "inclusion"
  | "pitting"
  | "scratch"
  | "patch"
  | "rolled_scale"
  | "bubble"
  | null;

export interface BBox {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface InspectionResult {
  id: string;
  inspected_at: string;
  line_id: string;
  image_path: string;
  verdict: Verdict;
  defect_type: DefectType;
  confidence: number;
  bbox: BBox | null;
}

// === 시계열 추적 (지민 Timeline → Dashboard) ===

export interface TimelineEntry {
  timestamp: string;
  line_id: string;
  total: number;
  defects: number;
  defect_rate: number;
  top_defect_type: DefectType;
  by_type: Record<string, number>;
}

export interface TimelineSummary {
  total_inspected: number;
  total_defects: number;
  overall_defect_rate: number;
  peak_time: string | null;
  peak_defect_rate: number;
  dominant_defect_type: DefectType;
}

export interface AnomalyAlert {
  timestamp: string;
  line_id: string;
  defect_rate: number;
  window_defects: number;
  window_total: number;
  message: string;
}

export interface TimelineData {
  entries: TimelineEntry[];
  summary: TimelineSummary;
  alerts: AnomalyAlert[];
}

// === 원인 분석 (지민 SHAP → Dashboard) ===

export interface CauseVariable {
  name: string;
  display_name: string;
  shap_value: number;
  current_value: number;
  normal_range: [number, number];
  is_abnormal: boolean;
}

export interface RootCauseRequest {
  line_id: string;
  time_start: string;
  time_end: string;
}

export interface RootCauseResult {
  analyzed_at: string;
  line_id: string;
  defect_count: number;
  causes: CauseVariable[];
  recommendation: string;
  similar_cases: number;
}

// === 품질 리포트 ===

export interface QualityReport {
  date: string;
  lines: string[];
  total_inspected: number;
  total_defects: number;
  defect_rate: number;
  defect_breakdown: Record<string, number>;
  hourly_rates: TimelineEntry[];
  top_causes: CauseVariable[];
  actions_taken: string[];
}

// === 공정 파라미터 ===

export interface ProcessParams {
  recorded_at: string;
  line_id: string;
  mold_temp: number;
  injection_pressure: number;
  injection_speed: number;
  cooling_time: number;
  humidity: number;
  ambient_temp: number;
}

// === KPI 대시보드 요약 ===

export interface DashboardKPI {
  total_inspected: number;
  defect_rate: number;
  defect_rate_delta: number;
  top_defect_type: DefectType;
  top_defect_pct: number;
  top_cause_name: string;
  top_cause_shap: number;
  active_alerts: number;
}
