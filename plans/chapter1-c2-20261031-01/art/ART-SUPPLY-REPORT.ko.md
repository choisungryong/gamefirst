# C2 아트 공급 보고서

2026-10-31 현재 첫 플레이 후보용 바닥 1장, 채택 캐릭터 이동 5장, 행동 5장을 공급했습니다. 초기 주인공 레이아웃 증거 1장도 남겼습니다. 기존 KayKit의 색 변경으로 완료 처리하지 않았고, 독립적인 성인 비율의 어두운 판타지 아트를 생성했습니다.

## 보존

`C:/Project/game-research/implementation-backups/chapter1-c2-before-20261031-01/manifest.json`에 통합 직전 chapter1 5개 파일과 루트 HANDOFF/상태 2개 파일, 이전 소스 51개 해시, 네이티브 장비/진행 저장 2개 사본·해시를 보존했습니다. 원래 제품 파일은 수정하지 않았습니다.

## 경로와 검증

런타임 경로는 `chapter1/art/actors/{hero,walker,ranged,charger,elite}.png/json`입니다. 각 이동 16프레임과 남쪽 행동 12프레임을 별도 PNG에서 읽습니다. JSON은 프레임별 소스 사각형, 발 기준점, 텍스처, pixels_per_meter를 제공합니다. 이동 방향은 south/east/north/west 순서입니다.

큰 알파 연결 요소 기반 검사에서 각 이동 시트 16개, 각 행동 시트 12개를 검출했습니다. 선택 프레임 사각형 안 이웃의 큰 연결 요소 픽셀은 0개입니다. 생성된 결과를 직접 보아 성인 비율·무기/의상 구분·포즈 변화를 확인했습니다. 흉갑/칼의 보행병, 후드/활의 원거리병, 낮고 넓은 멧돼지 돌격수, 왕관/판금/망치의 정예가 구분됩니다.

주인공의 초기 시트는 정렬이 불충분하여 보존 증거로만 남겼고 두 번째 생성본을 채택했습니다. 픽셀을 자동으로 잘라 새 시트를 만드는 대신 원본 PNG와 가변 사각형 메타데이터를 제공합니다. 런타임 뷰 담당자가 프레임별 AtlasTexture/발 offset을 적용합니다.

`ASSET-LEDGER.json`에는 12개 PNG의 생성 원본 경로·사본 해시·크기·모드·전체 프롬프트와 메타데이터 해시 5개가 있습니다. 12개 프로젝트 사본의 SHA256이 생성 원본과 일치합니다. `GENERATION-PROMPTS.json`, `ELITE-ACTION-PROMPT.json`, `ATLAS-INSPECTION.json`, `ENEMY-ACTIONS-INSPECTION.json`, `ELITE-INSPECTION.json`을 참조합니다.

## 제작 방식과 공개 모델 조사

내장 `image_gen.imagegen`과 imagegen 스킬을 사용했습니다. CLI/API 우회는 사용하지 않았으며 투명 PNG 알파를 유지했습니다. 외부 원작 게임 코드·그래픽·사운드는 복사하지 않았습니다. 생성 이미지에 CC0 라이선스를 임의로 부여하지 않았습니다.

공개 3D 경로는 [Quaternius RPG Character Pack](https://quaternius.com/packs/rpgcharacters.html) 공식 CC0 안내와 [Gobkit 공식 무료 목록](https://gobkit.com/api/free)을 조사했습니다. 현재 확보된 공개 후보의 외형이 목표와 맞지 않아 파일을 다운받거나 채택하지 않았습니다. 최종 리깅 GLB 경로는 원래 브리프의 대안으로 유지합니다.

루트가 성인 비율 주인공 전후좌우 시각 증거를 검토한 뒤 첫 플레이 후보에 한해 2.5D 경로를 승인했습니다. 이것은 최종 C2 아트 승인이나 SACRATA 동등 품질 달성 선언이 아닙니다.

## 실행한 주요 명령

- PowerShell `Copy-Item -LiteralPath ... -Destination ...`: 생성 원본 보존 및 프로젝트 사본 생성
- `python plans/chapter1-c2-20261031-01/art/inspect_action_atlases.py`
- `python plans/chapter1-c2-20261031-01/art/inspect_elite_atlases.py`
- `python plans/chapter1-c2-20261031-01/art/write_asset_ledger.py`

분석 스크립트는 PNG를 읽고 메타데이터와 보고서를 쓰며 이미지 픽셀을 변경하지 않습니다. 최초 원장 실행에서 Windows cp949 기본 인코딩 오류가 발생하여 프롬프트 JSON 읽기를 UTF-8로 지정한 뒤 성공했습니다.

## 남은 범위

남쪽 외의 행동 동작, 전용 대기 동작, 장비별 외형 변형, 리깅/보간은 미제작입니다. 4개 키프레임만으로 만든 동작이므로 시간적 부드러움도 추가 개선이 필요합니다. 발 기준점·PPM은 초기 교정 값이며 실제 카메라에서 검증해야 합니다. 바닥의 실제 반복 이음새 검사는 아트 담당자가 완료하지 않았습니다. 전투 효과와 사운드의 최종 체감 승인은 루트의 실행 검토가 필요합니다.

