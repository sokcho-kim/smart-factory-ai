# 02. 지민 파트와의 결합 지점

PunchLine은 정환의 **Vision Engine**과 지민의 **Data Intelligence**가 시간 기반으로 조인되어야 하나의 시스템이 된다. 결합이 어긋나면 "감지는 되지만 원인 추적은 안 됨" 같은 반쪽짜리 데모가 된다.

## 핵심 결합 지점 5가지

### ① 타임스탬프 정합 — 가장 중요

지민의 인과 분석은 **"불량이 발생한 그 시각에 어떤 공정 조건이었나"** 를 매칭한다. 따라서:

- 추론 결과의 타임스탬프는 **UTC ISO8601** 단일 포맷 (`2026-05-22T09:42:13.456Z`)
- 추론이 일어난 시각이 아니라 **이미지가 촬영된 시각** 기준 (지연 보정)
- 밀리초까지 기록 (공정 데이터가 초 단위로 변할 수 있음)
- 시뮬레이션에서도 "재생 시각 = 가상 라인 시각" 로 통일

> 정환이 0.5초만 어긋나게 기록해도 지민의 매칭이 깨진다. 이게 첫 번째 통합 리스크.

### ② JSON 인터페이스 (Phase 1 단계에서 미리 합의)

`POST /inspect` 응답 스키마 — **지민이 이 스키마를 그대로 받아서 DB에 적재한다**.

```json
{
  "inspection_id": "uuid-v4",
  "captured_at": "2026-05-22T09:42:13.456Z",
  "line_id": "A",
  "image_path": "data/sample/img_002847.jpg",
  "verdict": "DEFECT",                 // OK | DEFECT
  "defect_types": [                    // 다중 결함 가능
    {
      "type": "crack",                 // 표준 라벨 — 지민 RAG 키로 사용
      "confidence": 0.942,
      "bbox": [x1, y1, x2, y2],        // YOLO 출력
      "area_ratio": 0.034              // 결함 영역 / 전체 이미지
    }
  ],
  "anomaly_score": 0.87,               // PatchCore 점수 (0~1)
  "model_versions": {
    "yolo": "v8n-casting-neu-v2",
    "patchcore": "mvtec-bottle-v1"
  }
}
```

**라벨 표준화 (정환이 결정해서 지민에게 통보해야 함)**

```python
DEFECT_LABELS = {
    "crack",           # 크랙
    "porosity",        # 기공
    "scratches",       # 긁힘
    "patches",         # 패임/얼룩
    "rolled_in_scale", # 압연 스케일
    "inclusion",       # 이물질
    "deformation",     # 변형
    "other"            # 기타
}
```

지민의 조치 가이드 RAG 키가 이 라벨 셋에 일대일 대응해야 한다.

### ③ DB 스키마 협의

지민이 PostgreSQL 스키마를 설계하는데, 정환의 출력이 들어갈 `inspection_results` 테이블 컬럼은:

```sql
CREATE TABLE inspection_results (
    inspection_id   UUID PRIMARY KEY,
    captured_at     TIMESTAMPTZ NOT NULL,
    line_id         VARCHAR(8) NOT NULL,
    image_path      TEXT NOT NULL,
    verdict         VARCHAR(8) NOT NULL,    -- 'OK' or 'DEFECT'
    defect_types    JSONB,                  -- 위 JSON 그대로
    anomaly_score   REAL,
    yolo_version    VARCHAR(32),
    patchcore_version VARCHAR(32)
);

CREATE INDEX idx_captured_at ON inspection_results (captured_at);
CREATE INDEX idx_verdict ON inspection_results (verdict);
```

→ `captured_at` 인덱스가 지민의 시계열 조인 성능을 결정한다. 정환이 API 만들 때 이 컬럼만은 정확히.

### ④ 시연 시나리오 — 양품→불량 급증→복귀 시퀀스

지민의 SHAP 분석이 "그림" 으로 보이려면 **시계열에 패턴이 필요**하다. 정환이 만드는 시연 이미지 시퀀스:

```
00:00~02:00  양품 50장 (불량률 2%)
02:00~04:00  불량 급증 30장 (크랙 위주, 불량률 40%)
04:00~06:00  양품 50장 복귀 (불량률 2%)
```

이걸 만들 때 정환은 지민에게 **시뮬레이션 공정 데이터(온도/압력/속도)도 같은 시각 패턴으로 만들 것**을 요청해야 한다:
- 02:00~04:00 구간만 금형 온도 85~90°C (정상 70~80°C)
- 나머지 구간은 정상

이렇게 합쳐야 SHAP이 "온도 = 크랙의 주 원인" 을 제대로 찾는다.

### ⑤ Streamlit 대시보드 화면 분담

| 패널 | 담당 | 데이터 소스 |
|------|------|-------------|
| 좌상: 실시간 검사 화면 (이미지 + bbox) | 정환 | `/inspect` 응답 |
| 우상: 시계열 불량률 차트 | 정환 | DB 시간대별 집계 |
| 좌하: SHAP 원인 변수 Top3 | 지민 | 지민 분석 API |
| 우하: 조치 가이드 패널 | 지민 | 지민 RAG |

→ 정환이 화면 골격 + 좌상/우상 만들고, 지민이 좌하/우하 컴포넌트를 PR로 추가하는 구조. **Streamlit 컴포넌트가 서로 상태를 안 흔들도록 `st.session_state` 키 네임스페이스만 분리** (`vision_*`, `intel_*`).

## 정환이 지민에게 미리 줘야 할 것 (D-5까지)

| 시기 | 산출물 | 형태 |
|------|--------|------|
| 5/17까지 | `defect_labels.json` (라벨 표준) | 파일 |
| 5/17까지 | `/inspect` 응답 JSON 스키마 명세 | Markdown |
| 5/18까지 | Mock 추론 결과 100건 (CSV/JSON) — 지민 파이프라인 테스트용 | 파일 |
| 5/20까지 | 시연 이미지 시퀀스 + 각 이미지 메타 (시각, 라인) | ZIP + manifest |
| 5/20까지 | 실 API endpoint 작동 (`http://localhost:8000/inspect`) | 서버 |

## 통합 리스크 체크리스트

- [ ] 타임스탬프 포맷이 양쪽 모두 UTC ISO8601 인가
- [ ] 결함 라벨 셋이 양쪽이 같은가
- [ ] DB 스키마가 지민의 분석 쿼리에 맞는가 (인덱스 포함)
- [ ] Streamlit `session_state` 키 충돌이 없는가
- [ ] Docker Compose에서 양쪽 서비스가 동시 기동되는가
- [ ] 본선 데모 데이터의 비전 시퀀스 vs 공정 시뮬 데이터가 시각적으로 합치되는가
