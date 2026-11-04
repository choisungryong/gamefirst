# 후보23 실제1080p 프레임 간격 계약

기존 measurement/CONTRACT.md와무효formal06등을보존한다. 같은23 EXE의정상냉기90131/pilot/기본HP·실제획득성장,메뉴에서실제클릭시작,focus처리활성,Forward+/MSAA2/scale3d1/VSync off/uncapped/time_scale1/OS delta_smoothing false. 이전clock·10초warmup+60초wholeinterval·nearest rank·180000cap·mode/focus/오류검사·p95≤16.67ms·동일EXE3회조건을유지한다. 수동전체/180최대부하/하드웨어GPU타이머/고정60FPS승인아님.

크기정의는실제관측근거로보완한다. render-preflight01의살아있는같은프레임에서Window/DisplayServer1920×1080,Image readback1920×1080,screen scale1/DPI96인데Texture2D.get_size는2304×1296을반환했다. 이전엄격Texture크기불일치무효를성공으로바꾸지않는다. 새frame_probe_render23는그반환값을raw CSV의texture_reported_width/height로명시적으로보존하며1920으로위조하지않는다.

실제1920×1080은메뉴에서측정시작전과sample완료뒤아직살아있는viewport의Image readback+PNG IHDR로독립검증한다. 매frame Window1920×1080/visible logical size/content_scale/scale3d/mode/MSAA의동일성을확인하고변경시무효. 보고된Texture크기도preflight값과매frame같아야한다. source/PCK불변·스케일1/동적설정변경없음과두실제readback을조합하며readback을매frame한것처럼주장하지않는다. 노출값불일치자체는도감에공개한다.

warmup과sample중GPUreadback·PNG·입력로그·observer파일I/O없음. 초기메뉴WGC확인뒤실제클릭후상태refresh는screenshot false로수행한다. sample뒤CSVflush/postflight readback·PNG는성능표본에포함하지않음. 모든wholeinterval의최종경계/긴frame도자르지않는다. 정식판정은두PNG/불변성/clock raw/metadata/실행/로그를독립재계산한3회가모두유효하고p95≤16.67ms일때만한다. 이는현재23의대표초반정상부하계약이며전체7분모든구간/모든하드웨어보장은아니다. 최종미술·조작·청취완성을대체하지않는다.
