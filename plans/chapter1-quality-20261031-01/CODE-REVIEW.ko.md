# 후보03 독립 코드 검토

2026-11-01, Asia/Seoul. 제품 파일을 수정하지 않고 표현 계층·셰이더·패키지 명세를 읽었다. 검토 기준은 `package03/FINAL-SOURCE-FREEZE.json`의 현재 원본, `fx/v02/source-manifest.json`, `world/verification02/source-manifest.json`이다. 기능 검사와 별도로 작성한 소스 검토이며 GPU 성능·청취·재미·SACRATA 품질 승인이 아니다.

## 발견 사항

**P3 — 음소거 해제/볼륨 변경 시 재생 중 cue의 개별 gain이 사라진다.** `chapter1/presentation/combat_audio.gd:67`은 GAINS[cue]를 적용하지만 `:88`의 apply_volume은 모든 one-shot에 master×.11을 다시 쓴다(`:93`). 예를 들어 이미 재생 중인 step의 계수 .38이1로 바뀌어 음량이 약2.63배가 될 수 있다. 새로 시작하는 cue는 원래 gain으로 돌아온다. 전체 최악 peak 상한은 유지되므로 clipping 또는 코어 손상 문제는 아니다. 후속 수정에서는 voice별 현재 gain을 보존하고 mute/master 적용 시 함께 곱해야 한다. 후보03 실행 파일과 동결 원본은 이 검토에서 바꾸지 않았다.

현 단계 내보내기를 막는 P0–P2 소스 결함은 찾지 못했다. 이것은 결함 부재의 증명이나 제품 품질 승인이 아니다.

## 검토한 경계

- `cloister_effects.gd:98,108–132,236–268,293–304`: event seq 중복 억제, 파편960/stroke96/impact48, consume당8개 새 impact, 수명 정리와 pause 상태의 수명 보존을 확인했다. 투사체384/orb400/그림자513과 바닥 아이템32의 코어 경계를 소비한다. `sync`의 temporary 배열·convex_hull 생성(`:199–210`)은 상한이 있지만 프레임 비용은 별도 실측이 필요하다.
- `cloister_effects.gd:164–174`: 표현이 현재 장비/랭크로 비행 중 탄의 유료 계산 값을 재구성하지 않고, 발사된 projectile의 radius/direction을 사용한다. 피해 계산을 쓰지 않는다.
- `cloister_world_quality03.gd:130–164,229–248`: 런 RNG와 별도의 고정 장식 RNG,620개 낮은 식생, 공유 아틀라스2표면, bounded camera trauma와 reduced-motion을 확인했다. 장식은 충돌체가 아니며 높은 소품 발은 플레이 사각형 밖에 있다. 620개의 실제 알파 덮임률/최종 겹침 수는 검사하지 않았다.
- `cloister_hud.gd:86–96`: 기술명 최소 폭과 고정된2줄을 사용한다. modal/장비/성장은 명시적 signal로 코어에 요청한다. headless158 검사와 실제 GPU 표본은 다른 근거로 취급한다.
- `chapter_view.gd:77–85,278–289`: QA 쓰기는 단순화된 경로의 명시적 새 증거 폴더/실행본 qa-captures 하위만 허용하고 기존 파일을 덮지 않는다. 새 C2 런은 사용자 equipment/progress 저장을 읽거나 쓰지 않는다. 이 변경에서 네트워크 전송·프로세스 실행·보호자산 추출 경로는 없다.
- `combat_audio.gd:25–36,53–72`:13 voice와2개 중요 cue 예비, cue별 cooldown/variant, pause UI cue 경계를 확인했다. WAV20개의 CC0 출처와 처리 장부는 패키지에 포함되며 음원 전체를 직접 청취한 결과로 바꾸어 부르지 않는다.
- `cloister_actors.gd:189–213,235–272`: 방향별 시전과 짧은 cosmetic recoil은 actor 노드만 바꾼다. 코어 위치/피해에는 쓰지 않는다. 기존4프레임 이동을 유지하며 실패한8프레임 달리기 생성물을 채택하지 않았다.

정식1080p 성능, 네이티브 장시간 조작, 소리의 실제 청취, 밀집 적 가독성은 열린 검수다. root는 preview03에서 이전 대비 바닥/폐허/식생 개선과 HUD/불꽃 경계 수정을 확인했으며 비교 후보로 수용했다. 목표 품질 완료로 수용한 것은 아니다.
