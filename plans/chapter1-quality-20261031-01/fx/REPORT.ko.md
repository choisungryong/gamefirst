# 전투 표현·HUD·음향 개선 구현

2026-10-31. 후보02의 수치 전투는 유지하고, 새 품질 후보의 표현을 개선했다. **이 문서는 작성자의 구현/합성 fixture 결과이며 SACRATA 목표 품질·실제 GPU·실청취 승인이 아니다.**

## 바뀐 화면과 피드백

- 화염탄은 붉은 외피/주황 꼬리/백열 중심을 갖고, 진화한 탄은 발사 당시 radius로 더 큰 형태를 사용한다. 적 탄은 작은 녹슨 붉은 바늘로 구별한다. 현재 장비나 성장 상태로 이미 날아가는 탄을 다시 계산하지 않는다.
- 폭발은 paid radius의 바닥 열기·불규칙 충격과 짧은 입체 화염/연기를 쓴다. 기존의 항상 보이는 흰 원 둘레를 없앴다. 냉기는 각진 창과 파쇄, 번개는 굵기를 가진 지그재그 리본과 짧은 가지를 쓴다.
- 일반 원거리 전조는 낮은 알파의 녹슨 붉은 면과 준비 시간에 따른 가장자리, 정예는 더 강한 우선순위를 쓴다. 실제 core capsule을 포함하는 보수적 fan hull은 유지한다. 겹침이 최종적으로 읽히는지는 GPU 장면 검수가 필요하다.
- 3개의 ImmediateMesh 객체를 재사용한다. 그림자 없는 MultiMesh 효과, 960개 파편,96개 stroke,48개 바닥 충격/48개 화염 plume, 한 consume 호출당8개 새 충격을 상한으로 사용한다. 원래 shadow513/projectile384/orb400/ground loot32의 소비 경계도 유지한다. VFX 누락/LOD가 게임 판정을 바꾸지 않는다.
- 약한 카메라 반응은 world.kick_camera로 한14tick마다 최대1회 요청한다. HUD의 '화면 흔들림'을 끌 수 있다. 플레이어 피해와 진화 충격만 요청하고, 개별 hit 전부에 흔들림을 넣지 않았다.
- HUD는 철/황동 계열, 높이를 줄인 생명력/XP와 원소별3기호·랭크로 정리했다. 큰 제목은 바탕 계열, 실시간 텍스트는 맑은 고딕이다. 기존 단축키·중첩 modal·같은tick 종료HP 갱신과 숨긴 skills 요약 Label을 유지했다.
- 드롭은 실제 common/magic/rare에 따라 색이 다르며, 이름은8m 안에서만 보인다. 물체 빛은 남겨 먼 드롭도 찾을 수 있다.

## 음향의 실제 출처와 처리

공식 [Kenney Impact Sounds](https://kenney.nl/assets/impact-sounds), [RPG Audio](https://kenney.nl/assets/rpg-audio), [Sci-fi Sounds](https://kenney.nl/assets/sci-fi-sounds)의 CC0 자료를 사용했다. 각 공식 페이지와 번들 License.txt를 확인했고, 원본 ZIP·페이지·해시는 `C:/Project/game-research/audio-sources/quality03-20261031-01/` 및 이 폴더의 AUDIO-SOURCE/AUDIO-MORE-SOURCES.json에 있다. 기존 정적 다운로드 링크의 첫 응답은 ZIP이 아닌 HTML이었고 그대로 보존했다. 이후 공식 페이지의 'Continue without donating'가 쓰는 공개 서명 링크 절차로 유효한 ZIP을 받았다. 계정·결제·보호 회피는 없었다.

20개 mono48kHz PCM16 WAV(19가지 cue variant+ambient loop)를 새로 구성했다. 선택한 충격·유리·나무·cloth·동전·thruster/crunch 등의 레이어, 짧은 fade, DC 제거, rate 변환과 정규화를 사용한다. 단순 sine음을 완성 음향이라고 바꾸어 부르지 않는다. 각 source/layer/출력 SHA·RMS·peak는 chapter1/art/quality03_audio/AUDIO-LEDGER.json에 있다. 원본 소리가 실제 녹음인지 합성인지 별도 보증하지 않으며, ambience도 설계한 drone 후보다.

각 cue peak≤.68, clipping sample0. 새 combat_audio.gd는13개 voice(ambient1+one-shot12), cue별 cooldown, 중요 cue용2개 예비 voice를 사용한다. 최대 master1에서 모든 one-shot의 개별 gain≤.11이므로 단순 최악 위상합도 .68×12×.11 + .22×.025 = .9031 이하다. 실제 버스/동영상의 loudness·손맛은 파형만으로 승인할 수 없다. 기존 presentation/expedition_audio.gd와 기존10WAV는 바꾸지 않았다.

AudioStreamPlayer/AudioStreamWAV 및 shader API는 [Godot4.5 공식 문서](https://docs.godotengine.org/en/4.5/classes/class_audiostreamwav.html), [spatial shader reference](https://docs.godotengine.org/en/4.5/tutorials/shaders/shader_reference/spatial_shader.html)의 형식을 따른다. 소스 미리보기의 unimported WAV에는 문서화된 load_from_file을 사용하고 fallback 목록을 기록한다. 내보낸 패키지에서는 가져온 resource로 fallback0을 검증해야 한다.

## 실행한 검증

`fixture-positive-execution.json`: 실제38검사/exit0, 실패 없음. `fixture-negative-execution.json`: 의도 실패 포함39검사/exit1. `scene-smoke-execution.json`: headless 실제2초 장면 exit0, stderr 및 SCRIPT ERROR/ERROR 없음. 세 실행의 전체 argv/stdout/stderr/actual exit는 원시에 있다.

합성 fixture는 effect cap·lifetime, FX 뒤 전체 core snapshot 불변,13voice와19variant, cue cooldown·mute·pause·정지 UI음, 같은tick 최종HP0·retry120·3skill slot을 확인한다. 합성 event/HP fixture를 일반 플레이로 표시하지 않는다. GPU가 없는 headless 장면은 shader의 실제 렌더 결과나 음향 청취 검사가 아니다.

초기 소스 parse 실행은 아직 가져오지 않은 새 WAV에서 loader 오류를 기록했다(명령은 exit0이었지만 오류가 있어 유효 통과가 아니다). 이어 문서화된 source fallback을 넣었다. 그 다음 engine --quit-after3 frame 직접 종료는 ObjectDB warning을 남겼다. 명시적2초 QA 종료와 정리 지연을 쓰는 최종 실행은 깨끗했다. 앞선 tool 결과는 실패 이력으로 남아 있으며 누수0을 주장하지 않는다.

`source-manifest.json`과 source 사본은 작성자 소유33 runtime 파일을 고정한다. `FREEZE.json`은 current/snapshot 일치 및 core03 nine/baseline51의 불변을 확인한다. GPU compile·동일 카메라의 전후 장면·연속 movie·실청취·1440/1080 HUD·독립 검토·패키지 감사는 다음 검수다. 커밋·업로드·원작 자산 복사는 수행하지 않았다.
