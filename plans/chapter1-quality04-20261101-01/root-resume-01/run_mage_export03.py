from pathlib import Path
import subprocess,json,struct
HERE=Path(__file__).resolve().parent
source=HERE/'mage_export_research02.py';target=HERE/'mage_export_research03.py';assert not target.exists()
s=source.read_text(encoding='utf-8').replace("/gltf-preview-02')","/gltf-preview-03')")
s=s.replace('mesh.parent=root;deform.parent=root','deform.parent=root;mesh.parent=deform')
s=s.replace('export_extras=False,export_yup=True)','export_extras=False,export_yup=True,export_influence_nb=8)')
target.write_text(s,encoding='utf-8')
command=['C:/Project/rea-tools/blender-4.5.15-windows-x64/blender.exe','--background','--disable-autoexec',
 'C:/Project/game-research/art-sources/oga-mage-20261101-01/motion-preview-01/mage_motion_research.blend','--python-exit-code','1','--python',str(target)]
r=subprocess.run(command,capture_output=True,timeout=180)
data={'command':command,'actual_exit':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace'),
 'prior_attempt':'02 exported but warned nonparent mesh and 4-weight truncation. 03 parents mesh to skin and exports up to8 influences.'}
with (HERE/'mage-export03-execution.json').open('x',encoding='utf-8') as f:json.dump(data,f,indent=2)
print(json.dumps(data))
if r.returncode==0:
 p=Path('C:/Project/game-research/art-sources/oga-mage-20261101-01/gltf-preview-03/mage_animated.glb');b=p.read_bytes();n,k=struct.unpack_from('<II',b,12);j=json.loads(b[20:20+n])
 info={'animations':[(a['name'],len(a['channels'])) for a in j.get('animations',[])],'skins':[len(s['joints']) for s in j.get('skins',[])],
       'mesh_attributes':[list(pr['attributes']) for me in j['meshes'] for pr in me['primitives']]}
 with (HERE/'mage-export03-structure.json').open('x',encoding='utf-8') as f:json.dump(info,f,indent=2)
 print(json.dumps(info))
