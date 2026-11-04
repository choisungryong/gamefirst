"""Read only comparisons against existing pins; no historical test is rerun."""
from pathlib import Path
import hashlib
import json
import sys

ROOT=Path('C:/Project/d2r-combat-baseline')
C2=ROOT/'plans/chapter1-c2-20261031-01'
BACKUP=Path('C:/Project/game-research/implementation-backups/chapter1-c2-docs-before-20261031-01')
BEFORE=Path('C:/Project/game-research/implementation-backups/chapter1-c2-before-20261031-01/manifest.json')
PACKAGE=C2/(sys.argv[1] if len(sys.argv)>1 else 'package-candidate02')
OUT=C2/'FINAL-PRESERVATION.json'
assert not OUT.exists(), 'New evidence ID required'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def compare(root,manifest):
    return [{'path':p,'expected':s,'actual':sha(root/p) if (root/p).is_file() else None} for p,s in manifest.items() if not (root/p).is_file() or sha(root/p)!=s]
oldbuild=ROOT/'evidence/phase7/builds/phase7-candidate-20261030-01'
oldpin=read(oldbuild/'source-manifest.json')
oldcurrent=compare(ROOT,oldpin)
oldsnapshot=compare(oldbuild/'source',oldpin)
oldexe=ROOT/'builds/phase7/phase7-candidate-20261030-01/AshenCloister-phase7.exe'
oldexe_expected='5a56ccb5a13973a7d223d5d4a71b75a0c51ad89db6c78b564c1b10b4c09c6f29'
profiles=[]
for entry in read(BEFORE)['native_profiles']:
    p=Path(entry['path'])
    actual=sha(p) if p.is_file() else None
    profiles.append({'path':str(p),'expected_sha256':entry['sha256'],'actual_sha256':actual,'matches':actual==entry['sha256']})
backup=read(BACKUP/'manifest.json')
oldbook=ROOT/'plans/chapter1-preproduction-20261031-01/book/dist'
oldbook_mismatch=compare(oldbook,backup['book_v01'])
zip_v01=ROOT/'plans/chapter1-preproduction-20261031-01/CHAPTER1-PRODUCTION-BOOK-20261031-01.zip'
docproof=[]
for name,expected in backup['documents'].items():
    old=(BACKUP/name).read_bytes();now=(ROOT/name).read_bytes()
    docproof.append({'path':name,'backup_sha256':sha(BACKUP/name),'expected_before_sha256':expected,'after_sha256':sha(ROOT/name),'old_body_exact_suffix':now.endswith(old),'prefix_bytes':len(now)-len(old)})
corebase=ROOT/'chapter1/evidence/core-pilot-20261031-03'
corepin={r['path']:r['sha256'] for r in read(corebase/'source-manifest.json')}
corecurrent=compare(ROOT,corepin)
coresnapshot=compare(corebase/'source',corepin)
build=read(PACKAGE/'build.json')
runtimepin=read(PACKAGE/'source-manifest.json')
current=compare(ROOT,runtimepin)
stage=compare(Path(build['stage']),runtimepin)
exe=Path(build['exe'])
result={
    'date_local':'2026-10-31 Asia/Seoul',
    'old_phase7_source_count':len(oldpin),'old_phase7_current_mismatches':oldcurrent,'old_phase7_snapshot_mismatches':oldsnapshot,
    'old_phase7_exe':{'path':str(oldexe),'expected_sha256':oldexe_expected,'actual_sha256':sha(oldexe),'matches':sha(oldexe)==oldexe_expected},
    'native_profiles':profiles,'documents':docproof,
    'v01_book_files':len(backup['book_v01']),'v01_book_mismatches':oldbook_mismatch,'v01_book_zip_sha256':sha(zip_v01),'v01_book_zip_matches':sha(zip_v01)==backup['book_v01_zip_sha256'],
    'core03_files':len(corepin),'core03_current_mismatches':corecurrent,'core03_snapshot_mismatches':coresnapshot,
    'current_package':{'proof':str(PACKAGE),'source_count':len(runtimepin),'current_mismatches':current,'staging_mismatches':stage,'exe_sha256':sha(exe),'expected_exe_sha256':build['sha256'],'exe_matches':sha(exe)==build['sha256']},
    'scope':'Pinned selected sources, snapshots, EXEs, current native profiles and v01 book only. Does not prove byte preservation of every historical unpinned evidence file or recover previously lost reports.'
}
result['success']=not any([oldcurrent,oldsnapshot,oldbook_mismatch,corecurrent,coresnapshot,current,stage]) and result['old_phase7_exe']['matches'] and all(p['matches'] for p in profiles) and all(d['old_body_exact_suffix'] and d['backup_sha256']==d['expected_before_sha256'] for d in docproof) and result['v01_book_zip_matches'] and result['current_package']['exe_matches']
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
sys.exit(0 if result['success'] else 1)
