from pathlib import Path
import json,shutil,hashlib,re
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote
HERE=Path(__file__).resolve().parent;ROOT=Path('C:/Project/d2r-combat-baseline');BOOK=HERE/'book-v04/dist'
draft=BOOK.parent/'draft-before-gpu-02';assert not draft.exists();draft.mkdir()
for p in BOOK.glob('*'):
 if p.is_file():shutil.copy2(p,draft/p.name)
capture=ROOT/'builds/chapter1/chapter1-full-candidate-20261101-09/qa-captures/gpu-preview01'
mapping={'opening09.png':'run-001-frame-020.png','nave09.png':'run-001-frame-150.png','sanctuary09.png':'run-001-frame-270.png','boss09.png':'run-001-frame-330.png','victory09.png':'state-0012-run-001-victory.png','inventory09.png':'state-0013-run-001-inventory.png'}
for target,source in mapping.items():shutil.copy2(capture/source,BOOK/'scenes'/target)
def figure(name,caption):return f'<figure><img loading="lazy" src="scenes/{name}" alt="{caption}"><figcaption>{caption}</figcaption></figure>'
def edit(name,fn):
 p=BOOK/(name+'.html');p.write_text(fn(p.read_text(encoding='utf-8')),encoding='utf-8')
edit('index',lambda s:re.sub(r'<figure>.*?</figure>',figure('nave09.png','후보09 실제GPU 2분29초. 화염 진화·보조 기술·장비가 연결된 성가대 전투. 자동 입력 검증이며 수동 플레이·최종 품질 승인이 아닙니다.'),s,count=1,flags=re.S))
edit('chapter',lambda s:s.replace('<h2 id="nave">',figure('opening09.png','후보09 앞뜰: 전투와 봉인 목표')+'<h2 id="nave">').replace('<h2 id="sanctuary">',figure('nave09.png','실제 이동해 도착한 성가대')+'<h2 id="sanctuary">').replace('<h2>회복과 선택</h2>',figure('sanctuary09.png','재의 성소: 다음 보스를 준비하는 무리 전투')+figure('boss09.png','실제 보스 전투의 생명력과 전장')+'<h2>회복과 선택</h2>'))
edit('profile',lambda s:s.replace('저장 revision을 남기고 손상된 원본이나 다른 실행의 변경은 덮어쓰지 않습니다.','저장 revision을 남기고 손상된 원본은 보존합니다. 저장 전에 외부 변경을 확인하며, 다중 프로세스 잠금과 전원 손실 내구성 검수는 남아 있습니다.').replace('</main>',figure('inventory09.png','완료한 판의 획득 장비 비교. 이 검증 실행은 보관함 저장을 껐으며, 지속 보관함에 저장된 화면이 아닙니다.')+'</main>'))
rows=json.loads((HERE/'NORMAL-RELEASE-RESULTS.json').read_text(encoding='utf-8'))['runs']
table='<table><thead><tr><th>주력</th><th>완료 시간</th><th>처치</th><th>주력 진화</th></tr></thead><tbody>'
for r in rows:
 sec=r['seconds'];table+=f'<tr><td>{dict(ember="화염",frost="냉기",arc="번개")[r["primary"]]}</td><td>{int(sec)//60}:{int(sec)%60:02d}</td><td>{r["kills"]}</td><td>확인</td></tr>'
table+='</tbody></table><p>실행 파일의 headless/고정60FPS 정상 입력 정책 결과입니다. HP/XP 지급 없이 이동·성장 선택·장비·회복약을 사용했습니다. 모두 실제 보스 처치와 소유 고유 보상이 있으며 종료0/stderr0입니다. 수동 플레이나 실제 성능 수치가 아닙니다.</p>'
gpu_log=HERE/'runtime/gpu-preview01/stdout.txt'
text=gpu_log.read_text(encoding='utf-8',errors='replace')
results=[json.loads(s.split('FULL_CHAPTER_RUNTIME_RESULT ',1)[1]) for s in text.splitlines() if 'FULL_CHAPTER_RUNTIME_RESULT ' in s]
victory=next(r for r in results if r['mode']=='victory')
execution=json.loads((HERE/'runtime/gpu-preview01/execution.json').read_text(encoding='utf-8'))
assert execution['actual_exit']==0 and execution['stderr_bytes']==0 and victory['tick']==21749
gpu={'actual_exit':0,'stderr_bytes':0,'seconds':victory['tick']/60,'kills':victory['kills'],'level':victory['growth']['level'],'owned_reward':victory['elite_reward_uid'],'captures':execution['capture_count'],'history':victory['chapter']['history'],'manual_after_victory':'CUA opened inventory, scrolled, selected ash_bloom and observed -10%/+1projectile/fire death burst comparison. Final equip click arrived after autoquit and was not confirmed.','scope':'Real RTX2070SUPER/Forward+ run with normal QA input/max-fps120/captures/profile-off. Not manual full run, heard audio, or formal performance.'}
with (HERE/'GPU-FULL-RESULT.json').open('x',encoding='utf-8') as f:json.dump(gpu,f,ensure_ascii=False,indent=2)
extra='<h2>후보09 실행 파일 검증</h2>'+table+figure('victory09.png','실제GPU 실행도6분2초/3185처치/레벨11로 완료했습니다. 선택 화면 정지와 종료 오디오 경고는 이 실행에서 재발하지 않았습니다.')
edit('validation',lambda s:s.replace('<h2>아직 승인하지 않은 것</h2>',extra+'<h2>아직 승인하지 않은 것</h2>').replace('후보09의 실제GPU 전체 실행과 세 빌드의 패키지 실행 결과는 별도 실행 보고서로 갱신합니다.','후보09 실제GPU 전체 실행과 세 빌드의 패키지 실행 결과는 확인했고 원시 로그와 상태를 보존했습니다.'))
class Links(HTMLParser):
 def __init__(self):super().__init__();self.urls=[]
 def handle_starttag(self,tag,attrs):
  for key,value in attrs:
   if key in ['src','href'] and value:self.urls.append(value)
missing=[];checked=0
for p in BOOK.glob('*.html'):
 parser=Links();parser.feed(p.read_text(encoding='utf-8'))
 for url in parser.urls:
  parsed=urlparse(url)
  if parsed.scheme or not parsed.path:continue
  target=(p.parent/unquote(parsed.path)).resolve();checked+=1
  if not target.is_file():missing.append({'page':p.name,'url':url})
assert not missing,missing
manifest={str(p.relative_to(BOOK)):hashlib.sha256(p.read_bytes()).hexdigest() for p in BOOK.rglob('*') if p.is_file()}
with (BOOK.parent/'REVISION-02.json').open('x',encoding='utf-8') as f:json.dump({'files':manifest,'local_links_checked':checked,'missing':missing,'draft':str(draft),'browser':'All6page navigation titles read; desktop screenshots index/loot/animation; first image horizontal overflow fixed and reloaded. Mobile/print not verified.'},f,ensure_ascii=False,indent=2)
print(json.dumps({'gpu':{k:v for k,v in gpu.items() if k!='history'},'book_files':len(manifest),'local_links':checked,'missing':missing},ensure_ascii=False))
