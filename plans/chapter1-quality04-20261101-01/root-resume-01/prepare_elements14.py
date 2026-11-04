from pathlib import Path
import hashlib,json,shutil,subprocess
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OUT=BASE/'elements14';STAGE=Path('C:/Project/game-research/build-staging/chapter1-elements-20261101-01')
assert not OUT.exists()and not STAGE.exists();OUT.mkdir();STAGE.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pins=json.loads((BASE/'full13/FINAL-SOURCE-FREEZE.json').read_text(encoding='utf-8'));assert all(sha(ROOT/n)==h for n,h in pins.items())
s=(ROOT/'chapter1/view/comet.gdshader').read_text(encoding='utf-8')
a=s.index('  float lance=');b=s.index(' }else if(bolt_data.y>.8)',a)
s=s[:a]+'''  // Keep the paid point at the white nose; the faceted body trails behind.
  p=vec2((UV.x-.5)*2.,(UV.y-.5)*2.);
  float extent=max(0.,.21-abs(p.x+.32)*.39);
  float aa=max(fwidth(p.y),.008);
  float lance=(1.-smoothstep(extent,extent+aa,abs(p.y)))*smoothstep(-1.,-.82,p.x)*(1.-smoothstep(.08,.14,p.x));
  float spine=(1.-smoothstep(.014,.055,abs(p.y)))*smoothstep(-.88,-.7,p.x)*(1.-smoothstep(.03,.13,p.x));
  float ridge=smoothstep(-.025,.025,p.y+p.x*.12);
  shape=lance;
  color=mix(vec3(.05,.32,.56),vec3(.32,.79,.96),ridge);
  core=vec3(.76,.96,1.)*spine*1.65;
'''+s[b:]
p=ROOT/'chapter1/view/comet_quality14.gdshader';assert not p.exists();p.write_text(s,encoding='utf-8')
s=(ROOT/'chapter1/view/impact.gdshader').read_text(encoding='utf-8')
s=s.replace(' float shape=heat*(.28+n*.5)+wave*.40;',' float shape=heat*(.28+n*.5)+wave*.40;\n vec3 core_color=vec3(1.,.77,.30);')
a=s.index('  float crystal=');b=s.index(' }else if(impact_data.y>.8)',a)
s=s[:a]+'''  float angle_=atan(p.y,p.x);
  float spokes=pow(abs(cos(angle_*6.+sin(r*11.)*.16)),34.);
  float broken=step(.24,noise(p*13.));
  float cracks=spokes*(1.-smoothstep(front-.12,front+.08,r))*smoothstep(.04,.16,r)*broken;
  shape=(wave*.42+cracks*.85)*pow(1.-age,.65);
  color=mix(vec3(.07,.35,.66),vec3(.62,.93,1.),cracks);
  core_color=vec3(.78,.96,1.);
'''+s[b:]
s=s.replace('shape=(fissures*heat*.65+wave*.22);color=vec3(.46,.61,1.);','shape=(fissures*heat*.65+wave*.22);color=vec3(.46,.61,1.);core_color=vec3(.80,.88,1.);')
s=s.replace('vec3(1.,.77,.30)*core*1.7','core_color*core*1.7')
p=ROOT/'chapter1/view/impact_quality14.gdshader';assert not p.exists();p.write_text(s,encoding='utf-8')
closure=json.loads((BASE/'full13/build/staging-manifest.json').read_text(encoding='utf-8'))
old=Path('C:/Project/game-research/build-staging/chapter1-full-candidate-20261101-13')
for n,h in closure.items():
 assert sha(old/n)==h
 p=STAGE/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
extra=['chapter1/view/chapter_elements_quality14.gd','chapter1/view/comet_quality14.gdshader','chapter1/view/impact_quality14.gdshader','chapter1/view/arc_quality14.gdshader']
for n in extra:shutil.copy2(ROOT/n,STAGE/n)
p=STAGE/'chapter1/chapter_one_view.gd';p.write_text(p.read_text(encoding='utf-8').replace('res://chapter1/view/chapter_effects_quality10.gd','res://chapter1/view/chapter_elements_quality14.gd'),encoding='utf-8')
p=STAGE/'project.godot';p.write_text(p.read_text(encoding='utf-8').replace('Quality13','Elements14Research01'),encoding='utf-8')
(OUT/'stage01.json').write_text(json.dumps({'stage':str(STAGE),'root13_freeze_still_matches':True,'extra':extra,'pins':{str(p.relative_to(STAGE)).replace('\\','/'):sha(p)for p in STAGE.rglob('*')if p.is_file()},'scope':'Independent FX research stage, no root13 source mutation. Not visual/gameplay approval.'},indent=2),encoding='utf-8')
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('import',['--editor','--import']),('check',['--check-only','--script','res://chapter1/view/chapter_elements_quality14.gd'])]:
 command=[engine,'--headless','--path',str(STAGE)]+args
 with(OUT/(label+'01.stdout.txt')).open('xb')as stdout,(OUT/(label+'01.stderr.txt')).open('xb')as stderr:
  p=subprocess.Popen(command,stdout=stdout,stderr=stderr);print(json.dumps({'label':label,'pid':p.pid}),flush=True)
  code=p.wait(timeout=150)
 report={'command':command,'actual_exit':code,'stderr_bytes':(OUT/(label+'01.stderr.txt')).stat().st_size};(OUT/(label+'01.json')).write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report),flush=True)
 if code!=0 or report['stderr_bytes']:raise RuntimeError(label)
