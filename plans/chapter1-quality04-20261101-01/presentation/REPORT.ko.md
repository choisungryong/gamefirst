# 품질04 동작·타격·가독성 보완

2026-11-01, Asia/Seoul. 품질03의 기존 아트·전투 소리를 유지하면서 표현 코드4개를 수정했다. **대표90초 품질 관문의 기술 후보이며 SACRATA 최종 품질, 실청취, 정식 성능,5–8분 전체1장 완성 승인이 아니다.**

- `cloister_actors.gd`: 기존 실제60Hz core step 뒤 호출되는 consume에서 이동의 직전/현재 좌표를 캡처하고, render sync에서 엔진의 physics interpolation fraction으로 실제 Node3D transform을 보간한다. 렌더가30Hz여도 중간 core tick을 놓쳐 보행이 멎지 않는다. 위치는 최대1tick 지연되며 hitbox는 바꾸지 않는다. pause는 endpoint에 고정하고 resume의 역방향 미끄러짐·재도전/teleport의 긴 이동을 막는다.
- 기존4프레임 보행의 위상을 이동거리로 구동하고 방향 전환/짧은 시전 후에도 보존한다. 새8프레임·새 다리 접촉·리깅·아트 보간을 만들었다고 주장하지 않는다. 시전 사건은 이미 발사된 시점이므로4방향 atlas의 release2→recovery3을 바로 표시한다. 발사 후 ready/anticipation을 재생하던 문제를 고쳤다.44개 영웅 frame의 발 기준점과 physical scale은 원본 JSON을 따른다.
- 영웅보다 카메라 쪽에 있는 살아 있는 적의 **현재 표시 frame을 카메라로 투영한 사각형**이 영웅 frame과 겹칠 때만 별도의 얇은 따뜻한 alpha rim1개를 켠다. 영웅 본체 depth test/default priority는 유지한다. 뒤쪽 적·사체·겹치지 않는 적은 켜지 않는다. 이는 보수적인 frame 사각형 검사이며 per-pixel alpha/depth 가림 판정은 아니다. 겹칠 때 rim 전체 외곽을 보여주는 방법이다.
- `cloister_effects.gd`: 지급된 hit 사건에0.10초의 작은 원소별 선형 accent를 추가하고 consume당12개/strokes96/debris960/impact48 상한을 유지한다. 일반 hit마다 카메라를 흔들지 않으며 기존 중요 사건의14tick 제한을 유지한다. 접지 그림자는 렌더된 actor 좌표를 따른다. 기존 불꽃 shader/주황 사각 경계 수정은 변경하지 않았다.
- `combat_audio.gd`: voice별 cue gain을 저장해 활성 재생 중 mute 해제/master 변경 후에도 step.38/fire.8 등 개별 gain을 유지한다. ambience.025/일반.11 배율·13voice·중요 cue 예비2칸을 유지한다. 품질03 코드검토P3를 수정했다.

## 실제 검사

`positive-08/execution.json`: **278checks, actual exit0, failures[], stderr0bytes**. `negative-09/execution.json`: **279checks, 의도적 검증 실패1개만, actual exit1, stderr0bytes**. 각 raw stdout/stderr·실행 명령·당시 contract 사본·제품4파일 SHA256을 같은 폴더에 보존했다. 재실행 collector는 기존 출력 폴더가 있으면 실패하므로 과거 증거를 덮지 않는다.

실제 `chapter1/Chapter1.tscn`을 올린 headless fixture에서 분수0/.25/.5/.75/1의 실제 transform·30render/60core 표본·거리 위상·4방향 전환·release/recovery·JSON 발 기준점44개·앞/뒤/사체 overlap·기존 본체 depth·실제 pause/resume/retry 명령·효과/음향 pool 상한·active cue gain/mute/master/pause를 검사했다. 실제 core90step 뒤 consume/presentation 호출 전후에 **모든 script 변수, 중첩 growth/catalog, private cooldown/context/events, 각 RNG seed/state**를 재귀 대조했다. public snapshot만 비교한 검사가 아니다.

일부 좌표·시전·겹침·대량 사건은 경계조건을 만든 합성 fixture다. 일반 플레이 결과, OS 직접 조작, GPU 그림 품질, 전경 성능, 실제 소리 청취 증거로 확대하지 않는다. headless dummy renderer의 MultiMesh transform getter가0을 반환했으므로 그림자 접지의 시각 검사는 GPU 할당 후 별도로 필요하다.

## 보존·실패 기록

`freeze-02/manifest.json`과 `source/`가 최종4제품의 해시/바이트 사본이다. `before-audit.json`의 기존3사본은 before-manifest와 모두 일치한다. `original-png-pins.json`은 전역 백업에 핀한 원본15PNG가 모두 같음을 확인한다. 이 담당자는 core/world/HUD/glue를 수정하지 않았으며 다른 담당자의 품질04 변경을 품질03 core 바이트 불변으로 표시하지 않는다.

초기 인수 때 effects의 hit-stroke 블록이 enemy telegraph 분기에 잘못 들어가 미정의 변수를 참조하던 중단 상태를 복구했다. `initial-failure-01` actual1은 fixture의 float 정밀도·기본24적·빈 voice pause 속성 가정 등을 수정하기 전 결과다. `positive-03` actual1은 dummy MultiMesh transform 읽기 한계를 드러냈으며 통과로 바꾸어 쓰지 않았다. `positive-04`/`verbose-05`의 종료 ObjectDB/resource 경고는 보존했다. verbose 원시에서 AudioStreamWAV/playback 대기 참조를 확인했고, 동일 turn 안에 여러 재생/중지를 몰아 넣는 fixture 종료 전에 audio server가 대기 명령을 소비할 시간을 준 후 `positive-06`, `negative-07`, 최종08/09는 stderr0이다. 누수0의 장시간 증거는 아니다.

한 차례 원본 프로젝트에서 `--headless --editor --import --quit`을 실행해 actual0으로 끝났지만 과거 evidence PNG까지 스캔한 것은 부적절했다. full raw 파일 로그를 설정하지 않아 tool의 일부 출력만 있고 첫 출력은 잘렸다. `freeze-02/import-incident.json`은 해당 시각 주변에 생성/수정된 후보165개 .import/.uid를 경로/시각/해시로 기록하고 flat 사본을 보존한다. 사전 sidecar 목록이 없어 모두 그 명령이 생성했다고 확정하지 않으며 .godot 캐시 전체 목록도 아니다. 원본/sidecar를 삭제하지 않았고 전체 폴더 inventory 불변을 주장하지 않는다. 후속 검사는 직접 headless script만 사용했다. `freeze-01`은 감사 스크립트가 방금 만든 사본을 다시 순회해 Windows 경로 길이 한계로 실패한 부분 사본이며, 원본은 건드리지 않았다. 수정 후02에서 동결/15PNG 대조를 완료했다.

## 확인한 공식 API

- [Engine.get_physics_interpolation_fraction](https://docs.godotengine.org/en/4.5/classes/class_engine.html#class-engine-method-get-physics-interpolation-fraction): render 시점의 현재 physics tick 분수.
- [AnimatedSprite3D.set_frame_and_progress](https://docs.godotengine.org/en/4.5/classes/class_animatedsprite3d.html#class-animatedsprite3d-method-set-frame-and-progress): 방향 animation 전환 후 frame/진행률 지정.
- [SpriteBase3D](https://docs.godotengine.org/en/4.5/classes/class_spritebase3d.html): pixel_size/offset/billboard/no_depth_test와 기본값.
- [Camera3D.unproject_position](https://docs.godotengine.org/en/4.5/classes/class_camera3d.html#class-camera3d-method-unproject-position): 현재 frame의 camera-space 투영.
- [AudioStreamPlayer](https://docs.godotengine.org/en/4.5/classes/class_audiostreamplayer.html): playing/stream_paused/volume_db/play/stop.
- [Spatial shader](https://docs.godotengine.org/en/4.5/tutorials/shaders/shader_reference/spatial_shader.html), [AtlasTexture](https://docs.godotengine.org/en/4.5/classes/class_atlastexture.html): 별도 outline billboard·alpha·영역 UV.

GPU/동영상/정식 성능/실청취는 이 담당자에게 할당되지 않아 실행하지 않았다. 보행 아트의 낮은4프레임·기존 south-only hurt/death 행동·발 접촉/생체역학 품질·최종 군중 가독성은 열린 품질 관문이다.
