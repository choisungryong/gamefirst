from pathlib import Path
H=Path(__file__).parent
s=(H/'analyze_actor28_movies01.py').read_text(encoding='utf-8').replace("O/'analysis01'","O/'analysis02'")
s=s.replace("assert rows[0]['tick']==rows[1]['tick'] and rows[0]['frames']==rows[1]['frames']",'''for row in rows:
 raw=O/row['variant']/'normal-speed.avi'
 cmd=[str(ffmpeg),'-v','error','-i',str(raw),'-map','0:v:0','-f','framemd5','-']
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=90);assert p.returncode==0
 (D/(row['variant']+'-raw-framemd5.txt')).write_text(p.stdout,encoding='utf-8')
 hashes=[line.rsplit(',',1)[-1].strip() for line in p.stdout.splitlines() if line and not line.startswith('#')]
 tail=0
 for value in reversed(hashes):
  if value!=hashes[-1]:break
  tail+=1
 row['raw_frames']=len(hashes);row['identical_final_frame_repeats']=tail
 row['frames_through_first_terminal_image']=len(hashes)-tail+1
assert rows[0]['tick']==rows[1]['tick']
assert rows[0]['frames_through_first_terminal_image']==rows[1]['frames_through_first_terminal_image']
assert rows[0]['identical_final_frame_repeats']!=rows[1]['identical_final_frame_repeats']''')
s=s.replace('Compare actual final tick/frame counts, not inherited raw RESULT scope text saying10simsec.','Raw decoded framemd5 proves excess frames are identical final-image repeats; actual end ticks and frame counts through first terminal image match. Original raw total frame counts differ and remain preserved. chapter_view.gd uses150ms OS-clock audio cleanup after stopping simulation. Compare these verified active spans, not inherited raw RESULT scope text saying10simsec.')
target=H/'analyze_actor28_movies02_generated.py';assert not target.exists();target.write_text(s,encoding='utf-8');exec(compile(s,str(target),'exec'))
