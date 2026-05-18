import type { DefectType } from "./types";

/** 불량률 상태 임계값 (ISA-101 신호등) */
export const DEFECT_RATE_THRESHOLDS = {
  green: 0.03, // < 3% 정상
  yellow: 0.08, // 3~8% 주의
  // >= 8% 위험
} as const;

export type StatusLevel = "green" | "yellow" | "red";

export function getStatusLevel(defectRate: number): StatusLevel {
  if (defectRate < DEFECT_RATE_THRESHOLDS.green) return "green";
  if (defectRate < DEFECT_RATE_THRESHOLDS.yellow) return "yellow";
  return "red";
}

/** SPC 관리 상한선 (서버 alert_threshold과 동일) */
export const UCL = 0.1;

/** 불량 유형 한글 레이블 */
export const DEFECT_TYPE_LABELS: Record<string, string> = {
  crack: "크랙",
  inclusion: "개재물",
  pitting: "피팅",
  scratch: "스크래치",
  patch: "패치",
  rolled_scale: "압연 스케일",
  bubble: "버블",
};

export function getDefectLabel(type: DefectType | string | null): string {
  if (!type) return "-";
  return DEFECT_TYPE_LABELS[type] ?? type;
}

/** 숫자 포맷 */
export function fmtPct(v: number): string {
  return `${(v * 100).toFixed(1)}%`;
}

export function fmtNum(v: number): string {
  return v.toLocaleString("ko-KR");
}

export function fmtTime(iso: string): string {
  return new Date(iso).toLocaleTimeString("ko-KR", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

export function fmtTimeShort(iso: string): string {
  return new Date(iso).toLocaleTimeString("ko-KR", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}
