"""기획서 v2 — 시나리오 B: 유령 도면 복원 + 안전 관제 플랫폼."""
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor

SRC = "docs/proposal/기획서_v2.pptx"
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
        table.cell(1, 1).text = "유령 도면 복원 기반 AI 공장 안전 관제 플랫폼"
        for row in table.rows:
            for cell in row.cells:
                for p in cell.text_frame.paragraphs:
                    p.font.size = Pt(12)

# ═══ Slide 2: 문제 정의 ═══
box = find_content_box(slides[1])
if box:
    clear_and_write(box, [
        "■ 핵심 문제: 도면과 현장이 다르다 — '유령 도면' 문제",
        "",
        "제조 현장의 설비 배치도(도면)는 최초 설치 시점에 작성된 후",
        "설비 이동, 증설, 철거, 통로 변경 등이 반영되지 않은 채 방치됩니다.",
        "이렇게 현장과 괴리된 도면을 '유령 도면(Ghost Blueprint)'이라 합니다.",
        "",
        "• 문제 1: 국내 중소 제조업체의 78%가 최신 설비 배치도를 보유하지 않음",
        "  (한국산업안전보건공단, 2024 사업장 안전실태조사)",
        "• 문제 2: 화재/누출 사고 시 대피 경로가 도면과 불일치하여 대응 지연",
        "  (2024 화성 배터리 공장 화재 — 도면상 비상구 위치와 실제 불일치 지적)",
        "• 문제 3: 안전 점검 시 도면 기반 체크리스트가 무의미해지는 악순환",
        "",
        "■ 해결 대상",
        "• 설비 배치가 수시로 변하는 중소 제조 공장 (100~500인 규모)",
        "• 도면 관리 인력이 없어 현장-도면 괴리가 누적되는 사업장",
        "",
        "■ 핵심 KPI",
        "• 도면-현장 일치율: 기존 측정 불가 → 90% 이상 자동 갱신",
        "• 안전 위반 탐지: 수동 점검(월 1회) → AI 실시간 상시 감시",
        "• 사고 대응 시간: 현장 파악 47분 → 도면 기반 즉시 확인 (<5분)",
    ], font_size=10)

# ═══ Slide 3: 솔루션 개요 ═══
box = find_content_box(slides[2])
if box:
    clear_and_write(box, [
        "■ FactoryMind — 죽은 도면을 살리는 AI 안전 관제 플랫폼",
        "",
        "현장 사진/영상에서 AI가 설비와 장애물을 탐지하고,",
        "기존 도면과 자동 대조하여 차이를 발견하고,",
        "안전 법규 위반 여부까지 판단하는 통합 플랫폼입니다.",
        "",
        "■ 핵심 아이디어: 3단계 자동화",
        "",
        "① SEE  — 현장을 본다",
        "   YOLO 기반 Object Detection으로 현장 사진에서 설비/통로/장애물 탐지",
        "",
        "② COMPARE — 도면과 비교한다",
        "   탐지된 객체 좌표를 도면 위에 매핑, 변경점(이동/추가/제거) 자동 식별",
        "",
        "③ JUDGE — 위험을 판단한다",
        "   산업안전보건법 기반 Graph-RAG로 법규 위반 여부 자동 점검",
        '   (예: "비상구 앞 1.2m 내 장애물 적치 — 산안법 제16조 위반")',
        "",
        "■ 차별점",
        '기존 스마트팩토리는 "센서 데이터 → 예측"에 집중합니다.',
        'FactoryMind는 "공간 데이터 → 안전"이라는 새로운 축을 제시합니다.',
        "센서가 없는 공장도, 카메라 한 대면 시작할 수 있습니다.",
    ], font_size=10)

# ═══ Slide 4: 주요 기능 정의 ═══
box = find_content_box(slides[3])
if box:
    clear_and_write(box, [
        "■ 핵심 기능 5가지",
        "",
        "기능 1. 현장 객체 탐지 (Vision AI)",
        "  • YOLO v11 기반 설비/통로/장애물/소화기/비상구 탐지",
        "  • 현장 사진 또는 CCTV 프레임 입력 → 객체 목록 + 좌표 출력",
        "",
        "기능 2. 도면 자동 갱신 (Blueprint Sync)",
        "  • 탐지된 객체를 기존 도면(SVG/이미지) 위에 오버레이",
        "  • 변경점 자동 감지: 신규 설비, 이동된 설비, 제거된 설비, 통로 차단",
        "  • 변경 이력 타임라인 관리",
        "",
        "기능 3. 안전 법규 자동 점검 (Safety RAG)",
        "  • 산업안전보건법, 소방법 등 관련 법규를 Graph-RAG로 구축",
        "  • 현장 상태 vs 법규 요건 자동 대조 → 위반 사항 리스트업",
        '  • 위반 근거 조문 + 시정 가이드 제공 (예: "통로폭 1.2m → 법정 1.5m")',
        "",
        "기능 4. 위험 지도 대시보드",
        "  • 도면 위 히트맵으로 위험 구역 시각화",
        "  • 설비별/구역별 안전 점수 산정",
        "  • 안전 관리자용 일일 리포트 자동 생성",
        "",
        "기능 5. 변경점 알림 및 보고",
        "  • 현장-도면 괴리 발생 시 즉시 알림",
        "  • 안전 점검 보고서 자동 생성 (법정 양식 기반)",
    ], font_size=10)

# ═══ Slide 5: 데이터 및 기술 활용 계획 ═══
box = find_content_box(slides[4])
if box:
    clear_and_write(box, [
        "■ 활용 데이터",
        "• 공장 배치도 (CAD/PDF/이미지) — 샘플 도면 자체 제작 또는 공개 도면 활용",
        "• 공장 현장 사진 — AI Hub '산업현장 안전장비 이미지', Roboflow 공장 데이터셋",
        "• 산업안전보건법/소방법 조문 — 법제처 Open API (법령 XML 파싱 경험 보유)",
        "• YOLO 학습용 어노테이션 — Roboflow 산업 설비 데이터셋 + 자체 라벨링",
        "",
        "■ AI/분석 기술",
        "• Object Detection: YOLO v11 (설비/장애물/안전설비 탐지)",
        "  — 정환의 YOLO+DeepSORT 주차장/압력솥 프로젝트 경험 직접 활용",
        "• Image Alignment: 도면-현장 좌표 정합 (Homography 변환)",
        "• Graph-RAG: 안전 법규 지식 그래프 + 조문 검색",
        "  — 지민의 graph-rag-study 경험 직접 활용",
        "• OCR/IDP: 도면 PDF 텍스트 추출 (PyMuPDF + Tesseract)",
        "",
        "■ 기술 스택",
        "• AI: Python, PyTorch, Ultralytics(YOLO), LangChain",
        "• Backend: FastAPI, Qdrant (벡터DB), PostgreSQL",
        "• Frontend: Streamlit (대시보드), Plotly/Leaflet (도면 시각화)",
        "• Infra: Docker Compose (FE+BE+Qdrant 일체화)",
        "",
        "■ 기술적 제약 및 해결 전략",
        "• 실제 공장 데이터 부재 → 샘플 공장 도면 자체 제작 + 공개 데이터 혼합",
        "• 도면-사진 정합 정확도 → Homography 기반 수동 앵커 + 자동 보정 병행",
        "• 법규 DB 구축 범위 → 산안법 핵심 조항(통로, 소화기, 비상구) 우선 구축",
    ], font_size=10)

# ═══ Slide 6: 사용자 시나리오 ═══
box = find_content_box(slides[5])
if box:
    clear_and_write(box, [
        "■ 주요 사용자",
        "① 안전 관리자 — 공장 안전 점검 및 법규 준수 확인 (주 사용자)",
        "② 공장장/시설팀 — 설비 배치 변경 관리, 대피 경로 확인",
        "③ 외부 점검관 — 산업안전보건공단 점검 시 현황 자료 제출",
        "",
        '■ 대표 시나리오: "안전 관리자 김 과장의 월요일"',
        "",
        "09:00  주말 동안 생산라인 재배치 발생",
        '  → 현장 직원이 스마트폰으로 현장 사진 촬영 후 업로드',
        "",
        "09:05  FactoryMind가 사진 분석",
        "  → YOLO가 설비 12대, 소화기 3개, 통로 4개 탐지",
        "  → 기존 도면과 대조: 프레스기 2대 이동, 통로 1개 차단 감지",
        '  → 도면 위에 변경점 빨간색 표시 + "도면 갱신 필요" 알림',
        "",
        "09:10  안전 법규 자동 점검 결과 확인",
        '  → "B구역 통로폭 1.2m — 산안법 시행규칙 제17조 위반 (최소 1.5m)"',
        '  → "C구역 소화기 이동 — 소방법 제10조 기준 접근 거리 초과"',
        "  → 위반 2건 + 시정 가이드 포함 보고서 자동 생성",
        "",
        "09:15  도면 갱신 승인 → 최신 도면 확정",
        "  → 변경 이력에 자동 기록",
        "  → 다음 점검 시 이 도면이 기준이 됨",
        "",
        "■ 핵심: 사진 한 장이면 도면 갱신 + 안전 점검이 동시에 끝난다",
    ], font_size=9)

# ═══ Slide 7: MVP 구현 범위 ═══
box = find_content_box(slides[6])
if box:
    clear_and_write(box, [
        "■ 본선 MVP 구현 범위",
        "",
        "━━ Must-have (사전 준비 + 당일 통합) ━━",
        "  [사전] YOLO 모델 학습 완료 (설비/통로/소화기/비상구 탐지)",
        "  [사전] 샘플 공장 도면 제작 + 좌표 매핑 체계 구축",
        "  [사전] 산안법 핵심 조항 Graph-RAG 구축",
        "  [당일] 현장 사진 업로드 → 객체 탐지 → 도면 오버레이 시연",
        "  [당일] 도면-현장 변경점 자동 감지 시연",
        "  [당일] 안전 법규 위반 탐지 + 근거 조문 제시 시연",
        "",
        "━━ Should-have ━━",
        "  위험 지도 히트맵",
        "  변경 이력 타임라인",
        "  안전 점검 보고서 PDF 생성",
        "",
        "━━ Phase 2+ (향후) ━━",
        "  실시간 CCTV 연동 (DeepSORT 추적)",
        "  3D 도면 지원 (디지털 트윈)",
        "  모바일 앱 (현장 사진 즉시 업로드)",
        "",
        "■ 역할 분담",
        "",
        "소지민 (Space & Logic Architect)",
        "  • 산안법/소방법 Graph-RAG 구축 (법령 파싱 + 지식 그래프)",
        "  • 도면 파싱 및 객체-법규 매칭 로직",
        "  • 위반 판정 엔진 + 시정 가이드 생성",
        "",
        "원정환 (Vision & Platform Engineer)",
        "  • YOLO 학습 + 현장 객체 탐지 파이프라인",
        "  • 도면-사진 좌표 정합 (Homography)",
        "  • Streamlit 대시보드 + Docker 시연 환경",
    ], font_size=9)

# ═══ Slide 8: 기대 효과 ═══
box = find_content_box(slides[7])
if box:
    clear_and_write(box, [
        "■ 정량적 기대 효과",
        "",
        "• 도면 갱신 비용 90% 절감",
        "  → 외부 용역(건당 200~500만원) → 사진 촬영만으로 자동 갱신",
        "• 안전 점검 시간 70% 단축",
        "  → 수동 현장 대조(4시간) → AI 자동 점검(30분 이내)",
        "• 안전 위반 탐지율 향상",
        "  → 월 1회 수동 점검 → 상시 AI 감시 (사진 업로드 시마다)",
        "",
        "■ 정성적 기대 효과",
        "",
        "• 산업재해 예방: 도면-현장 괴리로 인한 대피 실패 방지",
        "• 법규 준수 자동화: 안전 관리자의 법규 숙지 부담 경감",
        "• 감사 대응력 강화: 점검관에게 최신 도면 + 점검 이력 즉시 제출",
        "• 중소기업 안전관리 민주화: 전문 인력 없이도 AI가 안전 점검",
        "",
        "■ 현장 적용 가능성",
        "• 스마트폰 카메라 + 기존 도면만 있으면 즉시 도입 가능",
        "• 센서/IoT 장비 추가 설치 불필요 — 진입 장벽 최소화",
        "• Docker 기반 온프레미스 배포로 보안 이슈 없음",
        "",
        "■ 향후 확장성",
        "• Phase 2: CCTV 실시간 연동 → 상시 모니터링 (DeepSORT 추적)",
        "• Phase 3: 센서 데이터 융합 → 설비 예지보전 + 공간 안전 통합",
        "• Phase 4: 디지털 트윈 → 3D 공장 모델 + 사고 시뮬레이션",
        "• Phase 5: SaaS화 → 다공장 관리, 산업단지 단위 안전 관제",
    ], font_size=10)

prs.save(SRC)
print("기획서 v2 저장 완료:", SRC)
