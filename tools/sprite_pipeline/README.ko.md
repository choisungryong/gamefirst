# 캐릭터 스프라이트 등록 파이프라인 v1

`index.html`은 에셋북에 복사해 사용하는 작업대입니다. 투명 PNG와 동작 배치를 읽어 이동·공격·피격·사망을 미리 보고 등록 설정을 내려받습니다. 이미지는 외부 서비스로 전송하지 않습니다. 정지 이미지에서 새 동작을 생성하지 않습니다.

## 등록 순서

1. 동작이 그려진 투명 PNG 시트를 선택합니다.
2. 가로·세로 칸 수, 역할, 1m당 픽셀을 지정합니다. 기본 행 순서는 남/동/북/서 이동, 공격, 피격, 사망입니다. 다른 배치는 ‘동작 행과 발 위치 조정’에서 지정합니다.
3. 발 기준선과 각 동작을 확인한 뒤 ‘등록 설정 저장’을 누릅니다. 설정 JSON을 원본 PNG와 같은 폴더에 둡니다.
4. 아래 컴파일 명령으로 새 디렉터리에 등록합니다. 같은 출력 경로를 다시 쓰면 거부합니다.

```powershell
& 'C:/Users/twins/AppData/Local/Programs/Python/Python310/python.exe' 'C:/Project/d2r-combat-baseline/tools/sprite_pipeline/compile.py' --spec 'C:/YourAssets/new-character.sprite.json' --id new-character --output 'C:/Project/d2r-combat-baseline/chapter1/art/sprite_catalog/new-character-v01' --resource-base 'res://chapter1/art/sprite_catalog/new-character-v01'
```

출력은 `actor.json`, 원본과 바이트가 같은 PNG 사본, 출처·해시·동작 목록을 담은 `manifest.json`입니다. 기존 `chapter1/art/actors`와 제품 어셈블리·저장은 변경하지 않습니다. 실제 프로젝트에 넣을 출력 디렉터리는 resource-base와 일치시킵니다. PNG는 Godot 프로젝트에서 import 후 패키지 리소스 목록에 포함해야 합니다.

기존 가변 프레임 시트는 `--spec` 대신 `--legacy 기존.json`으로 옮길 수 있습니다. 기존 발 위치·프레임 사각형·시간·크기를 유지하고 여러 PNG도 함께 등록합니다. 임의의 PNG에서 동작 의미를 자동 추측하지 않습니다.

## 게임 표시 연결

`chapter1/presentation/sprite_asset_presenter.gd`를 시각 자식 노드로 만들고 `configure("res://.../actor.json")`를 한 번 호출합니다. 이후 `sample("move", "south", phase)`처럼 동작·화면 방향·정규화된 진행도를 전달합니다. 이동과 대기는 순환하고 공격·피격·사망은 마지막 프레임에서 정지합니다. 동작이 없으면 방향별 이동의 첫 포즈로 대체하고 `last_sample.fallback=true`로 명시합니다.

공격의 예고→타격→회복 진행도는 기존 core/controller가 제공합니다. 등록의 `release_frame`은 저작 메타데이터이며 피해를 발생시키거나 core의 타격 시점을 바꾸지 않습니다. 새 표시기를 현재 3D 배우에 덧씌우지 않았습니다. 에셋북의 ‘전투 역할 연결’에서 컴파일한 actor.json과 PNG를 불러오고 타격 프레임을 지정해 역할 설정 JSON을 저장합니다. 역할은 기존 주인공/일반 적/원거리/돌진/중간 정예 중 선택한 유형이며 해당 AI·능력치·판정은 유지합니다. 최종 보스는 기존3D를 유지합니다. 전투용 동작이 빠진 에셋은 기본 연결에서 거부합니다. 아래 별도 미리보기가 설정을 읽습니다. 현재 제품에 자동 배포하는 버튼은 아닙니다.

현재는 4방향 등록을 지원합니다. 8방향·한 장 그림의 리깅/동작 생성·캐릭터별 공격 패턴·아이템/난이도 제작은 별도 단계입니다. 몹 하나를 추가할 때는 그 에셋의 방향/동작/발 위치/역할 가독성을 검수하고, 공통 코드·공격 규칙이 바뀌지 않으면 전체 장 검사를 매번 되풀이하지 않습니다. 출시 후보 단위에서 전체 전투·저장·음향·대표 성능을 묶어 검수합니다.


## 등록한 에셋으로 전투 미리보기

작업대에서 컴파일한 폴더의 actor.json과 모든 PNG를 함께 선택하고, 공격 포즈의 타격 프레임을 0부터 지정한 뒤 역할 설정을 저장합니다. 등록된 예제도 사용할 수 있습니다.

```powershell
& 'C:/Users/twins/AppData/Local/Programs/Python/Python310/python.exe' 'C:/Project/d2r-combat-baseline/tools/sprite_pipeline/preview.py' --registry 'C:/YourAssets/walker.roles.json' --output 'C:/Project/game-research/build-staging/my-walker-preview-01'
```

새 격리 디렉터리에 현재 제1장 소스와 선택한 등록 에셋만 준비해 실행합니다. 메뉴에서 직접 플레이할 수 있고 `--pilot --quit-after 20`을 더하면 기존 정상 정책으로 짧게 확인하고 종료합니다. 미리보기는 항상 저장을 끕니다. 기존 EXE·소스 어셈블리·사용자 저장과 이전 미리보기는 변경하지 않습니다. 반복 출력 경로는 거부합니다.

CLI로 역할 설정을 만들 때는 다음처럼 실행할 수 있습니다.

```powershell
python tools/sprite_pipeline/roles.py --bind walker=chapter1/art/sprite_catalog/new-character-v01/manifest.json --release walker=2 --output new-character.roles.json
```

현재 전투 연결은 프로토타입입니다. 기존3D 리그를 숨겨 호환용으로 유지하고 스프라이트를 붙이므로 최적화된 스프라이트 전용 런타임이라고 하지 않습니다. 자료의 공통 방향 공격은 방향별 포즈로 자동 변환하지 않으며, 배포 전 방향·밀집 가독성·공격 타이밍·성능을 검수해야 합니다. 미리보기 검사 결과는 출시 승인이 아닙니다.
