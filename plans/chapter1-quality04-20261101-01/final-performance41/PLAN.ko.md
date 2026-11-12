# 선택 후보41 최종 성능 관문 준비

2026-11-12. 이 폴더는 **준비 소스**다. 엔진·GPU·측정·사용자 프로필 변경을 실행하지 않았다. 후보41이 실제로 완성되기 전에는 바인딩조차 거부한다. 이전 후보37 helper와 그 WIP는 변경하지 않는다.

## 고정 대상과 보존

대상은 `full41` 증거의 `chapter1-full-candidate-20261112-41` 실행본 하나다. 다른 후보로 자동 대체하지 않는다. 예상 의존175개(40의172개+UI41+초상PNG+출처MD), 성공한 실제 PCK 통합·PCK 감사·최종 보존, 종료0·시간초과없음·launch_error null, 실제 EXE 크기와 SHA256, 루트/스테이지41 해시가 모두 맞아야 한다. 실제 패키지 구조가 다르면 먼저 계약을 조정하고 소스 검토를 받는다. 관문 숫자를 조용히 낮추지 않는다.

실행 직전 `bind`가 세 측정에 공통인 불변 세션을 만든다. 현재 Quality 저장 폴더의 본문과 모든 journal 파일 집합/SHA를 읽어 기록한다. 과거 revision3/장비23개를 현재 사용자에게 강요하지 않는다. 프로필을 복사·복원·삭제하지 않는다. 측정 중 정상 사용자 진행이 생기면 결과는 무효가 되며 이전 진행으로 되돌리지 않는다.

37·38·40은 각 과거 EXE/스테이지/manifest 해시를 검사한다. 현재 루트 조립본이41이라는 이유로 과거37 루트 해시가 달라졌다고 복구하거나 실패를 숨기지 않는다. 과거 원형의 증거는 변경되지 않은 자체 스테이지와 원래 freeze manifest다.41의 원화 출처·상태 문서는 최종 패키지 freeze 전에 확정해야 한다.

## 측정 조건

- 실제 Windows EXE/Forward+·1920×1080·3D scale1·MSAA2·VSync off·FPS cap0·time_scale1.
- 실제 메뉴에서 대기한다. root가 CUA로 창에 초점을 주고 정상 시작 버튼을 누른다. autostart·ignore-focus는 사용하지 않는다.
- 기존 정상 pilot를 사용한다. 장비·HP·XP 지급이나 코어 변경이 없다. 프로필은 `--chapter1-profile-off`로 쓰지 않는다.
- 단조 시계 `Time.get_ticks_usec`로 warmup10초 + sample60초. 준비·종료 PNG/live-readback만 사용하며 측정 중 게임 캡처/녹화/입력 로그/파일 출력은 없다.
- 같은 EXE·observer·현재 프로필 바인딩에서 고정 `run-01`, `run-02`, `run-03`만 사용한다. 성공한 세 개만 골라 조합하지 않는다. 실패 시 원시를 보존하고 원인을 확인한다.
- 각 샘플의 전체 callback 간격을 보존한다. 긴 프레임과 경계 초과를 잘라 내지 않는다. 시퀀스/시간차·process callback 누락·카운터 후퇴·실제 render/simulation 진행·focus·크기·설정·샘플 기간·raw SHA·요약 분위수를 독립 재계산한다.

기준은 각 회차 유효성 및 p95≤16.67ms다. 이 수치는 첫70초의 정상 정책 대표 부하이며 전체 장의 최악 부하·하드웨어 GPU 시간·모든 프레임60FPS를 뜻하지 않는다. 수동 완주·실제 음향 청취·미술 완성의 증거도 아니다.

## 실행 순서 — root의 명시적 실행 GO 후에만

다른 GPU 작업과 사용자 게임이 없어야 한다. 측정 구간에는 다른 에이전트의 엔진/대량 검사와 CUA 스크린샷도 멈춘다. 창을 다른 앱으로 바꾸면 해당 회차는 무효다.

```powershell
python -B plans/chapter1-quality04-20261101-01/final-performance41/run_performance41.py bind --session final01
python -B plans/chapter1-quality04-20261101-01/final-performance41/run_performance41.py run --session final01 --run-id run-01
# MENU 준비 출력 후 root CUA focus + 정상 시작, 종료까지 관찰 입력/캡처 없음
# run-02, run-03도 같은 방식으로 하나씩 실행
python -B plans/chapter1-quality04-20261101-01/final-performance41/run_performance41.py aggregate --session final01 --output three-run-summary.json
```

각 `run`은 소유 PID만 제한 시간 뒤 정리하며 기존 사용자 프로세스를 종료하지 않는다. 모든 파일은 새 경로/exclusive write다. 실패 원시를 덮어쓰지 않는다. `run`/`audit`/`aggregate`는 무효 또는 목표 미달이면 종료1이다. 전체 목표 완료 여부는 원시·결과 범위와 별도로 판단한다.

## 준비 시 확인한 위험과 남은 확인

기존37 helper는 과거13핀과 현재 루트37 freeze를 고정해 새41에 그대로 사용할 수 없었다. 새 helper는41 패키지 계약과 실행 직전 현재 프로필을 분리했다. 기존 CLI가 결과 JSON만 쓰고 무효여도 종료0일 수 있던 점도 fail-closed로 바꿨다. process-frame 누락과 render/simulation 무진행도 원시 감사에서 거부한다.

준비 검사는 Python AST/import·명령 대상·세션/회차 경로 검증까지만 수행했다. `prepare_helpers.py`는 최초 복사 변환 기록이며 이후 직접 보강한 최종 helper가 기준이다. GDScript parser·실제 프로세스·창 focus·정상 pilot의70초 생존·실제 CSV와3회 결과는 아직 확인하지 않았다. 이 준비 문서를 성능 통과로 표시하지 않는다.

## 독립 소스 검토 보강 — 2026-11-12

실제 메뉴에서 **서리창 시작** 버튼을 선택해야 한다. CLI의 primary 인수는 메뉴 선택으로 바뀔 수 있으므로, 관측기는 최초 playing 시점과 종료 시점의 실제 view.seed_/primary 및 growth.snapshot().primary를 읽어 seed90131·서리창을 확인한다. 매 프레임 view의 시드/primary가 같은지도 확인한다. 성장 snapshot은 시작/종료에서만 읽으며 매 프레임 복사하지 않는다. 다른 시작 기술을 누르면 원시는 남고 회차·세션은 무효다. 실패 회차만 골라 교체해 좋은3개를 조합하지 않으며, 원인을 해결한 뒤 새 세션의 고정3개를 다시 수행한다.

런타임 출력 경로에도 session 이름을 포함한다. 새 세션의 run-01은 이전 세션의 run-01 디렉터리를 덮어쓰거나 충돌하지 않는다. 같은 세션/회차 재실행은 계속 거부한다. 독립 검토는 Python 정적·소스 확인이며 GDScript 실제 parser와 측정은 제품41 생성 후 별도다.
