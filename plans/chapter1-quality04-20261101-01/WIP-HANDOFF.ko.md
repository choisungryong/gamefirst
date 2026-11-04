# 최신 전체1장 후보09 진행

`full09/STATUS.ko.md`와 루트 HANDOFF 최신 머리말을 우선한다. 아래 품질04 기록은 보존된 이전 상태다. 전체1장 기능분기/후보07–09/릴리스 결함·수정/새 도감/실제GPU6분2초 완료는 full09에 있다. 최종목표는 active다.

---

# 2026-11-01 품질04 계속 작업

목표는 SACRATA 지향 전투/아트/타격과 디아블로식 장비·성장이 결합된 실제5–8분짜리1장이다. 대표90초나 기술검사를 목표 완료로 바꾸지 않는다. 현재 전체1장·보스·보상저장은 미완료다.

보조 agents는 사용량 제한으로 중단되어 root가 직접 수정·검증을 이어갔다. 원래 do 스킬의 위임 흐름은 해당 도구가 가용하지 않아 사용하지 못한다. 새로운 agent를 반복 생성하지 않는다. 직전 goal turn은 실제 소스·검증·빌드 진전이 있으므로 no-progress가 아니다.

## 보존 및 현재 실행

- 전 작업 백업77파일: `C:/Project/game-research/implementation-backups/chapter1-quality04-before-20261101-01/manifest.json`. root 수정 전 현재72runtime+HANDOFF 백업73: `C:/Project/game-research/implementation-backups/chapter1-quality04-root-resume-before-20261101-01/manifest.json`.
- 기존03/02/phase7 EXE·사용자 equipment/progress·이전증거는 보존한다. 새04/05/06도 덮지 않는다. 소스03는 역사사본으로 유지하고 현재코어는 후속 규칙이므로 bitwise03 일치를 주장하지 않는다.
- 현재 후보06: `builds/chapter1/chapter1-c2-candidate-20261101-06/AshenCloister-Chapter1.exe`, SHA `dd59675a89e88b8a02cc8b3e0539f5129d68d6afe2d14c4390c73bb0ac101fbe`; runtime72/stage74/PCK125, package `packaging/build06/`. 후보04는 `134304f1d2927d5a6af8e1d3f74960256bed5966badab7455a1d892123383dab`,05는`a5d2c658ae9e06c710e036c1965cc340fdfde5acce2a32d41e5a2b34dbb272f4`. 04–06의 전투·표현은 같고 선택적인 QA probe 수정이 다르다.

## 완료 변경과 근거

- 실제 적 접근에 grid-local32 이웃 압력·영웅 여유·closest/UID 공격자리 우선권을 도입했다. 모서리에서 영구 공격교착이 생긴 최초 red를 보존하고 수정했다. 240tick 합성 겹침 적분은 약96–98% 감소했으나 잔여 겹침은 있다. core04/ 계약/동결과 verification-01/를 확인한다.
- 배우는 고정tick 위치를 consume에서 기록하고 렌더에서 보간한다. 기존4프레임 보행의 거리 위상·방향전환·발사/회복 포즈를 연결하고 실제 투영겹침 때만 얇은 영웅 outline을 켠다. 작은 명중 accent와 현재 voice별 gain의 mute/master 복원을 구현했다. presentation/freeze-02/ 4파일,278정상0/279의도1.
- root가 기존 `_cleanup`의25m 밖 windup/dash/recover/frozen 순간 재배치를 발견·수정했다. 자유 move+not frozen만 재배치한다. root-resume-01/anchor-before actual1(4실패)→after20체크0→intentional1. 재검사 semantic75/0,crowd48/0,4모서리 독립32/0. 테스트 old output은 덮지 않는다.
- 기존6 normal driver는5승1냉기71패배(39.18s/30kill/Lv3)다. 기존03의65s/237kill보다 악화된 패배를 보존했다. 원인은 초기XP 소실이 아니라 자동 회피가 x19 벽으로 계속 미는 경우다. 동일 규칙에서 별도로 명명한 primary-first-wall-aware 일반입력은 냉기71 79.1167s/648kill/Lv12 승리. 기존 실패를 대체하거나 전승/밸런스 승인으로 표시하지 않는다. root-resume-01/wall-results.json.
- 후보04 실제1920window GPU90s preview는82.5667s/867kill/Lv12/화염4진화·냉기3·번개3 승리, actual0,18PNG. `root-resume-01/gpu-preview-01/`. root가 frame005의 실제 간격/outline을 확인했다. 아트/동작 최종 승인 아니다.

## 성능 probe 진행과 남은 것

- raw Time.get_ticks_usec,10warm+60sample, per-frame focus/size/mode/count,180000행 상한 명시 invalid, 기본off. 메뉴는 첫 playing까지 warm을 시작하지 않는다. root가 먼저 메뉴를 focus하고 Start를 클릭한다. probe 종료 후 audio reset+.15sec clean quit은 명시 QA flag일 때만이다.
- 원 runner의 packaged 경로 불일치는 `measurement/run_probe_packaged.py`에서 EXE qa-probe 경로로 수정하고 raw를 증거 폴더로 복사한다. helper들/실패 원본은 남긴다.
- 후보04 formal01은 export OS.get_cmdline_args가[]라 CLI-token guard 거부/0행. 후보05 formal05-01은 실제 OS.delta_smoothing이 true로 남아 거부/0행. 후보06 probe는 문서화된 OS.delta_smoothing=false를 QA 프로세스에만 설정하고 sample 종료 뒤 원값으로 복구한다. 원시 시간은 smoothing과 무관한 단조 wall clock이다. pure23checks0.
- 후보06 formal06-01은70초 실제 수집/33252measured intervals/60000533us/p95 2.827ms지만 **무효**다. Window1920×1080, 실제 render texture2304×1296으로 엄격한1920×1080 guard와 불일치했다. unfocused0·오류없음·상한미도달. 실제 더 큰 렌더의 참고자료이지 정식1080p3회 통과로 표시하지 않는다. 같은 실패를 이유없이 반복하지 않는다. `measurement/runs/formal06-01/`.
- 앞으로 성능 크기를 정확히 정의하거나 최종1장 빌드에서 최소1080p 내부렌더와 실제값을 투명하게 검증한다. 대량180합성/고정60FPS/누수0을 주장하지 않는다. 실청취도 미완료다.

## 아트와 부작용

- imagegen 남쪽8보행 시도03도 같은 선행발 반복이라 거절했다. `chapter1/art/quality05/attempts/hero_south_run03_rejected.png`(SHA2db0e18c4e52fdd416a92777f18220f025bd97e897c762e546872f44e9521c0e), JSON에 exact prompt/built-in/원본을 남긴다. PNG 픽셀은 수정하지 않았다. 런타임 미채택.
- 실제 rig/animation의 대안을 연구 중이다. 공개 Flare HD art source `https://github.com/flareteam/flare-game-art-src`, tree SHA8830c68b420b631e09a459e5b0bf87c0e068a558, metadata만 `C:/Project/game-research/art-sources/flare-hd-20261101-01/`에 보존했다. 라이선스/credits/아트 후보를 확인한 후 시각·모션이 나으면 채택 여부를 결정한다. 원작D2/SACRATA 자산은 복사하지 않는다.
- 한 agent의 실수로 root-project headless editor import가165개 timestamp .import/.uid 후보를 만들거나 갱신했다. full raw log 없음, 후보사본/JSON과 원본15PNG 일치 기록은 presentation/freeze-02/import-incident.json. 삭제나 과거 metadata 복원 입증을 하지 않았다. 이후 모든 import는 원본70+extras만 복사한 외부 stage에서만 한다.
- CUA Windows 앱 제어는 동작한다. IAB browser2 기존/소유 tab의 제어가 `browser.user is unavailable`로 실패한다. user tab1은 건드리지 않았다. 소유 임시YouTube tab3는 close가 실패해 남았을 수 있고 현재재생/정지는 확인하지 못했다. 백엔드 우회/사용자브라우저 종료는 하지 않는다.

다음은 실제 프레임040/060의 군중·시전·outline 검토, rig 기반 보행 후보의 실제 표시/라이선스 검토, C2의 아트·음향 품질을 끌어올리며 전체1장 제작 계약을 이어가는 것이다. HANDOFF 루트의 기존03 본문은 현재까지 보존했고 이 WIP가 후속 상태다. 목표는 active이며 전체 완성은 아니다.
