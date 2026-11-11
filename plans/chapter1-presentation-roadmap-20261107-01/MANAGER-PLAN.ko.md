# 전체 게임 요소 관리 툴 업데이트 계획

2026-11-07. 기존 v44 에셋북과 스프라이트 작업대를 보존하고, 최신 실제 소스를 기준으로 보는 제작실을 추가한다. 오래된 후보36 표지를 현재 상태로 오인하지 않게 한다. 모든 요소에는 현재/상속/패키지 의존/보존/계획 상태와 근거를 표시한다.

## Phase 0 — 기존 도구와 데이터 발견: 완료

기존 full30/book-v44/dist는 정적 도감과5개 보존 스프라이트 작업대다. 실제 후보37 closure는163파일이며 이 숫자가163개 게임 요소를 뜻하지 않는다. 현재 정의는 장비base12/접사12/고유3/능력치경계16, 기술3/패시브3, 구역3/의식2, 음향variant19+앰비언스1이다. 출처는 chapter_items.gd:4/18/32/37, growth_quality37.json, chapter_run.gd:4–10, combat_audio.gd:6–9다. 과거번호의 파일도 활성상속일 수 있다.

## M1 — 소스 기반 카탈로그

실행할 것: 기존 pathlib/JSON/SHA 패턴으로 카탈로그를 생성한다. 요소와 파일을 분리하고 고정ID/분류/이름/실제속성/소스줄/의존성/미리보기/출처/관련작업을 연결한다. 장비 상수는 제한된JSON literal 추출, 구역Vector는숫자만읽는방식으로 해석하며 임의eval/게임실행을 쓰지 않는다. 전체 포함파일과 정의 수를 실제소스와 대조한다.

확인:163패키지파일과 semantic정의가 누락/중복 없이 연결됨, 없는모델/출처/미검수사용상태를 만들어내지 않음. 원소스와 사용자저장은 읽기전용.

가드:전체 디스크·사용자AppData를 스캔하지 않는다. 원본/상속/계획을 나이순으로 구분하지 않는다.

## M2 — 제작실 화면과 미리보기

실행할 것: 별도 tools/game_manager에 작은 로컬 앱을 만든다. 사이드분류/전체검색/목록/상세검사창, 실제속성·출처·원본파일·관련작업을 연결한다. 이미지/SVG와음원controls를 제공하고 GLB는메시/리그/애니메이션메타와 가능한로컬모델미리보기를 제공한다. v44 도감·작업대는 원경로 링크로 유지하고 대량파일을 복사하지 않는다.

확인:대표 캐릭터/장비/스킬/맵/음원/이미지를 실제로 찾고확인, 검색·분류·목록과상세일치, 좁은화면·키보드가독성. JSON 값이모두가독텍스트로표시되고 미리보기미지원은 명시.

가드:없는3D미리보기를 있는것처럼꾸미지 않는다. 의존성은필요한작은파일만로컬보존하고node_modules/GB복사없이진행한다.

## M3 — 목표·작업·메모 관리

실행할 것: PROJECT-GOAL과40개백로그를관리화면에연결한다. 효과음은후순위,UI38을현재작업으로표시한다. 요소별상태/우선순위/개선메모를 별도관리JSON에지속저장한다. 게임속성을수정하는것처럼표시하지않고관리메모저장을명확히한다. 새게임데이터편집요청은 별도변경제안/검증경계를설계한다.

확인:메모/상태저장후새로고침과서버재시작에서도유지,동시편집충돌이조용히덮어쓰지않음,원게임파일해시불변.음향후순위와현재시각작업이첫화면에보임.

가드:로컬127.0.0.1만바인딩,임의경로쓰기/명령실행없음,요청ID·필드·길이검증,외부origin/경로순회차단,사용자저장·자격증명·.git비공개.관리상태를품질검증결과로자동변환하지않음.

## API 계약

GET /api/catalog: schema_version, generated_at, build, goal, entities, files, tasks, coverage, warnings.
요소: id,name,category,type,usage,source(path,line),attributes,dependencies,assets,provenance,evidence,task_ids.
파일: id,path,extension,bytes,usage,license.
GET /api/management: revision,records.
POST /api/management: revision,id,changes(status,priority,notes). 관리JSON만저장,오래된revision은409와현재값반환.
GET /files/<project-relative>: 허용된소스/에셋/도감미리보기만읽기. 외부경로와사용자저장사본차단.

분류: characters,enemies,bosses,skills,passives,equipment,affixes,uniques,maps,rituals,ui,effects,audio,assets.
관리상태: todo,in_progress,review,done,deferred. category/usage는실제카탈로그사실,관리status는작업상태로분리한다.

## 최종 확인

실제 브라우저에서 카탈로그/미리보기/저장·복원/목표·백로그 연결을 확인하고 바로가기를 제공한다. 앱을새로열어빈화면이나사라진메모가아닌지확인한다. 완료한기존전체게임검사는다시돌리지않는다.현재게임37와성공/실패원시는보존한다.