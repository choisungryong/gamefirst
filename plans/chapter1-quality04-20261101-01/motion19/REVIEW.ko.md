# 일반 적·중간 정예 골격 동작 연구19 — 진행 중

제품은 후보18을 유지한다. 새 Actor19 세 시안은 별도 외부 stage에서만 조립했으며 루트 chapter_one_view와 후보 EXE·사용자 저장을 변경하지 않았다.

## 실제 화면 판단

- replay01: 기존 CC0 KayKit 골격을 실제 이동/공격/죽음 상태에 연결했다. 밝고 큰 두개골/짧은 팔다리의 장난감 같은 비율 때문에 제품 채택 제외.
- replay02: 같은 모델의 머리 축소/어두운 재질/누더기를 시도했으나 화면에서 둥근 캐주얼 실루엣이 남는다. 채택 제외. 성공 로그와 PNG는 보존한다.
- replay03: 이미 허가된 Mophs 악마 GLB에서 체인 surface를 뺀 일반/중간 정예 시안. 보스 presenter는 그대로다. 실제 at-03.0 화면에서 팔다리/진행 방향 구분이 앞선 두 시안보다 낫다. 다만 보스와 같은 계열 모델이며 어두운 몸체가 바닥에 묻히는 부분과 외형 차별화는 추가 개선 대상이다. 아직 최종 아트 승인/제품 연결/후보19 패키징을 하지 않았다.

## 검증한 범위

replay01의 후보18 기준 화면을 재사용해 replay03과 비교했다. 정상 정책/기본HP/실제 획득 성장/냉기 seed90131을 tick6500까지 재구성한 뒤8초 fixed60 GPU다. 전체 core snapshot 시작·종료 모두 동일, rig28, 샘플8014. import/check/GPU 각각 exit0/stderr0. 연구 루트18 freeze 일치. 수동 전체/실시간/성능 검사가 아니다.

semantics01은 별도 목적의30초 fixed60 GPU다. 실제 생성된 적에서 windup_slam59·windup_fan62·slam35·fan70 프레임을 관찰했다. 실제 paid recover의 release 이후 clip 위치87프레임을 검사했다. 숫자는 공격 횟수가 아니다. 정상 냉기 사체 age>.23의 재질 alpha<.001을5308 actor-frame에서 검사했다. paused/choice/inventory/equipment4모드에서 pose·death age·cold record 정지, 원래 모드 복귀 후 전체 core snapshot 불변1검사 통과. import/check/GPU exit0/stderr0. root18/source pins 보존. 모든 게임 프로세스 종료 확인.

semantics01/visual.json의 scope 문구는 상속 helper의8초 설명이 남아 있다. 실제 실행 기간은 launch의 quit-after=30과 semantics.json/RESULT.json이 맞다. 원시 파일을 성공 설명에 맞춰 고치지 않는다.

## 다음 작업

실제 windup→paid release·방향별 동작을 영상/해당 순간 화면으로 검수한다. 중간 정예와 최종 보스 외형 차별화, hero 가림, 실제 빙결/리셋과 재생성, 군중 성능을 추가 검증한 뒤 제품 채택 여부를 판단한다. 기존14·16·17·17b·18 및 모든 실패 원본을 보존한다. 첫 장 최종 목표는 active다.

## 후속 화면 검수 — readable19

`chapter_actors_readable19.gd`는 악마 시안을 상속한다. 일반 적의 얼굴을 뼈색으로 밝히고 약한 rim을 더했다. 중간 정예는 적갈색 몸체·금빛 얼굴에 Spine1을 따르는 어깨 장갑/뿔을 추가했다. 장비 재질도 기존 cold/death/owner alpha 계산에 포함하며, 보스는 상속된 기존 경로를 유지한다. 추가 외부 아트 없음.

attack01은 Python 기본 cp949로 UTF8 view를 읽다가 실패해 GPU 미시작. attack02는 검사 helper의 `_capture(String)`가 부모 `_capture(int)`와 충돌해 check exit1/stderr298, GPU 미시작. 원본 stage/스크립트/실패 로그를 보존했고 새 attack03에서 함수명을 분리했다.

attack03은 새 readable19/정상 policy tick6500부터30초 fixed60 GPU, import/check/GPU exit0/stderr0. 실제 중간 정예의 양방향 준비·공격 clip 4장과 normal6장을 보존했다. 이 첫 공격 clip 캡처는 windup의 마지막6틱 시작(time0)이므로 **paid release 증거로 쓰지 않는다**. 준비 자세/서로 다른 방향을 실제 PNG로 확인했다.

release01은 같은 초기 정상 빌드에서 별도5초만 실행해 state를 포함한 이름으로 준비→release를 캡처했다. 실제 enemy622의 fan tick6521, slam tick6747에서 state=recover/clip time=.157이며 해당 PNG 두 장을 직접 확인했다. 둘 다 실제 paid release와 연결된다. 영웅은 위험 범위를 피한 상태라 피해 받은 영웅 검사로 확대하지 않는다. 총6공격PNG, import/check/GPU exit0/stderr0. 기존 source pins와 root18 freeze 보존. 상속 helper 문구의30초/8초 설명이 release01 raw JSON에 남지만 launch quit-after=5가 실제 길이다.

화면에서 일반 적은 어두운 바닥에 앞선 시안보다 잘 드러나고 정예는 크기·색·어깨가 구분된다. 어깨 뿔은 현재 카메라에서 작게 보여 이것만으로 실루엣 목표 완료로 보지 않는다. 원거리/돌진 적의 기존 sprite와 최종 보스는 그대로이며, 일반 walker의 근접공격은 이 정상 회피 policy에서 캡처되지 않았다. 다음은 그 미검증 경로·빙결/리셋·hero 가림 fixture와 군중 성능을 확인하고 제품 통합을 결정한다. 모든 게임 실행 terminal, 서버8781만 유지.
