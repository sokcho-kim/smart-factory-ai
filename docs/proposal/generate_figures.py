"""기획서 도표/그림 생성."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

OUT = "docs/proposal/figures"


# ═══ 1. 슬라이드 3: 핵심 흐름도 (DETECT → TRACE → GUIDE) ═══
def make_flow_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(12, 3.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 3.5)
    ax.axis("off")

    steps = [
        {"x": 1, "label": "촬영", "sub": "웹캠/라인카메라\n제품 외관 촬영", "color": "#E3F2FD"},
        {"x": 3.5, "label": "① DETECT", "sub": "YOLO v8n\n양품/불량 판정\n불량 유형 분류", "color": "#BBDEFB"},
        {"x": 6, "label": "② TRACE", "sub": "공정 파라미터 매칭\n다변수 SHAP 분석\n인과관계 추적", "color": "#90CAF9"},
        {"x": 8.5, "label": "③ GUIDE", "sub": "조치 가이드 제공\n유사 사례 검색\n재발 방지", "color": "#64B5F6"},
        {"x": 11, "label": "기록", "sub": "자동 DB 적재\n타임스탬프 정확\n이력 축적", "color": "#42A5F5"},
    ]

    for s in steps:
        box = FancyBboxPatch((s["x"] - 0.9, 0.3), 1.8, 2.7,
                             boxstyle="round,pad=0.1", facecolor=s["color"],
                             edgecolor="#1565C0", linewidth=1.5)
        ax.add_patch(box)
        ax.text(s["x"], 2.65, s["label"], ha="center", va="center",
                fontsize=11, fontweight="bold", color="#0D47A1")
        ax.text(s["x"], 1.5, s["sub"], ha="center", va="center",
                fontsize=8, color="#333333")

    for i in range(len(steps) - 1):
        ax.annotate("", xy=(steps[i + 1]["x"] - 1.0, 1.75),
                     xytext=(steps[i]["x"] + 1.0, 1.75),
                     arrowprops=dict(arrowstyle="->", color="#1565C0", lw=2))

    ax.text(6, 0.05, "사람 입력 0건 — 전 과정 자동", ha="center", va="center",
            fontsize=10, fontstyle="italic", color="#E65100")

    fig.tight_layout()
    fig.savefig(f"{OUT}/flow_detect_trace_guide.png", dpi=200, bbox_inches="tight",
                facecolor="white")
    plt.close()
    print("✓ flow_detect_trace_guide.png")


# ═══ 2. 슬라이드 2: 문제 정의 — Before/After 비교 ═══
def make_before_after():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

    # Before
    ax1.set_title("기존 방식", fontsize=14, fontweight="bold", color="#C62828", pad=15)
    before = [
        ("09:47", "작업자가 불량 발견", "#FFCDD2"),
        ("09:50", "수기 기록 (시간 부정확)", "#FFCDD2"),
        ("12:00", "점심 — 기록 누락", "#EF9A9A"),
        ("15:00", "엑셀 확인 → 빠져있음", "#EF9A9A"),
        ("15:30", '"몇 시인지 모르겠다"', "#E57373"),
        ("", "→ 원인 추적 불가", "#D32F2F"),
    ]
    for i, (t, desc, c) in enumerate(before):
        y = 5 - i
        box = FancyBboxPatch((0.1, y - 0.35), 4.8, 0.65,
                             boxstyle="round,pad=0.05", facecolor=c, edgecolor="none")
        ax1.add_patch(box)
        label = f"{t}  {desc}" if t else desc
        ax1.text(2.5, y, label, ha="center", va="center", fontsize=9,
                color="white" if i >= 4 else "#333")
    ax1.set_xlim(0, 5)
    ax1.set_ylim(0, 6)
    ax1.axis("off")

    # After
    ax2.set_title("FactoryMind 도입 후", fontsize=14, fontweight="bold", color="#2E7D32", pad=15)
    after = [
        ("09:00", "라인 가동 → 웹캠 자동 촬영", "#C8E6C9"),
        ("09:42", "크랙 3건 감지 → 자동 알림", "#A5D6A7"),
        ("09:42", "금형 온도 86°C 원인 특정", "#81C784"),
        ("09:44", "작업자 온도 조정", "#66BB6A"),
        ("09:55", "불량률 정상 복귀", "#4CAF50"),
        ("", "→ 전 과정 자동 기록 완료", "#2E7D32"),
    ]
    for i, (t, desc, c) in enumerate(after):
        y = 5 - i
        box = FancyBboxPatch((0.1, y - 0.35), 4.8, 0.65,
                             boxstyle="round,pad=0.05", facecolor=c, edgecolor="none")
        ax2.add_patch(box)
        label = f"{t}  {desc}" if t else desc
        ax2.text(2.5, y, label, ha="center", va="center", fontsize=9,
                color="white" if i >= 4 else "#333")
    ax2.set_xlim(0, 5)
    ax2.set_ylim(0, 6)
    ax2.axis("off")

    fig.tight_layout()
    fig.savefig(f"{OUT}/before_after.png", dpi=200, bbox_inches="tight",
                facecolor="white")
    plt.close()
    print("✓ before_after.png")


# ═══ 3. 슬라이드 5: 시스템 아키텍처 ═══
def make_architecture():
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")

    # Layers
    layers = [
        {"y": 5, "h": 0.8, "label": "[VIEW] 대시보드 (Streamlit + Plotly)",
         "sub": "실시간 검사 현황  |  시계열 불량 추이  |  원인 분석 결과  |  품질 리포트",
         "color": "#E8F5E9"},
        {"y": 3.8, "h": 0.8, "label": "[AI] 엔진",
         "sub": "YOLO v8n 결함 탐지  |  PatchCore 이상 탐지  |  SHAP 인과 분석  |  조치 가이드 RAG",
         "color": "#E3F2FD"},
        {"y": 2.6, "h": 0.8, "label": "[API] 백엔드 (FastAPI)",
         "sub": "검사 결과 API  |  공정 데이터 조인  |  알림 엔진  |  리포트 생성",
         "color": "#FFF3E0"},
        {"y": 1.4, "h": 0.8, "label": "[DB] 데이터 (PostgreSQL)",
         "sub": "검사 이력 DB  |  공정 파라미터 DB  |  불량 이미지 저장  |  조치 이력",
         "color": "#F3E5F5"},
        {"y": 0.2, "h": 0.8, "label": "[HW] 데이터 수집",
         "sub": "웹캠 (3만원~)  |  PLC/센서 연동  |  시뮬레이션 데이터  |  Docker Compose",
         "color": "#FFEBEE"},
    ]

    for layer in layers:
        box = FancyBboxPatch((0.5, layer["y"] - 0.1), 11, layer["h"],
                             boxstyle="round,pad=0.1", facecolor=layer["color"],
                             edgecolor="#666", linewidth=1)
        ax.add_patch(box)
        ax.text(1.2, layer["y"] + layer["h"] / 2 + 0.05, layer["label"],
                ha="left", va="center", fontsize=11, fontweight="bold")
        ax.text(6, layer["y"] + layer["h"] / 2 - 0.15, layer["sub"],
                ha="center", va="center", fontsize=8.5, color="#555")

    # Arrows between layers
    for i in range(len(layers) - 1):
        ax.annotate("", xy=(6, layers[i]["y"] - 0.1),
                     xytext=(6, layers[i + 1]["y"] + layers[i + 1]["h"] - 0.1),
                     arrowprops=dict(arrowstyle="<->", color="#999", lw=1.5))

    fig.tight_layout()
    fig.savefig(f"{OUT}/architecture.png", dpi=200, bbox_inches="tight",
                facecolor="white")
    plt.close()
    print("✓ architecture.png")


# ═══ 4. 슬라이드 8: KPI 목표 차트 ═══
def make_kpi_chart():
    fig, axes = plt.subplots(1, 4, figsize=(12, 3))

    kpis = [
        {"label": "불량 탐지율", "before": 75, "after": 95, "unit": "%"},
        {"label": "데이터 수집률", "before": 10, "after": 100, "unit": "%"},
        {"label": "원인 추적 시간", "before": 100, "after": 5, "unit": "분", "lower_better": True},
        {"label": "도입 비용", "before": 100, "after": 10, "unit": "%", "lower_better": True},
    ]

    for ax, kpi in zip(axes, kpis):
        bars = ax.bar(["기존", "목표"], [kpi["before"], kpi["after"]],
                      color=["#EF9A9A", "#81C784"], edgecolor="none", width=0.5)
        ax.set_title(kpi["label"], fontsize=10, fontweight="bold", pad=8)
        ax.set_ylabel(kpi["unit"], fontsize=8)
        for bar, val in zip(bars, [kpi["before"], kpi["after"]]):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                    f"{val}{kpi['unit']}", ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax.set_ylim(0, max(kpi["before"], kpi["after"]) * 1.25)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.tight_layout()
    fig.savefig(f"{OUT}/kpi_chart.png", dpi=200, bbox_inches="tight",
                facecolor="white")
    plt.close()
    print("✓ kpi_chart.png")


# ═══ 5. 슬라이드 7: 역할 분담 ═══
def make_role_split():
    fig, ax = plt.subplots(1, 1, figsize=(10, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")

    # 정환
    box1 = FancyBboxPatch((0.3, 0.3), 4.2, 3.2,
                          boxstyle="round,pad=0.15", facecolor="#E3F2FD",
                          edgecolor="#1565C0", linewidth=2)
    ax.add_patch(box1)
    ax.text(2.4, 3.2, "원정환", ha="center", va="center",
            fontsize=13, fontweight="bold", color="#0D47A1")
    ax.text(2.4, 2.7, "Vision Engine + Platform", ha="center", va="center",
            fontsize=9, color="#1565C0", fontstyle="italic")

    tasks1 = [
        "YOLO v8n 결함 탐지 모델",
        "PatchCore 이상 탐지",
        "Streamlit 대시보드",
        "Docker Compose 시연 환경",
    ]
    for j, t in enumerate(tasks1):
        ax.text(2.4, 2.1 - j * 0.45, f"• {t}", ha="center", va="center", fontsize=8.5)

    # 지민
    box2 = FancyBboxPatch((5.5, 0.3), 4.2, 3.2,
                          boxstyle="round,pad=0.15", facecolor="#FFF3E0",
                          edgecolor="#E65100", linewidth=2)
    ax.add_patch(box2)
    ax.text(7.6, 3.2, "소지민", ha="center", va="center",
            fontsize=13, fontweight="bold", color="#BF360C")
    ax.text(7.6, 2.7, "Data Intelligence + Root Cause", ha="center", va="center",
            fontsize=9, color="#E65100", fontstyle="italic")

    tasks2 = [
        "공정-불량 인과 분석 (SHAP)",
        "시계열 품질 추적 파이프라인",
        "조치 가이드 지식 베이스",
        "데이터 통합 (비전+센서 조인)",
    ]
    for j, t in enumerate(tasks2):
        ax.text(7.6, 2.1 - j * 0.45, f"• {t}", ha="center", va="center", fontsize=8.5)

    # 가운데 연결
    ax.annotate("", xy=(5.5, 2.0), xytext=(4.5, 2.0),
                arrowprops=dict(arrowstyle="<->", color="#333", lw=2))
    ax.text(5.0, 2.3, "API\nJSON", ha="center", va="center", fontsize=8,
            color="#666", fontstyle="italic")

    fig.tight_layout()
    fig.savefig(f"{OUT}/role_split.png", dpi=200, bbox_inches="tight",
                facecolor="white")
    plt.close()
    print("✓ role_split.png")


# ═══ 6. 슬라이드 4: 기능 구성도 ═══
def make_feature_cards():
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.5))

    features = [
        {"title": "① DETECT\n자동 검사", "items": ["YOLO v8n 결함 탐지", "양품/불량 판정", "불량 유형 분류", "웹캠으로 동작"], "color": "#E3F2FD", "edge": "#1565C0"},
        {"title": "② RECORD\n자동 기록", "items": ["타임스탬프 자동", "사람 입력 0건", "시계열 데이터 축적", "교대조별 비교"], "color": "#E8F5E9", "edge": "#2E7D32"},
        {"title": "③ TRACE\n원인 추적", "items": ["공정 파라미터 매칭", "다변수 SHAP 분석", "인과관계 특정", "복합 상호작용"], "color": "#FFF3E0", "edge": "#E65100"},
        {"title": "④ GUIDE\n조치 안내", "items": ["표준 조치 가이드", "유사 사례 검색", "재발 방지 추적", "품질 리포트"], "color": "#F3E5F5", "edge": "#6A1B9A"},
    ]

    for ax, f in zip(axes, features):
        ax.set_xlim(0, 4)
        ax.set_ylim(0, 5)
        ax.axis("off")
        box = FancyBboxPatch((0.1, 0.1), 3.8, 4.8,
                             boxstyle="round,pad=0.15", facecolor=f["color"],
                             edgecolor=f["edge"], linewidth=2)
        ax.add_patch(box)
        ax.text(2, 4.3, f["title"], ha="center", va="center",
                fontsize=11, fontweight="bold", color=f["edge"])
        for j, item in enumerate(f["items"]):
            ax.text(2, 3.0 - j * 0.65, f"• {item}", ha="center", va="center",
                    fontsize=8.5, color="#333")

    fig.tight_layout()
    fig.savefig(f"{OUT}/feature_cards.png", dpi=200, bbox_inches="tight",
                facecolor="white")
    plt.close()
    print("✓ feature_cards.png")


if __name__ == "__main__":
    make_flow_diagram()
    make_before_after()
    make_architecture()
    make_kpi_chart()
    make_role_split()
    make_feature_cards()
    print("\n모든 도표 생성 완료 →", OUT)
