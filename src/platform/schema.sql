-- PunchLine DB Schema
-- 검사 결과, 공정 파라미터, 불량 이력을 자동 기록하는 구조

-- 1. 검사 결과 (비전 AI 출력)
CREATE TABLE IF NOT EXISTS inspection_results (
    id              SERIAL PRIMARY KEY,
    inspected_at    TIMESTAMP NOT NULL DEFAULT NOW(),  -- 검사 시각 (자동 타임스탬프)
    line_id         VARCHAR(20) NOT NULL,              -- 라인 ID (A, B, C...)
    image_path      TEXT,                              -- 원본 이미지 경로
    verdict         VARCHAR(10) NOT NULL,              -- 'ok' | 'defect'
    defect_type     VARCHAR(30),                       -- 'crack' | 'bubble' | 'scratch' | 'foreign' | NULL
    confidence      FLOAT,                             -- 모델 신뢰도 (0~1)
    bbox_x          INT,                               -- 결함 바운딩박스 x
    bbox_y          INT,
    bbox_w          INT,
    bbox_h          INT
);

CREATE INDEX idx_inspection_at ON inspection_results(inspected_at);
CREATE INDEX idx_inspection_line ON inspection_results(line_id);
CREATE INDEX idx_inspection_verdict ON inspection_results(verdict);

-- 2. 공정 파라미터 (센서/PLC 데이터)
CREATE TABLE IF NOT EXISTS process_params (
    id              SERIAL PRIMARY KEY,
    recorded_at     TIMESTAMP NOT NULL DEFAULT NOW(),  -- 센서 기록 시각
    line_id         VARCHAR(20) NOT NULL,
    mold_temp       FLOAT,     -- 금형 온도 (°C)
    injection_pressure FLOAT,  -- 사출 압력 (MPa)
    injection_speed FLOAT,     -- 사출 속도 (mm/s)
    cooling_time    FLOAT,     -- 냉각 시간 (s)
    humidity        FLOAT,     -- 습도 (%)
    ambient_temp    FLOAT      -- 주변 온도 (°C)
);

CREATE INDEX idx_process_at ON process_params(recorded_at);
CREATE INDEX idx_process_line ON process_params(line_id);

-- 3. 원인 분석 결과
CREATE TABLE IF NOT EXISTS root_cause_analysis (
    id              SERIAL PRIMARY KEY,
    analyzed_at     TIMESTAMP NOT NULL DEFAULT NOW(),
    line_id         VARCHAR(20) NOT NULL,
    time_window_start TIMESTAMP NOT NULL,   -- 분석 구간 시작
    time_window_end   TIMESTAMP NOT NULL,   -- 분석 구간 끝
    defect_count    INT NOT NULL,            -- 구간 내 불량 수
    top_cause_1     VARCHAR(30),             -- 원인 변수 1위
    top_cause_1_shap FLOAT,                  -- SHAP 기여도
    top_cause_2     VARCHAR(30),
    top_cause_2_shap FLOAT,
    top_cause_3     VARCHAR(30),
    top_cause_3_shap FLOAT,
    recommendation  TEXT                     -- 조치 가이드
);

-- 4. 조치 이력
CREATE TABLE IF NOT EXISTS action_log (
    id              SERIAL PRIMARY KEY,
    action_at       TIMESTAMP NOT NULL DEFAULT NOW(),
    line_id         VARCHAR(20) NOT NULL,
    rca_id          INT REFERENCES root_cause_analysis(id),
    action_taken    TEXT NOT NULL,            -- 수행한 조치
    result          VARCHAR(20),             -- 'resolved' | 'pending' | 'escalated'
    defect_rate_before FLOAT,                -- 조치 전 불량률
    defect_rate_after  FLOAT                 -- 조치 후 불량률
);
