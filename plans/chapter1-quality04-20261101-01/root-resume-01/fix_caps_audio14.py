from pathlib import Path
import shutil
HERE=Path(__file__).parent;ROOT=Path('C:/Project/d2r-combat-baseline');OUT=ROOT/'plans/chapter1-quality04-20261101-01/full14/release-caps01'
p=HERE/'elements_caps14.gd';shutil.copy2(p,OUT/'caps-before-audio-reset.gd')
s=p.read_text(encoding='utf-8');anchor='\tfor voice in audio.voices:voice.stop();voice.stream=null'
assert s.count(anchor)==1
s=s.replace(anchor,'''\taudio.reset()
\t# Match production shutdown: unpause stopped voices, then allow the actual
\t# mixing thread to release playback, independent of simulated timer speed.
\tvar release_at := Time.get_ticks_usec()+200000
\twhile Time.get_ticks_usec()<release_at:await get_tree().process_frame
'''+anchor)
p.write_text(s,encoding='utf-8')
s=(HERE/'release_caps14.py').read_text(encoding='utf-8').replace('release-caps01','release-caps02')
p=HERE/'release_caps14_02.py';assert not p.exists();p.write_text(s,encoding='utf-8')
(OUT/'DIAGNOSIS.ko.md').write_text('외부caps13검사는모두통과했으나종료때AudioStreamWAV/AudioStreamPlaybackWAV누수경고124bytes. verbose로실제객체를식별했다. 이검사는제품의audio.reset(중지voice의stream_paused=false)및실제시계release대기를우회했다. 제품정상종료경로를쓰는패키지전체/영상은quiet였다. 검사에동일reset/200ms실제시계대기를연결해새02에서검증하며,이결과전에는해결주장하지않는다.14제품freeze/EXE는수정하지않았다.\n',encoding='utf-8')
