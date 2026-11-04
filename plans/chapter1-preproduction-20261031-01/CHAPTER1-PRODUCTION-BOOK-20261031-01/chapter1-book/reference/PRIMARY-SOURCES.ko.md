# SACRATA 공식 1차 자료 조사

2026-10-31, Asia/Seoul. 범위: 공식 상점 설명·개발 공지·공식 공개 미디어의 메타데이터 읽기. 실제 게임 실행·플레이 영상 관찰·음향 청취·바이너리 분석은 이 조사에서 수행하지 않았다. 아래의 기능은 **개발자 공개 설명**이며 내부 구현·수치의 독립 검증이 아니다.

## 읽은 출처

| ID | 정확한 출처 | 실제 읽은 부분 |
|---|---|---|
| P01 | [Steam 상점](https://store.steampowered.com/app/3201450/SACRATA/?l=english) | About This Game, Hunt for Loot, Beauty That Slays, Build Your Fate, Survive the Nightmare, 개발/배급/출시 상태 |
| P02 | [공식 뉴스 모음](https://steamcommunity.com/app/3201450/allnews/?l=english) | 최근 종료 공지부터 2025 보스 개발로그까지. 일반 사용자 댓글은 기능 근거에서 제외 |
| P03 | [이름 변경·개발 진척 공지](https://steamcommunity.com/games/3201450/announcements/detail/676253085555756021) | Dual-Loop Integration, Exploratory Random Open World, Multi-Build System |
| P04 | [2026 플레이테스트 공개 공지](https://steamcommunity.com/games/3201450/announcements/detail/675133527946168044) | What’s Included, 전체 해금 예상 길이, 콘텐츠 수량 |
| P05 | [2026 플레이테스트 종료 공지](https://steamcommunity.com/games/3201450/announcements/detail/675134162359815162) | 종료·향후 Demo 계획·피드백에 따른 개선 영역 |
| P06 | [보스 개발로그 WIP](https://steamcommunity.com/games/3201450/announcements/detail/529842974219043633) | 보스 이름·4가지 공격 이름·공식 YouTube 프리뷰 링크 |
| P07 | [Steam 공개 AppDetails 응답](https://store.steampowered.com/api/appdetails?appids=3201450&l=english) | `3201450.data.release_date`, `screenshots`, `movies` 메타데이터. 이미지·영상 파일은 다운로드하지 않음 |
| P08 | [Steam 공식 뉴스 응답](https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=3201450&count=10&maxlength=0) | `appnews.newsitems`의 title/url/date/contents. 원문 본문과 실제 announcement 리디렉션 확인 |

웹 읽기 도구가 일부 직접 공지/API URL을 읽지 못해, 공개 HTTP 응답을 PowerShell `Invoke-RestMethod` / `Invoke-WebRequest`로 읽었다. 브라우저 로그인·세션·숨겨진 게임 상태는 접근하지 않았다. 관련 기능은 P02의 동일 공지 본문에서도 대조했다.

## 기능별 확인 사실

| 축 | 개발자가 설명한 구체 내용 | 출처·근거 위치 | 현재 이 조사로는 미확인 |
|---|---|---|---|
| 전투의 중심 | 디아블로에서 영감을 받은 전리품과 다수 적 생존 전투의 결합 | P01 About This Game | 자동/수동 시전별 입력 규칙, 실제 동시 적 수, 판정/속도 공식 |
| 런 성장 | 무작위 스킬과 장비로 특화 빌드·조합 구성 | P01 About This Game | 스킬 추첨 가중치, 레벨별 선택 수, 정확 진화 선행조건 |
| 장비 기대 | 처치 후 장비가 능력 향상·새 빌드·전설 장비의 기대를 제공 | P01 Hunt for Loot | 드롭률·등급 분포·아이템 테이블·픽업/비교 입력 |
| 지속 성장 | Echo Hall, Gear Forging, Talent Activation을 런 밖 성장과 연결 | P03 Dual-Loop Integration | 패배 시 정확 보존/손실 규칙·저장 schema |
| 장비 강화 | 재능 포인트, 장비 upgrade/temper, 주요 스탯을 강화하는 affix 선택 | P01 Build Your Fate | 강화 재료·비용·실패·잠금·재추첨 공식 |
| 빌드 재료 | divine skills, relics, runes, tokens를 조합 | P03 Multi-Build System | 각 시스템의 슬롯·상한·중복·적용 순서 |
| 탐색·보상 | 무작위 연속 공간에 보물상자·relic room·신단·blood spring·자원 노드·특수 이벤트 배치 | P03 Exploratory Random Open World | 맵 생성 알고리즘·이벤트 분포·상호작용 시간 |
| 보스 판독 | 공격을 읽고 재배치하며 빈틈을 이용하는 생존/딜 균형 | P01 Survive the Nightmare | 실제 무적 프레임·전조 시간·장판 판정 |
| 보스 행동 예 | Harug the Bonegrinder: Charge, Hammer Smash, Sweeping Strike, Leap Crush | P06 보스 개발로그 | 2025 WIP가 2026 영상과 동일 패턴/튜닝인지 여부 |

이는 항목별 기능 식별을 위한 요약이다. 모델/엔진·스킬 스케줄러·성능 최적화·피해 처리·애니메이션 시스템을 역추정하지 않는다.

## 버전·출시 상태를 구분

- 2026-10-31 확인 시점 P01/P07은 `Coming soon`, `coming_soon=true`이다. 정식 출시 제품으로 표시하지 않는다.
- P05는 플레이테스트가 종료되었고 다음 Demo를 준비한다고 설명한다. 종료 예고는 2026-10-11 23:59 UTC를 제시한다. 현재 상점에서 다시 요청/실행할 수 있다는 결론은 내리지 않는다.
- 뉴스 API의 Unix 시각을 KST로 변환하면 P03은 2026-09-04, P04는 2026-10-04, P05는 2026-10-12다. 뉴스 모음의 상대 날짜/미국 표기와 하루 차이가 있어 **발행 시각과 종료 사건 시각을 구분**한다.
- P04가 제시하는 약3시간은 **플레이테스트의 전체 콘텐츠 해금 예상 길이**다. 한 판 길이 또는 1장 길이가 아니다.
- P04의 수량은 지도 탐색 이벤트10, 정예/보스 합계7, 스킬/진화30+, Relic50+, 장비300+, 업적60+, 시너지/빌드 경로20+다. 개발자 설명을 옮긴 것이며 직접 목록을 세거나 모두 플레이해 확인하지 않았다. 이번 프로젝트1장의 의무 수량으로 복제할 근거가 아니다.
- P05의 개선 예정 영역은 성능/안정성, 빌드/전투 구별, 캐릭터/콘텐츠, 키 설정/컨트롤러/UI다. SACRATA가 모든 품질 영역을 이미 해결했다고 가정하지 않는다.
- 2025 초기 플레이테스트 안내의 화염·냉기/첫 보스 범위와 2026 안내를 섞지 않는다. 옛 로드맵의 예정 항목을 현재 구현 사실로 승격하지 않는다.

## 공식 미디어 인덱스 — 링크와 메타데이터만 확인

### 영상

1. [공식 보스 WIP 프리뷰](https://www.youtube.com/watch?v=exgkTMaz1_k): P06 본문의 `previewyoutube=exgkTMaz1_k`에서 식별. 이 조사에서는 재생하지 않았다.
2. P07의 movie `257117653`, 이름 `Early Access Launch Trailer`, `highlight=true`. 이 제목만으로 실제 얼리 액세스 출시를 단정하지 않는다. P01/P07 출시 상태는 Coming soon이다.
3. P07의 movie `257431412`, 이름 `Story CG`, `highlight=true`. CG를 실제 게임 플레이 기준으로 섞지 않는다.

공식 상점의 영상 UI를 통해 보는 경로는 [P01 상점](https://store.steampowered.com/app/3201450/SACRATA/?l=english)이다. HLS 목록 메타데이터는 존재하지만 다운로드/프레임 추출하지 않았다.

### 스크린샷

P07에서 공식 스크린샷11개를 반환했다. 다음은 에셋북의 출처 링크 후보이며, 이 조사에서는 이미지 내용을 직접 판독하지 않았으므로 장비/환경 등 임의 장면 라벨을 붙이지 않았다.

| Steam ID | 공식 원본 URL |
|---|---|
| 0 | [ss_87e3… 1920×1080](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3201450/87e3bab3d64bf6bb044381b346509a7f176975c9/ss_87e3bab3d64bf6bb044381b346509a7f176975c9.1920x1080.jpg?t=1791772780) |
| 1 | [ss_8a7c… 1920×1080](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3201450/8a7ca0e29f8eb3450509aeae93b2b567f828b956/ss_8a7ca0e29f8eb3450509aeae93b2b567f828b956.1920x1080.jpg?t=1791772780) |
| 2 | [ss_f6cd… 1920×1080](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3201450/f6cd4be3c544d8935eefa1a97a4ebd1a24b02141/ss_f6cd4be3c544d8935eefa1a97a4ebd1a24b02141.1920x1080.jpg?t=1791772780) |
| 3 | [ss_5614… 1920×1080](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3201450/5614d9c9b6275345e1358ab9e30685c9f4737f2f/ss_5614d9c9b6275345e1358ab9e30685c9f4737f2f.1920x1080.jpg?t=1791772780) |
| 4 | [ss_0ef5… 1920×1080](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3201450/0ef5fad9794bcbe7f8047b477e14914ecaad1860/ss_0ef5fad9794bcbe7f8047b477e14914ecaad1860.1920x1080.jpg?t=1791772780) |
| 5 | [ss_51ef… 1920×1080](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3201450/ss_51ef266953868ff112236f2196e8005bb1ef167b.1920x1080.jpg?t=1791772780) |
| 6 | [ss_470c… 1920×1080](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3201450/470c5c4d66c952f3e8b7c383640f357614c2fbe3/ss_470c5c4d66c952f3e8b7c383640f357614c2fbe3.1920x1080.jpg?t=1791772780) |
| 7 | [ss_68e4… 1920×1080](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3201450/68e444db8a8456fca3a671def9ea226298d067fd/ss_68e444db8a8456fca3a671def9ea226298d067fd.1920x1080.jpg?t=1791772780) |
| 8 | [ss_3200… 1920×1080](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3201450/ss_32000a082a579c224040352a78663441152ec545.1920x1080.jpg?t=1791772780) |
| 9 | [ss_59b1… 1920×1080](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3201450/59b11c3e442061741a7bb4ab263a8e29a06bc6a1/ss_59b11c3e442061741a7bb4ab263a8e29a06bc6a1.1920x1080.jpg?t=1791772780) |
| 10 | [ss_ebf6… 1920×1080](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3201450/ebf61480e49af87da449afd38afeddacf8c3bd69/ss_ebf61480e49af87da449afd38afeddacf8c3bd69.1920x1080.jpg?t=1791772780) |

P03에 연결된 공식 GIF 세 개는 다음과 같다. 읽기 도구가 GIF 재생을 지원하지 않아 움직임은 검토하지 않았다.

- [Dual-Loop Integration 미디어](https://clan.fastly.steamstatic.com/images/45515355/b330abd4cbe7457837d6b99fdc5359d5aca2afb0.gif)
- [Exploratory Random Open World 미디어](https://clan.fastly.steamstatic.com/images/45515355/9c2cef2fc5ea9ed048a7b08d789d3a3602155040.gif)
- [Multi-Build System 미디어](https://clan.fastly.steamstatic.com/images/45515355/daacbb33e4ebeaac7be81d95ef4c347f1bd17979.gif)

## 페이지에 옮길 수 있는 출처 패턴

- 공식 기능 설명: 이 문서 `기능별 확인 사실`의 축/확인 사실/출처/미확인 필드. 페이지에는 `공식 설명`으로 라벨링한다.
- 버전 표기: 이 문서 `버전·출시 상태를 구분`의 2025 WIP/2026 플레이테스트/현재 Coming soon 구분.
- 미디어 출처 카드: 위 `공식 미디어 인덱스`의 URL·Steam ID·미관찰 상태. 재생/판독을 실제 수행한 뒤 장면 라벨과 검토 날짜를 추가한다.
- 현재 프로젝트의 설계 결정은 이 문서에 작성하지 않는다. 공식 사실 추출과 최종 목표/스코프 결정은 별개다.

에셋북에 넣을 때 참고 이미지/영상의 공개 출처와 제작에 사용할 자산의 출처를 분리해야 한다. 이 자료에서 모델·텍스처·아이콘·음향을 제품에 재사용할 수 있는 라이선스는 확보하지 않았다. 단순 공개 열람을 제품 사용 권한으로 해석하지 않는다. 외부 미디어 파일을 프로젝트 에셋으로 다운로드하거나 복사하지 않았다.

## 확신과 남은 공백

높은 확신: 공식 상점의 소개 문구·출시 상태, 개발 공지의 명시 기능과 수량, 공개 API의 미디어 URL/ID, 공식 보스 프리뷰 링크. 중간 확신: 공개 설명이 각각의 당시 플레이테스트 빌드에 반영된 범위. 미확인: 사용자 영상의 정확 빌드, 내부 규칙·확률·최적화, 실제 플레이 손맛/프레임/음향, 전체 장비 목록·스킬 진화표, 현시점 재실행 가능성.

출처 설명은 확인했지만 직접 플레이 또는 영상 시청을 수행한 결과가 아니다. 이 보고서만으로 SACRATA 분석/우리 제품 품질 관문이 완료됐다고 표시하지 않는다.
