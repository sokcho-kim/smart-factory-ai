# 스마트 팩토리 대시보드 UI 사례 조사

> 조사일: 2026-05-14
> 목적: 공장 현장에서 실제 사용하는 대시보드 뷰 패턴 파악 → 해커톤 대시보드 설계 근거

---

## 참고 제품/사례

- **글로벌 MES/SCADA**: Siemens MindSphere, GE Proficy, Rockwell FactoryTalk, AVEVA, Tulip, Ignition, ThingWorx
- **AI 비전 검사**: Cognex ViDi, Landing AI, Elementary AI, Instrumental
- **한국**: 포스코DX PosFrame, SAIGE (PCB 검사), AHHA Labs (타이어)
- **HMI 표준**: ISA-101, Rockwell High Performance HMI Style Guide

---

## 뷰 타입별 정리

### 1. 안돈 보드 (Andon Board)

현장 벽면 대형 모니터에 거치하는 실시간 상태판.

- **라인별 상태**: 초록(정상) / 노랑(주의) / 빨강(정지) 신호등 패턴
- **Target vs Actual**: 목표 생산량 대비 실적. 큰 폰트 (5m 거리 판독)
- **호출 경과 시간**: 작업자 도움 요청 후 경과 시간
- **현재 불량률/OEE**: 핵심 KPI 하나에 화면 40~50% 할당
- 대상: 현장 작업자
- 참고: Peakboard, AVEVA Andon Visual Display

### 2. OEE 대시보드

관리자용 종합 현황. Tulip, Parsec TrakSYS에서 표준화.

- **3대 게이지**: 가용률(Availability) · 성능(Performance) · 품질(Quality)
- **다운타임 Pareto**: 정지 사유 Top 5 바 차트
- **시프트별 비교**: 주간/야간 교대 성과 비교 테이블
- **트렌드 라인**: 일별/주별 OEE 추이
- 대상: 공장 관리자

### 3. SPC 관리도 (Statistical Process Control)

ISA 표준, dataPARC 기반 패턴.

- **X-bar/R 차트**: 공정 파라미터(온도, 압력)의 UCL/LCL 한계선 + 실측값
- **이상 탐지 규칙**: 연속 7점 상승, 한계선 이탈 시 색상 전환 (회색→빨강)
- **Pareto 차트**: 불량 유형별 빈도 분포 (80/20 원칙)
- 대상: 품질 관리자
- 구현: Recharts `ReferenceLine` 컴포넌트로 UCL/LCL 표현

### 4. AI 비전 검사 결과 뷰

Cognex ViDi, Landing AI, Elementary AI 공통 패턴.

- **이미지 갤러리**: OK/NG 분류된 검사 이미지 그리드. NG에 바운딩 박스 + 불량 유형 레이블 오버레이
- **히트맵 오버레이**: Cognex ViDi Red 대표. 불량 위치를 히트맵으로 시각화
- **Confidence Score 바**: 판정 신뢰도 게이지. 임계값 미만 시 "사람 검토" 에스컬레이션
- **디지털 불량 도감 (Defect Book)**: Landing AI. 불량 유형별 대표 이미지+설명 카탈로그
- 대상: 검사 담당자, AI 엔지니어

### 5. 교대 핸드오프 (Shift Handoff)

TeepTrak 등에서 권장.

- **이전 시프트 요약**: 생산량, 불량률, 주요 이슈 리스트
- **미해결 알람**: 다음 시프트가 이어받을 문제
- **당일 누적 트렌드**: 시프트 경계선이 표시된 타임라인 차트
- 대상: 교대 작업자

### 6. 근본원인 분석 뷰

SHAP/XAI 기반 — 우리 프로젝트 고유.

- **Pareto 차트**: 공정 파라미터별 SHAP 기여도 내림차순
- **정상 범위 비교**: 현재값 vs 정상 범위 시각화 (bullet chart or range bar)
- **조치 가이드**: 파라미터별 권장 조치 텍스트
- **과거 유사 사례**: 동일 패턴 발생 이력
- 대상: 공정 엔지니어

---

## ISA-101 고성능 HMI 디자인 원칙

실제 공장 느낌을 내는 핵심. Rockwell HMI Style Guide, RealPars 참고.

| 원칙 | 설명 |
|------|------|
| 회색 기반 배경 | 정상 상태는 전부 그레이스케일. 색상은 오직 이상/알람에만 사용 |
| 색상 절약 효과 | 이상 탐지율 48% 향상 (HMI 연구 결과) |
| 여백 40~60% | 화면의 절반 가까이를 빈 공간으로 유지 |
| 계층적 드릴다운 | 전체 공장 → 라인 → 설비 → 센서값 4단계 |
| 알람 색상 표준 | 빨강=위험/정지, 노랑=경고/주의, 초록=정상 (이것만) |

**적용**: shadcn/ui의 neutral 팔레트를 기본으로 쓰고, destructive(빨강)/warning(노랑)은 알람에만.

---

## 한국 스마트팩토리 맥락

- **포스코DX PosFrame**: IoT/BigData/AI 통합 플랫폼. 사용자 정의 대시보드 + AI 모델 성능 모니터링
- **SAIGE**: PCB 검사 SaaS. 불량률 분석 대시보드 + AI 비전 자동검사. 한국 중소 제조업 대상
- **AHHA Labs**: 타이어 불량 검사. 3단계 파이프라인(불량 유무 → 위치 → 유형) 시각화. 99.9% 정확도
- **정부 스마트공장 5단계 모델**: 기초(1)→중간1(2)→중간2(3)→고도화(4)→최적화(5). 대시보드 수준이 단계 판정 기준에 포함

---

## 우리 프로젝트 적용 — 우선순위

API 엔드포인트 매핑 기준:

| 우선순위 | 뷰 | API | 설명 |
|---------|-----|-----|------|
| P0 | 안돈 메인 보드 | `/quality/kpi` + `/inspect/stream` | OK/NG 실시간 카운트 + 불량률 게이지 |
| P0 | 검사 갤러리 | `/inspect/stream` | 이미지 + bbox 오버레이, NG 필터 |
| P1 | SPC 타임라인 | `/quality/timeline` | 관리도 + UCL/LCL + 이상 포인트 강조 |
| P1 | SHAP 원인 분석 | `/quality/root-cause` | Pareto + 정상범위 비교 + 조치 가이드 |
| P2 | OEE 게이지 | `/quality/kpi` 확장 | 가용률·성능·품질 3대 게이지 |
| P2 | 교대 핸드오프 | `/quality/report` | 시프트 요약 + 미해결 알람 |

---

## 참고 자료

- [Tulip OEE Dashboard](https://tulip.co/blog/overall-equipment-effectiveness-oee-dashboard/)
- [Parsec 8 Manufacturing Dashboards](https://www.parsec-corp.com/blog/8-manufacturing-dashboards-supercharge-production)
- [dataPARC Control Charts](https://www.dataparc.com/blog/how-to-use-control-charts-to-improve-manufacturing-quality/)
- [Cognex VisionPro Deep Learning](https://www.cognex.com/en/products/machine-vision-software/visionpro-deep-learning)
- [Landing AI Visual Inspection](https://landing.ai/landing-ai-visual-inspection-platform/)
- [Elementary AI Platform](https://www.elementaryml.com/product/platform)
- [ISA-101 HMI Standards](https://www.isa.org/standards-and-publications/isa-standards/isa-101-standards)
- [Rockwell HMI Style Guide](https://literature.rockwellautomation.com/idc/groups/literature/documents/wp/proces-wp023_-en-p.pdf)
- [RealPars High Performance HMI](https://www.realpars.com/blog/high-performance-hmi)
- [TeepTrak Dashboard Design Guide](https://teeptrak.com/en/manufacturing-dashboard-design-guide-2026/)
- [포스코DX PosFrame](https://www.poscodx.com/kor/solution/posFrame)
- [SAIGE PCB 품질관리](https://saige.ai/blog/pcb-quality-ai-inspection/)
- [AHHA Labs 타이어 검사](https://ahha.ai/2024/11/05/tire_anomaly/)
