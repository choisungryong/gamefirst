# 생성 지연24 연구 — 제품 미연결

후보23formal3회는대표p95기준을충족했으나약54초spawn군에서70–81ms긴frame이반복됐다. profile01은소스23정상2800tick재구성후fixed60 GPU10sim초→3400tickCPU callback분해다. 전체core독립정상정책동일/quiet. actor.sync최장170.704ms/전체process171.381ms,단일_create최장38.531ms. 이fixed60계측시간을formal실시간값과동일하게부르지않는다.

실제78새MeshInstance의원래mesh ID는78개지만resource_path는모두같은불변GLB ArrayMesh하나였다. inherited_batch19_cache가임시ID를key로써초기96→174로증가하며매번surface합치기와texture Image비교를되풀이했다. 가설만이아닌실제source/path/id/callback시간을RESULT.json에보존했다.

미연결chapter_actors_quality24.gd는21상속,허가된WARDEN subresource_path+kind로공유mesh를식별. inherited함수를그대로활용하기위한임시ID별칭만걸고즉시제거한다. 원배우별materialoverride/색/골격/AnimationPlayer/스킨/포즈는독립. 불변원본geometry만공유하며다른asset/빈path는원래경로로fallback한다. root23preload/EXE는미변경.

profile02 같은정상2800→3400동적구간/core동일/quiet. 공유skin1/build1/hit173(초기96포함)/임시cache0. actor.sync최장56.919ms/전체process57.543ms. 단일_create최장16.452ms,이후최장약7.777ms. 적생성비용이남으므로전체지연해결이라고확대하지않는다. 두계측은원시callback근거이며하드웨어GPUtimer/새formal3회가아니다.

fixture01은45검사/quiet. walker/ranged/charger/elite의기존23배치와vertex·index·UV·bone/weight등전체surfacearray동일,새동일종류mesh공유/색·texturepath·rim같음/배우별material과skeleton/player독립.실제두불변skin(walker/elite)만build,임시cache없음. 기존rig/paid pose/freeze/modal/deathalpha/reset/core복원23검사도포함한다. 이는합성표시fixture이며실제수동전체아님.

다음은24의실제정상화면/보스·구역2예외/반복reset을확인한뒤제품채택여부판단. 기존23/모든후보/stage·성공실패/사용자저장보존. 현재새24EXE없음.
