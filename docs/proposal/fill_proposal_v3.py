"""기획서 v3 — 시나리오 E: AI 비전 검사 + 불량 원인 추적 플랫폼."""
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor

SRC = "docs/proposal/기획서_v3.pptx"
prs = Presentation(SRC)
slides = list(prs.slides)


def clear_and_write(textbox, lines, font_size=11):
    tf = textbox.text_frame
    tf.clear()
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.size = Pt(font_size)
        p.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
        if line.startswith("\u25a0"):
            p.font.bold = True


def find_content_box(slide):
    for shape in slide.shapes:
        if shape.has_text_frame and "\uc791\uc131\ubc29\ubc95" in shape.text_frame.text:
            return shape
    return None


# ═══ Slide 1: 표지 ═══
for shape in slides[0].shapes:
    if shape.has_table:
        table = shape.table
        table.cell(0, 1).text = "FactoryMind"
        table.cell(1, 1).text = "AI 비전 검사 및 불량 원인 추적 플랫폼"
        for row in table.rows:
            for cell in row.cells:
                for p in cell.text_frame.paragraphs:
                    p.font.size = Pt(12)

# ═══ Slide 2: 문제 정의 ═══
box = find_content_box(slides[1])
if box:
    clear_and_write(box, [
        "■ 핵심 문제: 사람 눈에 의존하는 품질 검사, 그리고 반복되는 불량",
        "",
        "국내 중소 제조업체의 품질 검사는 대부분 작업자의 육안에 의존합니다.",
        "사람은 피로해지고, 기준이 흔들리고, 원인까지 추적할 여력이 없습니다.",
        "",
        "• 문제 1: 육안 검사의 불량 탐지율은 평균 70~80%",
        "  → 제품 100개 중 20~30개의 불량이 고객에게 유출",
        "  → 클레임 비용 + 신뢰도 하락 = 연간 수천만원 손실",
        "",
        "• 문제 2: 불량이 발견되어도 '왜 발생했는지' 모른다",
        "  → 같은 불량이 반복 발생 (크랙, 기포, 스크래치)",
        "  → 공정 조건(온도, 압력, 속도)과의 연결 분석이 수작업 또는 미실시",
        "",
        "• 문제 3: 숙련 검사원 은퇴 시 품질 노하우가 사라진다",
        "  → 신입 검사원의 숙련까지 6개월~1년 소요",
        "  → 검사 기준의 암묵지화 → 일관성 없는 판정",
        "",
        "■ 핵심 KPI",
        "• 불량 탐지율: 70~80% → 95% 이상 (AI 자동 검사)",
        "• 불량 원인 추적: 수작업 분석(수일) → 실시간 자동 추적",
        "• 반복 불량률: 동일 유형 재발 50% 감소 (원인 기반 조치)",
    ], font_size=10)

# ═══ Slide 3: 솔루션 개요 ═══
box = find_content_box(slides[2])
if box:
    clear_and_write(box, [
        "■ FactoryMind — 불량을 잡고, 원인까지 알려주는 AI 품질 플랫폼",
        "",
        "라인 카메라로 제품 외관을 자동 검사하고,",
        "불량이 발생하면 그 시점의 공정 조건을 분석하여 원인을 추적하고,",
        "조치 가이드까지 제공하는 통합 품질 관리 플랫폼입니다.",
        "",
        "■ 핵심 아이디어: 3단계 품질 지능화",
        "",
        "① DETECT — 불량을 잡는다",
        "   YOLO + Anomaly Detection으로 외관 결함 자동 탐지",
        "   양품 이미지를 학습하여, 제품 도면(CAD) 없이도 동작",
        "",
        "② TRACE — 원인을 추적한다",
        "   불량 발생 시점의 공정 파라미터(온도/압력/속도)를 자동 조회",
        "   상관 분석 + 설명 가능 AI(SHAP)로 핵심 원인 변수 특정",
        "",
        "③ GUIDE — 조치를 안내한다",
        "   불량 유형별 조치 가이드를 RAG로 검색하여 제공",
        '   "금형 온도 87°C → 80°C 이하로 조정 권장 (유사 사례 3건)"',
        "",
        "■ 차별점",
        "기존 비전 검사는 '불량인가 아닌가'만 판정합니다.",
        "FactoryMind는 '왜 불량인가, 어떻게 고치는가'까지 답합니다.",
        "검사 시스템이 아니라, 품질 개선 시스템입니다.",
    ], font_size=10)

# ═══ Slide 4: 주요 기능 정의 ═══
box = find_content_box(slides[3])
if box:
    clear_and_write(box, [
        "■ 핵심 기능 5가지",
        "",
        "기능 1. AI 외관 검사 (Vision AI)",
        "  • YOLO v11 기반 결함 위치 탐지 (바운딩 박스 + 히트맵)",
        "  • PatchCore 기반 Anomaly Detection (양품 학습 → 이상 탐지)",
        "  • 불량 유형 자동 분류: 스크래치, 크랙, 기포, 이물, 변형",
        "",
        "기능 2. 실시간 검사 대시보드",
        "  • 라인별 실시간 검사 결과 스트림 (양품/불량/보류)",
        "  • 시간대별·유형별·라인별 불량률 추이 그래프",
        "  • 불량 이미지 갤러리 + 결함 위치 시각화",
        "",
        "기능 3. 불량 원인 자동 추적 (Root Cause Analysis)",
        "  • 불량 발생 시점의 공정 파라미터 자동 조회 (온도, 압력, 속도, 습도)",
        "  • 상관 분석 + SHAP 기반 핵심 원인 변수 특정",
        '  • "크랙 발생과 금형 온도의 상관계수 0.73" 형태로 근거 제시',
        "",
        "기능 4. 조치 가이드 (RAG 기반)",
        "  • 불량 유형별 표준 조치 방법 자동 검색",
        "  • 과거 유사 사례 및 해결 이력 제공",
        "  • 공정 파라미터 조정 권장값 제시",
        "",
        "기능 5. 품질 리포트 자동 생성",
        "  • 일일/주간/월간 품질 통계 리포트",
        "  • 반복 불량 Top 5 + 원인 + 개선 현황 추적",
    ], font_size=9)

# ═══ Slide 5: 데이터 및 기술 활용 계획 ═══
box = find_content_box(slides[4])
if box:
    clear_and_write(box, [
        "■ 활용 데이터",
        "",
        "[비전 검사용]",
        "• MVTec AD — 15종 산업 제품 외관 결함 (5,354장, 이상 탐지 벤치마크)",
        "• Kaggle Casting Defect — 주조 제품 불량 이미지 (7,348장)",
        "• NEU Surface Defect — 열연 강판 표면 결함 6종 (1,800장)",
        "",
        "[원인 추적용]",
        "• SECOM — 반도체 공정 센서 590개 + 불량 라벨 (공정-불량 연결 데이터)",
        "• 시뮬레이션 데이터 — 온도/압력/속도와 불량 발생의 합성 데이터",
        "",
        "■ 제품 도면(CAD) 없이 동작하는 이유",
        "• 외관 불량 탐지 = 양품 이미지만 학습하면 됨 (Anomaly Detection)",
        "• 치수 검사(CAD 필요)는 Phase 2로 분리",
        "",
        "■ AI/분석 기술",
        "• 결함 탐지: YOLO v11 (위치), PatchCore/STFPM (이상 탐지)",
        "• 원인 분석: Feature Importance, SHAP (설명 가능 AI)",
        "• 조치 가이드: LangChain + Qdrant (RAG 기반)",
        "",
        "■ 기술 스택",
        "• AI: Python, PyTorch, Ultralytics(YOLO), anomalib",
        "• Backend: FastAPI, PostgreSQL, Qdrant",
        "• Frontend: Streamlit, Plotly",
        "• Infra: Docker Compose (FE + BE + Qdrant 일체화)",
    ], font_size=9)

# ═══ Slide 6: 사용자 시나리오 ═══
box = find_content_box(slides[5])
if box:
    clear_and_write(box, [
        "■ 주요 사용자",
        "① 품질 관리자 — 불량률 모니터링, 원인 분석, 개선 지시 (주 사용자)",
        "② 라인 작업자 — 실시간 검사 결과 확인, 불량 발생 시 즉시 대응",
        "③ 공장장 — 품질 KPI 대시보드, 주간/월간 품질 리포트 확인",
        "",
        '■ 대표 시나리오: "품질 관리자 이 대리의 오전"',
        "",
        "09:00  사출 라인 가동 → FactoryMind 자동 검사 시작",
        "  → 라인 카메라가 제품을 촬영, AI가 실시간 검사",
        "  → 대시보드에 양품/불량 카운트 실시간 표시",
        "",
        "09:15  크랙 불량 3건 연속 감지 → 알림 발생",
        '  → "A라인 크랙 불량 3건/15분 — 정상 대비 5배 (비정상)"',
        "  → 불량 이미지 + 결함 위치 히트맵 표시",
        "",
        "09:16  원인 추적 결과 자동 표시",
        '  → "금형 온도 87°C — 정상 범위(70~80°C) 초과"',
        '  → "최근 30분 온도 추이: 09:05부터 급상승"',
        '  → SHAP 분석: "금형 온도가 크랙 발생의 73% 기여"',
        "",
        "09:17  조치 가이드 확인 → 현장 조치",
        '  → "권장: 금형 온도 80°C 이하로 조정"',
        '  → "유사 사례: 2024.03 동일 패턴 — 냉각수 밸브 점검으로 해결"',
        "  → 작업자에게 조치 지시 → 10분 후 불량률 정상 복귀",
        "",
        "■ 핵심: 불량 감지 → 원인 특정 → 조치까지 2분 이내",
    ], font_size=9)

# ═══ Slide 7: MVP 구현 범위 ═══
box = find_content_box(slides[6])
if box:
    clear_and_write(box, [
        "■ 본선 MVP 구현 범위",
        "",
        "━━ Must-have (사전 준비 + 당일 통합) ━━",
        "  [사전] YOLO 결함 탐지 모델 학습 완료 (Casting/Steel 데이터)",
        "  [사전] PatchCore 이상 탐지 모델 학습 (MVTec AD)",
        "  [사전] SECOM 기반 공정-불량 상관 분석 파이프라인 구축",
        "  [사전] 조치 가이드 RAG 지식 베이스 구축",
        "  [당일] 실시간 검사 시뮬레이션 시연 (이미지 스트림 재생)",
        "  [당일] 불량 탐지 → 원인 추적 → 조치 가이드 E2E 시연",
        "  [당일] 품질 대시보드 통합 시연",
        "",
        "━━ Should-have ━━",
        "  불량 통계 리포트 자동 생성",
        "  반복 불량 패턴 알림",
        "  불량 이미지 갤러리 + 필터링",
        "",
        "━━ Phase 2+ (향후) ━━",
        "  치수 검사 (CAD 연동)",
        "  실시간 CCTV/라인 카메라 직결",
        "  MES 연동 (Lot 추적)",
        "  모바일 알림",
        "",
        "■ 역할 분담",
        "",
        "원정환 (Vision & Detection Engine)",
        "  • YOLO 결함 탐지 모델 학습 + 추론 파이프라인",
        "  • PatchCore 이상 탐지 모델 구현 (anomalib)",
        "  • 검사 시뮬레이션 (이미지 스트림 재생)",
        "  • Streamlit 대시보드 + Docker 시연 환경",
        "",
        "소지민 (Root Cause & Intelligence)",
        "  • 공정 파라미터 ↔ 불량 상관 분석 (SECOM + SHAP)",
        "  • 조치 가이드 RAG 구축 (지식 베이스 + 검색)",
        "  • 품질 통계 파이프라인 + 리포트 생성",
        "  • 데이터 통합 (비전 결과 + 공정 데이터 조인)",
    ], font_size=8)

# ═══ Slide 8: 기대 효과 ═══
box = find_content_box(slides[7])
if box:
    clear_and_write(box, [
        "■ 정량적 기대 효과",
        "",
        "• 불량 탐지율: 70~80% → 95% 이상",
        "  → 고객 유출 불량 75% 감소 → 클레임 비용 연 수천만원 절감",
        "• 불량 원인 추적 시간: 수일(수작업) → 2분(자동)",
        "  → 품질 관리자의 분석 업무 시간 80% 절감",
        "• 반복 불량률 50% 감소",
        "  → 원인 기반 조치로 동일 유형 재발 방지",
        "• 검사 인건비 60% 절감",
        "  → 3교대 육안 검사원 → AI 자동 검사 + 1인 모니터링",
        "",
        "■ 정성적 기대 효과",
        "",
        "• 검사 기준 일관성 확보: AI는 피로하지 않고 기준이 흔들리지 않음",
        "• 품질 노하우 디지털화: 숙련 검사원 은퇴 시에도 품질 유지",
        "• 데이터 기반 품질 문화: 감이 아닌 데이터로 의사결정",
        "• 거래처 신뢰도 향상: 불량률 데이터 + AI 검사 이력 제출 가능",
        "",
        "■ 현장 적용 가능성",
        "• 산업용 카메라(또는 스마트폰) + PC만 있으면 즉시 도입",
        "• 양품 이미지 100장이면 학습 시작 가능 (제품 도면 불필요)",
        "• Docker 기반 온프레미스 배포 — 공장 보안 정책 충족",
        "",
        "■ 향후 확장성",
        "• Phase 2: 치수 검사 (CAD 연동 + 비전 측정)",
        "• Phase 3: MES/ERP 연동 → Lot 단위 품질 추적",
        "• Phase 4: 멀티 라인/멀티 공장 통합 품질 관제",
        "• Phase 5: SaaS화 → 중소 제조업 구독형 품질 AI 서비스",
    ], font_size=10)

prs.save(SRC)
print("기획서 v3 저장 완료:", SRC)
