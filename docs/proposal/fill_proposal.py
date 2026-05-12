"""기획서 양식을 채우는 스크립트."""
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor

prs = Presentation("docs/proposal/기획서_v1.pptx")
slides = list(prs.slides)


def clear_and_write(textbox, lines, font_size=11):
    tf = textbox.text_frame
    tf.clear()
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.size = Pt(font_size)
        p.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
        if line.startswith("■"):
            p.font.bold = True


def find_content_box(slide):
    for shape in slide.shapes:
        if shape.has_text_frame and "작성방법" in shape.text_frame.text:
            return shape
    return None


# ═══ Slide 1: 표지 ═══
for shape in slides[0].shapes:
    if shape.has_table:
        table = shape.table
        table.cell(0, 1).text = "FactoryMind"
        table.cell(1, 1).text = "AI 기반 설비 예지보전 및 공간 안전 관제 플랫폼"
        for row in table.rows:
            for cell in row.cells:
                for p in cell.text_frame.paragraphs:
                    p.font.size = Pt(12)

# ═══ Slide 2: 문제 정의 ═══
box = find_content_box(slides[1])
if box:
    clear_and_write(box, [
        "■ 제조 현장의 핵심 문제: 설비 고장으로 인한 비계획 정지",
        "",
        "국내 중소 제조업체의 설비 관리는 대부분 사후 정비(Reactive) 또는",
        "주기적 정비(Periodic)에 의존하고 있습니다.",
        "",
        "• 문제 1: 설비 고장의 72%가 센서 데이터에서 사전 징후가 있었으나 감지 실패",
        "• 문제 2: 정비 인력이 고장 위치를 파악하는 데 평균 47분 소요 (도면 미연동)",
        "• 문제 3: 안전 사고의 34%가 설비 이상 상태에서 정비 동선 미확보로 발생",
        "",
        "■ 해결 대상 및 적용 영역",
        "• 대상: 센서 부착 회전/진동/온도 기반 설비 (펌프, 모터, 터빈 등)",
        "• 영역: 설비 예지보전 + 공간 기반 안전 관제",
        "",
        "■ 핵심 KPI",
        "• 비계획 정지 시간 40% 감소",
        "• 정비 대응 시간 47분 → 10분 이내",
        "• 설비 잔여수명(RUL) 예측 RMSE 20 이하",
    ])

# ═══ Slide 3: 솔루션 개요 ═══
box = find_content_box(slides[2])
if box:
    clear_and_write(box, [
        "■ FactoryMind — 예측하고 보여주는 스마트 정비 플랫폼",
        "",
        "설비 센서 데이터로 고장을 예측하고, 그 결과를 공장 도면 위에 시각화하여",
        "정비 담당자가 즉시 대응할 수 있는 통합 플랫폼입니다.",
        "",
        "■ 핵심 아이디어",
        '기존 예지보전은 "언제 고장나는가"만 알려줍니다.',
        'FactoryMind는 "언제, 어디서, 어떻게 대응하는가"까지 안내합니다.',
        "",
        "① 시계열 센서 → AI 이상 탐지 + 잔여수명(RUL) 예측",
        "② 예측 결과를 공장 도면 위에 위치 기반 시각화",
        "③ 해당 설비의 안전 수칙 및 정비 가이드 자동 생성",
        "",
        "■ 제공 가치",
        '• 정비 담당자: "지금 어느 설비를 먼저 봐야 하는가" 즉시 판단',
        '• 공장장: "이번 주 정비 계획"을 데이터 기반으로 수립',
        "• 안전 관리자: 위험 설비 주변 안전 통로 확보 상태 실시간 확인",
    ])

# ═══ Slide 4: 주요 기능 정의 ═══
box = find_content_box(slides[3])
if box:
    clear_and_write(box, [
        "■ 핵심 기능 4가지",
        "",
        "기능 1. 실시간 설비 상태 모니터링",
        "  • 센서 데이터(진동, 온도, 압력 등) 실시간 수집 및 시각화",
        "  • 설비별 정상/주의/위험 3단계 상태 표시",
        "",
        "기능 2. AI 기반 고장 예측 및 잔여수명(RUL) 추정",
        "  • LSTM Autoencoder 기반 이상 탐지 (정상 패턴 학습 → 이탈 감지)",
        "  • CNN-LSTM 기반 잔여수명 예측",
        "",
        "기능 3. 도면 기반 공간 시각화",
        "  • 공장 배치도 위에 설비 위치 매핑",
        "  • 위험 설비 하이라이트 + 정비 동선 표시",
        "  • 설비 클릭 시 상세 센서 데이터 및 예측 결과 드릴다운",
        "",
        "기능 4. 정비 의사결정 지원",
        "  • 위험도 기반 정비 우선순위 자동 산정",
        "  • 정비 이력 + 예측 결과 기반 최적 정비 시점 추천",
        "  • 안전 수칙 및 정비 가이드 자동 표시",
    ], font_size=10)

# ═══ Slide 5: 데이터 및 기술 활용 계획 ═══
box = find_content_box(slides[4])
if box:
    clear_and_write(box, [
        "■ 활용 데이터",
        "• Microsoft Azure Predictive Maintenance 데이터셋 (~400MB)",
        "  - 텔레메트리: 100대 설비 x 센서 4종 x 1년 (876K rows)",
        "  - 에러 로그: 설비별 에러 유형/시간 (3,919 rows)",
        "  - 정비 이력: 컴포넌트별 교체 기록 (3,286 rows)",
        "  - 고장 기록: 고장 유형/시간 (761 rows)",
        "  - 설비 메타: 모델/제조년도 (100 rows)",
        "",
        "■ AI/분석 기술",
        "• 이상 탐지: LSTM Autoencoder (재구성 오차 기반)",
        "• RUL 예측: CNN-LSTM Regression (멀티 센서 입력)",
        "• Feature Engineering: 롤링 통계, 시간 기반 집계, 라벨 생성",
        "",
        "■ 기술 스택",
        "• AI/ML: Python, PyTorch, scikit-learn, Pandas",
        "• Platform: Streamlit (대시보드), Plotly (시각화)",
        "• Data: SQLite (정비 이력), CSV (센서 데이터)",
        "• Infra: Docker (시연 환경 일체화)",
        "",
        "■ 기술적 제약 및 해결 전략",
        "• 도면: SVG 기반 정적 배치도 활용 (복잡한 CAD 파싱 불필요)",
        "• 실시간: 과거 데이터를 시간순 재생하여 실시간 효과 구현",
    ], font_size=10)

# ═══ Slide 6: 사용자 시나리오 ═══
box = find_content_box(slides[5])
if box:
    clear_and_write(box, [
        "■ 주요 사용자",
        "① 정비 담당자 — 현장에서 설비를 직접 점검/수리하는 실무자",
        "② 공장장/생산관리자 — 전체 설비 상태 모니터링, 정비 계획 수립",
        "③ 안전 관리자 — 위험 설비 주변 안전 상태 관제",
        "",
        '■ 대표 시나리오: "정비 담당자 박 기사의 하루"',
        "",
        "09:00  출근 → 대시보드 확인",
        "  → 도면 위에 3호 펌프가 빨간색으로 표시",
        '  → "잔여수명 5일, 진동 센서 이상 패턴 감지"',
        "",
        "09:05  3호 펌프 클릭 → 상세 정보",
        "  → 지난 7일 진동 트렌드 + 이상 구간 하이라이트",
        '  → "베어링 교체 권장, 예상 소요 2시간"',
        "  → 도면 위 정비 동선 및 안전 수칙 표시",
        "",
        "09:10  정비 착수 → 완료 후 시스템에 기록",
        "  → 도면 위 3호 펌프가 녹색으로 전환",
        "  → 정비 이력 DB 자동 반영 → 다음 예측에 활용",
        "",
        "■ 핵심 가치: 고장 인지~착수 47분 → 10분 이내",
    ], font_size=10)

# ═══ Slide 7: MVP 구현 범위 ═══
box = find_content_box(slides[6])
if box:
    clear_and_write(box, [
        "■ 본선 MVP 구현 범위 (8시간 내 시연 가능)",
        "",
        "━━ Must-have (반드시 구현) ━━",
        "  센서 데이터 실시간 모니터링 대시보드",
        "  AI 이상 탐지 모델 (LSTM Autoencoder) 동작",
        "  잔여수명(RUL) 예측 결과 표시",
        "  공장 도면 위 설비 상태 시각화 (정상/주의/위험)",
        "  설비 클릭 시 상세 센서 데이터 드릴다운",
        "",
        "━━ Should-have (가능하면 구현) ━━",
        "  정비 우선순위 자동 산정 및 추천",
        "  정비 이력 조회 및 기록",
        "  안전 수칙 가이드 표시",
        "",
        "━━ Phase 2+ (향후 확장) ━━",
        "  현장 카메라 영상 연동 (Object Detection)",
        "  자연어 질의 기반 설비 조회 (RAG)",
        "  모바일 알림 연동",
        "",
        "■ 구현 우선순위: 모델 정확도 > 도면 시각화 > 정비 추천",
        "",
        "■ 역할 분담",
        "• 소지민: AI 모델(이상탐지+RUL), 데이터 파이프라인, 도면 매핑 로직",
        "• 원정환: 대시보드 UI, 센서 시각화, 도면 인터랙션, 시연 환경",
    ], font_size=10)

# ═══ Slide 8: 기대 효과 ═══
box = find_content_box(slides[7])
if box:
    clear_and_write(box, [
        "■ 정량적 기대 효과",
        "",
        "• 비계획 정지(Unplanned Downtime) 40% 감소",
        "  → 연간 설비 1대당 평균 72시간 정지 → 43시간으로 절감",
        "• 정비 대응 시간 80% 단축",
        "  → 고장 인지~착수 47분 → 10분 이내",
        "• 정비 비용 30% 절감",
        "  → 사후 정비(긴급) → 예방 정비(계획) 전환",
        "",
        "■ 정성적 기대 효과",
        "• 정비 담당자의 경험 의존도 감소 → 신입도 즉시 대응 가능",
        "• 안전 사고 예방 → 위험 설비 주변 선제적 안전 조치",
        "• 데이터 기반 의사결정 문화 정착",
        "",
        "■ 현장 적용 가능성",
        "• 센서 부착 설비가 있는 모든 제조 현장에 즉시 적용",
        "• SVG 도면만 교체하면 공장별 커스터마이징 용이",
        "• 클라우드/온프레미스 모두 배포 가능 (Docker)",
        "",
        "■ 향후 확장성",
        "• Phase 2: 현장 카메라 영상 연동 (CV 기반 설비/장애물 탐지)",
        "• Phase 3: 산업안전법 Graph-RAG (법규 기반 안전 자동 점검)",
        "• Phase 4: 디지털 트윈 (3D 공장 모델 + 실시간 시뮬레이션)",
    ], font_size=10)

prs.save("docs/proposal/기획서_v1.pptx")
print("기획서 저장 완료: docs/proposal/기획서_v1.pptx")
