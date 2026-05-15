# Red Dead Redemption 2 크래시 트러블슈팅 추적

> 사용자: wonjeonghwan@gvm.kr
> PC: AMD Ryzen 7 3800X (Zen 2) / 32 GB RAM / RTX 3060 Ti / Windows 10 Home 22H2 (Build 19045)
> 작성 시작: 2026-05-16 02:15

## 증상

- Steam에서 RDR2 실행 시 다이얼로그: "오류 — 게임을 실행할 수 없습니다. 게임을 다시 설치하십시오."
- 사용자는 **이 PC에서 한 번도 정상 실행에 성공한 적 없음**
- 첫 시도일: 2026-04-01 (Rockstar Launcher crash 보고)
- 게임 여러 번 재설치 시도했지만 모두 실패

## 진단 (확정)

`Launcher.exe` (Rockstar Games Launcher) 코드 오프셋 `+0x228B41`에서 **STATUS_STACK_BUFFER_OVERRUN (0xC0000409 / WER BEX64)** 으로 결정적 충돌. Launcher가 이를 `0xC0000005`로 catch 후 비정상 종료 → Steam이 자식 프로세스 실패 다이얼로그 표시.

- 발생 지점: `[titlemanager] Downloading title list (SCS)...` 직후 (로그인 ~80 ms 이내)
- 호출자: `Launcher_base + 0x400B1E9D`의 힙 메모리 (CEF의 V8 JavaScript JIT 영역)
- Hash: 0xE6517D1E (Steam 경유) / 0x68C77D1E (직접 실행) — 동일 코드 경로
- Launcher 버전: 1.0.106.2879

## 결론: 문제 위치

**Rockstar Launcher 코드(내부)의 잠재적 버그 + 이 PC 환경(외부)의 무언가가 인젝트되어 트리거.** 게임 파일 자체는 정상.

---

## 시도한 것 (모두 실패 — 크래시 동일)

| 시도 | 결과 | 비고 |
|---|---|---|
| Rockstar Launcher 사용자 프로필 데이터 백업/재생성 | ❌ | `Documents\Rockstar Games\Launcher\Profiles\` 등 .bak로 이동 |
| 사용자 레벨 캐시 파일 정리 | ❌ | `settings_user.dat`, `launcher_online_config.dat` 등 백업 |
| Discord 모든 프로세스 종료 | ❌ | 6개 프로세스 종료해도 동일 |
| Steam 인게임 오버레이 — per-app 비활성화 | ❌ | `OverlayAppEnable "0"` 추가, Steam이 인식했지만 효과 없음 |
| Steam 오버레이 DLL 이름 변경 | ❌ | Steam이 즉시 자동 복구 |
| Steam 우회 → Launcher 직접 실행 | ❌ | 같은 오프셋에서 크래시 (Steam 무관) |
| Riot Vanguard (vgk.sys) 완전 제거 | ❌ | 커널 드라이버 언로드 + 폴더 삭제까지 완료. **재부팅 없이도 즉시 적용됨**. 그래도 크래시 동일 |
| Social Club CEF 브라우저 캐시 정리 | ❌ | `Documents\Rockstar Games\Social Club\` 전체 백업, 재생성 |
| Win8 호환성 모드 적용 | ❌ | Launcher가 "Windows 7/8 지원 종료" 다이얼로그로 실행 거부 |
| PCA(Program Compatibility Assistant) Store 정리 | ❌ | HKCU의 RDR2/Launcher 항목 모두 제거 |
| **Defender 폴더 예외 (RDR2 + Rockstar Games 폴더)** | ❌ | 사용자가 Windows Security UI로 추가. 그래도 `MpOav.dll`은 여전히 Launcher 프로세스에 인젝트됨 — 폴더 예외는 in-process 스캐닝 모듈 인젝션을 막지 못함을 확인 |

## 분석으로 원인 후보에서 제외된 것

- ✅ 게임 파일 손상 — 119.47 GiB = 128.28 GB, Steam manifest와 일치
- ✅ Discord overlay
- ✅ Steam overlay (gameoverlayrenderer64.dll)
- ✅ Riot Vanguard
- ✅ 호환성 모드 강제 적용
- ✅ TouchEn (JRSUKD25.SYS) — DEMAND_START이고 현재 비활성 (그래도 사용자가 인터넷뱅킹 사용하면 자동 로드됨)
- ✅ AppInit_DLLs — 비어있음
- ✅ Vulkan/D3D12 드라이버 — NVIDIA RTX 3060 Ti, RDR2 정상 지원

## 시도하지 않은 것 (관리자 권한 필요)

| 시도 | 위험도 | 예상 효과 | 비고 |
|---|---|---|---|
| **Defender 프로세스 예외 (Launcher.exe / PlayRDR2.exe / RDR2.exe)** | 낮음 | **매우 높음** | 폴더 예외가 실패한 후의 다음 단계. 프로세스 예외는 Defender의 in-process 스캐닝 모듈(`MpOav.dll`) 인젝션을 막을 가능성이 있음 |
| **Defender 실시간 보호 일시 OFF로 검증** | 낮음 (몇 분) | **결정적** | Defender가 원인인지 한 번에 확인. 작동하면 원인 확정 → 영구 예외 방법 찾기. 작동 안하면 Defender 아님 |
| Hyper-V/WSL 비활성화 + 재부팅 | 중간 | 중간 | VBS가 현재 running. V8 JIT 호환성 가설. WSL 사용 못함 |
| Windows 안전 모드(네트워킹) 부팅 | 낮음 | 진단용 — 결정적 | 외부/내부 판별 결정타 |
| Rockstar 공식 사이트 standalone 설치 | 낮음 | 중간 | Steam이 깐 버전이 아닌 최신 launcher 직접 설치 |
| Windows 재설치 (in-place repair) | 높음 | 매우 높음 | 최후의 수단. 앱은 유지, 시스템 파일만 리프레시 |
| Windows 클린 설치 | 최고 | 거의 확실히 해결 | 정말 마지막 수단 |

## 다음 권장 순서

1. ✅ ~~Defender **폴더** 예외 추가~~ — 실패 확인 (MpOav.dll 여전히 인젝트됨)
2. ⏭ **Defender 실시간 보호 일시 OFF로 검증** (5분, 결정적 검증)
3. ⏭ 또는 **Defender 프로세스 예외 추가** (5분)
4. ⏭ 위가 실패하면 Hyper-V/WSL 비활성화 + 재부팅 (10분)
5. ⏭ 위가 실패하면 안전 모드(네트워킹)에서 게임 실행 시도 — 외부/내부 결정타
6. ⏭ 그래도 안 되면 in-place repair install
7. ⏭ 마지막 수단: Windows 클린 설치

## 세션 중 발생한 시스템 변경 사항 (이 추적 문서로 관리)

| 항목 | 상태 | 복원 방법 |
|---|---|---|
| `C:\Users\wonje\Documents\Rockstar Games\Launcher\Profiles\` → `Profiles.bak-20260516-step1` | 백업됨 | 게임 작동 시 .bak 폴더 삭제 가능 |
| `AppData\Local\Rockstar Games\Launcher\*.dat` → `*.dat.bak-20260516-step1` | 백업됨 | 위와 동일 |
| Steam `localconfig.vdf`에 `OverlayAppEnable "0"` 추가 (RDR2만) | 적용됨 | Steam UI에서 게임 속성 > 인게임에서 재활성화 |
| `localconfig.vdf.bak-20260516` 백업 | 존재 | 게임 작동 시 삭제 가능 |
| Riot Vanguard | **완전 제거됨** | Valorant 다시 실행 시 자동 재설치 |
| HKCU Layers 호환성 모드 | 추가 후 제거 완료 | — |
| HKCU PCA Store Rockstar 항목 | 제거 완료 | Windows가 다음 크래시 시 재생성 가능 |
| `Social Club.bak-step2-20260516` | 복원 완료 | — |

## 크래시 시그니처 (참고용)

```
Exception: 0xC0000005 (실제로는 WER 0xC0000409 BEX64 stack buffer overrun)
[ 0] Launcher.exe + 0x228B41
[ 1] ntdll.dll (RtlReportFatalFailure 계열)
[ 2] ntdll.dll
[ 3] ntdll.dll
[ 4] Launcher_base + 0x400B1E9D (V8 JIT heap, 모듈 외부)
```

WER: "Faulting application name: bad_module_info, version: 0.0.0.0 | Faulting module name: unknown, ..."

발생 패턴: 로그인 성공 → `Went Online` → `Downloading title list (SCS)` → 100ms 이내 크래시
