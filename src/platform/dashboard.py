"""PunchLine Dashboard — Streamlit 대시보드 뼈대."""
import streamlit as st

st.set_page_config(page_title="PunchLine", layout="wide")
st.title("PunchLine")
st.caption("AI 비전 기반 품질 자동 기록 및 불량 원인 추적")

tab1, tab2, tab3 = st.tabs(["실시간 검사", "시계열 추적", "원인 분석"])

with tab1:
    st.header("실시간 검사 현황")
    st.info("Phase 2에서 구현 예정 — 이미지 스트림 + 양품/불량 판정")

with tab2:
    st.header("시계열 품질 추적")
    st.info("Phase 2에서 구현 예정 — 시간대별 불량률 차트")

with tab3:
    st.header("불량 원인 분석")
    st.info("Phase 2에서 구현 예정 — SHAP 분석 + 원인 Top3")
