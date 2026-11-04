# 접지감 개선29 · 2026-11-04

현재 제품29는Actor29의모델그림자만채택했다. World29 SSAO설정과World27바닥상감은미채택이다. 기존moon의방향·밝기와메시·material·전투규칙은유지한다.

compare01 session82242:정상2800/16000tick의SSAO off/quiet/strong6PNG/core불변/quiet. 직접본5장에서는전투접지감차이가작아미채택했다. 전체RGB평균차이0.04~0.12/255수준은원시차이량일뿐품질근거로승격하지않는다. 공식Godot4.5문서 https://docs.godotengine.org/en/4.5/classes/class_environment.html 및 https://docs.godotengine.org/en/4.5/tutorials/3d/environment_and_post_processing.html 을설정확인에사용했다.

shadow01 session32110:같은28source/두정상checkpoint/카메라·core·빛고정에서일반·중간정예modelmesh의shadow_casting만전환.4PNG모두직접검수/core불변/quiet. 발밑과몸뒤의실제그림자로접지감개선확인. sourceActor29는풀224개준비완료뒤와이후_create시modelmesh의캐스터설정을ON으로유지한다. 기존원형접지음영은유지한다.

cost01 session57080:1920×1080/uncapped/vsync off/ignorefocus/정상policy/2초warmup+10초OS시계표본각1회. p95 5.800→5.927ms/p99 6.558→6.821/최장35.785→37.147/>33.33각1/drawmax245→300.양쪽독립core같음/quiet.종료틱3528/3529로1틱차이가있으며lockstep성능비교아님. 최종focus/실제패키지/대표3회승인아니다.29afterPNG직접검수.

패키지29 build75876 terminal/실제shadow01 26211 terminal. 실제EXE/PCK2800checkpoint→3400tick 원래livepolicy/controllers/48표시혼합/독립core같음/224modelmeshshadowON·OFF0/실제1080p/quiet,afterPNG직접검수. pool_hits112는풀에서꺼낸횟수이며첫사용도포함한다. 과거의이계수를순수재사용횟수로읽지않는다. 39항목독립보존감사pass. source변경은Actor28→29 assembly와Actor29파일추가뿐.

전체냉기GPU검사는full29/runtime/gpu-cold01/session10115로진행중이며결과는아직미확정. 재실행하지말고기존PID24300/launch/raw/execution부터확인한다. 부분검수와개발비용표를수동전체·실청취·최종3회·전체후반리듬/품질승인으로확대하지않는다.
