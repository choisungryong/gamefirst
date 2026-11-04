# Chapter1 C2 실행 후보01

2026-10-31. 별도 실행본 제작 및 패키지 실행 검증을 완료했다. **약90초 대표 전투 구간이며 5–8분 첫 장 전체나 최종 품질 완료는 아니다.**

- 실행: `builds/chapter1/chapter1-c2-candidate-20261031-01/AshenCloister-Chapter1.exe`
- EXE: 109674608bytes, SHA256 `fc9e41da23af5ae004204bb3fb12f63d9c7acfc34adbf9e43d00e71d11be027d`.
- 코어03 동결9개와 현재 원본이 일치한다. source42개만 외부 staging으로 복사했고 PCK78개 실제 checksum·동적 로딩 자원·제외 경로 감사를 통과했다. 이전 진행 메시지의46개는 예상 수량이었으며 **실제 수량은42개**다.
- Godot import/export actualexit0. import/export 로그의 ERROR/WARNING/SCRIPT 검색 결과는 없다. `pck-audit.json`, `build.json`, 원본/staging manifests에 연결했다.
- 실제 EXE의1920×1080/Forward+/RTX2070SUPER 실행 actualexit0. 세 기술 실제 시전/명중·Ember 진화·장비9개 회수·4슬롯 장착·정예 실제 사망, 78.15초/813처치/최대59적을 기록했다. READY의5역할은 각각4방향+cast/hit/death가 있으며 PNG raw fallback은0이다.
- 실제 p95는20ms/4522표본이다. 동기PNG와 QA driver가 있는 한 번의 실행이므로 정식 GPU/품질 합격으로 삼지 않는다. 목표16.67ms는 미달 상태다.
- 코어03의6정상 사례는5승과 냉기 seed71의64.9초 패배를 보존한다. 기능75검사 통과와 정상6사례 전체exit1을 분리한다. 이 패키지 단일 승리로 해당 패배를 지우지 않는다.
- 원본 source51·core03pin9·이번runtime42 불일치0, 기존 phase7 EXE와 사용자 equipment/progress save2 해시는 시작 핀과 일치한다. `package-preservation.json`은 현재 비교이며 미핀된 과거 증거 전체의 불변을 입증하지 않는다.

정상 메뉴는 별도 PID13512로 열었고 부모가 단독 UI 검수를 맡았다. autostart/pilot/focus 무시 플래그가 없다. 실제 native 종료 결과는 이 보고서 작성 시 대기 중이며 `native-menu-launch.json`/추후 `native-menu-exit.json` 및 부모 관찰을 따른다. 이 담당자는 Windows UI 입력을 하지 않았다.

새 추가물: `run_packaged_pilot.py`, `verify_packaged_log.py`, `check_package_preservation.py`, `run_native_menu.py` 및 실제 로그/JSON/PNG·세 검토 문서. 런타임 구현 소스나 기존 증거를 수정하지 않았고 commit/upload는 하지 않았다.
