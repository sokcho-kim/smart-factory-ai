# SHARED_CONTEXT: PunchLine

> 생성일: 2026-05-13
> 기능: AI 비전 기반 품질 자동 기록 및 불량 원인 추적 시스템
> 팀: Fist99 (소지민, 원정환)

---

## API Contract

| Method | Path | Request | Response | Owner |
|--------|------|---------|----------|-------|
| POST | `/inspect` | `multipart/form-data` (image) | `InspectionResult` | 정환 |
| GET | `/inspect/stream` | WebSocket | `InspectionResult[]` (실시간) | 정환 |
| GET | `/quality/timeline?line_id=A&hours=24` | query params | `TimelineData` | 지민 |
| POST | `/quality/root-cause` | `RootCauseRequest` | `RootCauseResult` | 지민 |
| GET | `/quality/report?date=2026-05-22` | query params | `QualityReport` | 지민 |
| GET | `/health` | - | `{ status: "ok" }` | 공통 |

---

## Shared Types

```typescript
// === 검사 결과 (정환 → 지민, 정환 → Dashboard) ===

type Verdict = "ok" | "defect";

type DefectType =
  | "crack"       // 크랙
  | "inclusion"   // 개재물
  | "pitting"     // 피팅
  | "scratch"     // 스크래치
  | "patch"       // 패치
  | "rolled_scale" // 압연 스케일
  | null;         // verdict가 ok이면 null

interface BBox {
  x: number;
  y: number;
  w: number;
  h: number;
}

interface InspectionResult {
  id: string;                    // UUID
  inspected_at: string;          // ISO 8601
  line_id: string;               // "A" | "B" | "C"
  image_path: string;            // 원본 이미지 경로
  verdict: Verdict;
  defect_type: DefectType;
  confidence: number;            // 0~1
  bbox: BBox | null;
}

// === 시계열 추적 (지민 → Dashboard) ===

interface TimelineEntry {
  timestamp: string;             // 15분 단위 집계
  line_id: string;
  total: number;
  defects: number;
  defect_rate: number;           // 0~1
  top_defect_type: DefectType;
}

interface TimelineData {
  entries: TimelineEntry[];
  summary: {
    total_inspected: number;
    total_defects: number;
    overall_defect_rate: number;
  };
}

// === 원인 분석 (지민 → Dashboard) ===

interface RootCauseRequest {
  line_id: string;
  time_start: string;            // ISO 8601
  time_end: string;
}

interface CauseVariable {
  name: string;                  // "mold_temp" | "injection_pressure" | ...
  display_name: string;          // "금형 온도"
  shap_value: number;            // SHAP 기여도
  current_value: number;
  normal_range: [number, number];
  is_abnormal: boolean;
}

interface RootCauseResult {
  analyzed_at: string;
  line_id: string;
  defect_count: number;
  causes: CauseVariable[];       // Top 3~5, SHAP 내림차순
  recommendation: string;        // 조치 가이드 텍스트
  similar_cases: number;         // 과거 유사 사례 수
}

// === 품질 리포트 (지민 → Dashboard) ===

interface QualityReport {
  date: string;
  lines: string[];
  total_inspected: number;
  total_defects: number;
  defect_rate: number;
  defect_breakdown: Record<string, number>; // defect_type별 건수
  hourly_rates: TimelineEntry[];
  top_causes: CauseVariable[];
  actions_taken: string[];
}
```

---

## Environment Variables

| Variable | Required By | Description | Default |
|----------|------------|-------------|---------|
| `DATABASE_URL` | AI Server | PostgreSQL 연결 | `postgresql://punchline:punchline123@db:5432/punchline` |
| `NEXT_PUBLIC_AI_API_URL` | Dashboard | AI 서버 주소 | `http://localhost:8000` |
| `YOLO_MODEL_PATH` | AI Server (정환) | YOLO 가중치 경로 | `models/yolo_v8n_defect.pt` |
| `SHAP_MODEL_PATH` | AI Server (지민) | SHAP 분석용 모델 경로 | `models/lgbm_secom.pkl` |

---

## Integration Points

| From | To | Type | Description |
|------|-----|------|-------------|
| 정환 Vision Engine | PostgreSQL | INSERT | 검사 결과 자동 적재 (inspection_results 테이블) |
| 정환 Vision Engine | Dashboard (WebSocket) | PUSH | 실시간 검사 결과 스트림 |
| 지민 SHAP Pipeline | PostgreSQL | SELECT+INSERT | 공정 파라미터 조회 → 분석 결과 저장 |
| Dashboard | AI Server | REST API | 시계열 조회, 원인 분석 요청, 리포트 생성 |

### 데이터 흐름

```
[웹캠] → 정환 YOLO → InspectionResult → PostgreSQL
                                          ↓
                   지민 SHAP ← process_params 테이블 JOIN (timestamp 기준)
                        ↓
                  RootCauseResult → PostgreSQL
                                          ↓
               Dashboard ← REST API (timeline, root-cause, report)
```

---

## Team Progress

| Team | Member | Status | Current Task | Last Update |
|------|--------|--------|-------------|-------------|
| AI-VISION | 원정환 | 대기 | 데이터셋 다운로드 (Casting, NEU) | 2026-05-13 |
| AI-DATA | 소지민 | Phase 0 완료 | SECOM EDA 완료, DB 스키마, Next.js 뼈대 | 2026-05-13 |

---

## 브랜치 전략 (git-convention)

```
main ← 릴리즈 (본선 당일 최종본)
  └── dev ← 통합 브랜치
       ├── feature/vision-inspect     ← 정환: YOLO 검사 파이프라인
       ├── feature/vision-classify    ← 정환: 결함 유형 분류
       ├── feature/dashboard-ui       ← 정환: Next.js 대시보드
       ├── feature/shap-pipeline      ← 지민: SHAP 인과 분석
       ├── feature/timeline-api       ← 지민: 시계열 추적 API
       └── feature/root-cause-api     ← 지민: 원인 분석 API
```

### 커밋 컨벤션

```
feat(vision): YOLO v8n 이진분류 모델 학습 완료
feat(shap): SECOM 기반 인과 분석 파이프라인
feat(dashboard): 실시간 검사 탭 구현
fix(api): inspect 엔드포인트 타임스탬프 UTC 보정
docs(shared): API Contract 업데이트
```

---

## 파일 소유권

```
src/ai/
  ├── server.py              ← 공통 (엔드포인트 등록)
  ├── vision/                ← 정환 전담
  │   ├── inspector.py       ← YOLO 추론
  │   ├── classifier.py      ← 유형 분류
  │   └── stream.py          ← 이미지 스트림 처리
  └── analysis/              ← 지민 전담
      ├── shap_analyzer.py   ← SHAP 인과 분석
      ├── timeline.py        ← 시계열 집계
      └── report.py          ← 품질 리포트 생성

src/platform/dashboard/src/
  ├── app/page.tsx           ← 공통
  ├── components/
  │   ├── inspection/        ← 정환 전담 (실시간 검사 뷰)
  │   ├── timeline/          ← 지민 전담 (시계열 차트)
  │   └── root-cause/        ← 지민 전담 (원인 분석 뷰)
  └── lib/
      └── types.ts           ← 공통 (Shared Types 반영)

models/                      ← .gitignore, 각자 로컬 관리
  ├── yolo_v8n_defect.pt     ← 정환
  └── lgbm_secom.pkl         ← 지민
```
