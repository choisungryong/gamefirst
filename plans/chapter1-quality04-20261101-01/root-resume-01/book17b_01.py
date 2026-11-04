from pathlib import Path
import json,hashlib,re,shutil,os
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';OLD=B/'full17/book-v09/dist';BOOK=B/'full17b/book-v10/dist';assert not BOOK.exists();shutil.copytree(OLD,BOOK)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:os.path.relpath(p,BOOK).replace('\\','/')
build=json.loads((B/'full17b/build/build.json').read_text(encoding='utf-8'))
for p in BOOK.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 def repair(m):
  prefix,v=m.group(1),m.group(2)
  if v.startswith(('http:','https:','#','data:')):return m.group(0)
  raw,sep,anchor=v.partition('#');target=(OLD/raw).resolve()
  if not target.is_relative_to(OLD.resolve()):v=rel(target)+(sep+anchor if sep else '')
  return prefix+'="'+v+'"'
 s=re.sub(r'(src|href)="([^"]+)"',repair,s).replace('제작 도감 v09','제작 도감 v10').replace('후보17 / 이전 항목은 본문 번호 유지','후보17b / 원본17·이전 항목은 본문 번호 유지')
 p.write_text(s,encoding='utf-8')
p=BOOK/'index.html';s=p.read_text(encoding='utf-8');s=s.replace('후보17 실행 파일','후보17b 실행 파일').replace('chapter1-full-candidate-20261102-17/','chapter1-full-candidate-20261102-17b/').replace('f016bcaefbf169f4c1b32bc641130b3c936d3f8c90b7d5f51af84bfb22813a6b',build['sha256'])
s=s.replace('후보17 표현 연구:','HUD17 표현 연구(17b 동일 소스):')
s=s.replace('</main>','<p class="note">17b는 새 석재를 보행 경계 밖으로 옮긴 수정본입니다. 전체 정상GPU는 원17, 경계 화면은17b로 구분합니다. <a href="'+rel(B/'full17b/STATUS.ko.md')+'">17b 상태와 검수 범위</a></p></main>');p.write_text(s,encoding='utf-8')
shutil.copy2(B/'full17b/runtime/boundary01/captures/boundary-z19.png',BOOK/'scenes/boundary17b.png')
gpu=json.loads((B/'full17/runtime/gpu-cold01/RESULT.json').read_text(encoding='utf-8'));assert gpu['observer']['shatters']==840
shutil.copy2(B/'full17/runtime/gpu-cold01/captures/victory-after-1.60.png',BOOK/'scenes/packaged17-reward.png')
p=BOOK/'experience17.html';s=p.read_text(encoding='utf-8');s=s.replace('</main>','''<h2>보행 경계 밖으로 옮긴17b</h2><figure><img loading="lazy" src="scenes/boundary17b.png" alt="17b 실제 패키지의 경계 연구 화면"><figcaption>17의새기둥이보행범위안에있던문제를수정했습니다.17b실제패키지GPU에서114석재의바깥코너최소|z|20.4966을확인했습니다.영웅을z19에직접놓은fixture이며정상한판장면이아닙니다.경계에서보이는바닥끝/빈배경은별도미해결공간문제입니다.</figcaption></figure><h2>원17 실제 패키지의 전체GPU</h2><figure><img loading="lazy" src="scenes/packaged17-reward.png" alt="후보17 실제 패키지 첫승리 후 보상"><figcaption>정상획득빌드/seed90131의실제원17EXE전체GPU.6분37.7초/3451처치/파쇄840(냉기직접처치823),16과10게임상태동일,exit0/stderr0.보스사망뒤1.6초보상화면입니다.17b전체GPU로세지않으며수동/실청취/성능승인은아닙니다.</figcaption></figure></main>''');p.write_text(s,encoding='utf-8')
refs=[];missing=[]
for p in BOOK.glob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs.append([p.name,v])
  if not (p.parent/v.split('#')[0]).resolve().is_file():missing.append([p.name,v])
report={'pages':len(list(BOOK.glob('*.html'))),'local_references':len(refs),'missing':missing,'files':{str(p.relative_to(BOOK)).replace('\\','/'):sha(p) for p in BOOK.rglob('*') if p.is_file()},'scope':'17 actual fullGPU and17b decorative edge correction explicitly separated. Original14/16/17 images retain source labels. Browser QA pending.'};(BOOK.parent/'BUILD.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');assert not missing,missing;print(str(BOOK),flush=True)
