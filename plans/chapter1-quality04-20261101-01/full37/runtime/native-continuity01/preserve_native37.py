"""Narrow native progress audit/backup; no engine, source edit or profile write."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path('C:/Project/d2r-combat-baseline')
FULL=ROOT/'plans/chapter1-quality04-20261101-01/full37'
HERE=Path(__file__).resolve().parent
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):
    with Path(path).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,ensure_ascii=False);f.write('\n')
prior=FULL/'USER-PRESERVATION-ADDENDUM01.json'
original9=read(FULL.parent/'full36/USER-PRESERVATION-ADDENDUM02.json')['user_pins']
pins=read(prior)['user_pins']
assert len(original9)==9 and len(pins)==12
assert all(sha(path)==value for path,value in original9.items())
folder=Path.home()/'AppData/Roaming/AshenCloisterChapterOneQuality37'
profile_path=folder/'chapter-one-profile-v1.json'
for path,value in pins.items():
    if Path(path)!=profile_path:assert sha(path)==value,path
before=read(FULL/'USER-CONTINUITY.json')['source_profile_before']
after=read(profile_path)
changed=[key for key in before if before[key]!=after[key]]
assert set(before)==set(after) and set(changed)=={'items','next_id','receipts','revision'}
assert after['items'][:len(before['items'])]==before['items'] and len(after['items'])==len(before['items'])+1==23
assert after['items'][-1]['storage_id']==before['next_id']==23 and after['next_id']==24
assert after['receipts'][:len(before['receipts'])]==before['receipts'] and len(after['receipts'])==len(before['receipts'])+1
assert after['receipts'][-1]=='23588-1793981818-78031202'
assert after['revision']==before['revision']+1==3 and after['completed_runs']==1 and after['equipped']=={'body':1}
new_journal=folder/'chapter-one-profile-v1.revision-000003-23588-133437322.json'
assert new_journal.is_file() and sha(new_journal)==sha(profile_path)
assert set(folder.glob('*.json'))=={Path(name) for name in pins if Path(name).parent==folder}|{new_journal}
pins[str(profile_path)]=sha(profile_path)
pins[str(new_journal)]=sha(new_journal)
assert len(pins)==13
freeze=read(FULL/'FINAL-SOURCE-FREEZE.json')
assert len(freeze)==165 and all(sha(ROOT/name)==value for name,value in freeze.items())
build=read(FULL/'build/build.json')
assert sha(build['exe'])==build['sha256']
destination=HERE/'post-manual-preserved'
destination.mkdir()
copies=[]
for name,value in pins.items():
    source=Path(name);target=destination/source.parent.name/source.name
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as f:f.write(source.read_bytes())
    assert sha(target)==value and sha(source)==value
    copies.append({'source':str(source),'copy':str(target),'sha256':value,'bytes':target.stat().st_size})
write(destination/'MANIFEST.json',{'scope':'Current13 legitimate user state byte copies; source files unmodified','files':copies,'all13_match':True})
screenshots={name:sha(HERE/name) for name in ['menu.jpg','stash-body1.jpg','cold-start-169.jpg','growth-rank2.jpg','manual-defeat-25s.jpg']}
result={'continuity_pass':True,'full_manual_victory_pass':False,'full_manual_attempt_outcome':'defeat','manual_attempt':{'elapsed_display_seconds':25,'kills':39,'level':3,'source':'Root actual Computer Use observations and retained JPEGs; this worker did not replay UI'},'observations':['Native37 menu22items','Stashbody1diamond andcompleted1','Coldstart169/169HP','Rank2growth selected','Manualdefeat25s/39kills/Lv3; slowUIroundtrip andgrowthdialog consumedmovement input; not a fullmanual victory'],'screenshots':screenshots,'profile_checks':{'original9_unchanged':True,'old37journal1and2_unchanged':True,'old22_items_exact_prefix':True,'old_receipts_exact_prefix':True,'changed_keys_only':changed,'revision':3,'items':23,'next_id':24,'completed_runs':1,'equipped':{'body':1},'appended_item':after['items'][-1],'new_receipt':after['receipts'][-1],'new_journal_matches_profile':True,'current_pin_count':13},'product_checks':{'freeze165_unchanged':True,'exe_unchanged':True,'exe_sha256':build['sha256']},'latest_user_manifest':str(FULL/'USER-PRESERVATION-ADDENDUM02.json'),'scope':'Preservation audit of legitimate native progress after failed short manual attempt. No rollback/delete/grant/profile rewrite, no engine/GPU/audio/performance approval.'}
write(HERE/'RESULT.json',result)
write(FULL/'USER-PRESERVATION-ADDENDUM02.json',{'user_pins':pins,'reason':'Root actual native37 continuityPASS then failed25sec manual attempt legitimately appendedstorage23/receipt/revision3. Preserveall23items andnewjournal; original23/29/36nine and37oldjournal1/2 unchanged. Previous12pin adoption manifest is historical, not a rollback target.','prior_manifest':{'path':str(prior),'sha256':sha(prior)},'native_result':{'path':str(HERE/'RESULT.json'),'sha256':sha(HERE/'RESULT.json')},'backup_manifest':{'path':str(destination/'MANIFEST.json'),'sha256':sha(destination/'MANIFEST.json')}})
print(json.dumps({'audit':'PASS','continuity_pass':True,'full_manual_victory_pass':False,'current_pins':13,'sourcefreeze165_unchanged':True,'new_manifest':str(FULL/'USER-PRESERVATION-ADDENDUM02.json')}))
