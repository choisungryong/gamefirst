from pathlib import Path
import subprocess,json
HERE=Path(__file__).resolve().parent
source=HERE/'mage_export_research03.py';target=HERE/'mage_export_research04.py';assert not target.exists()
s=source.read_text(encoding='utf-8').replace("from mathutils import Vector","from mathutils import Vector, Matrix").replace("/gltf-preview-03')","/gltf-preview-04')")
s=s.replace("-.10-.60*k,-.13+.43*k","-.10-.24*k,-.13+.22*k").replace("-.10-.30*k,-.13+.20*k","-.10-.14*k,-.13+.12*k")
s=s.replace("math.radians(7)*k,0,math.radians(-9)*k","math.radians(4)*k,0,math.radians(-4)*k")
s=s.replace("shift('body',(0,.32*k,-.87*k));rig.pose.bones['body'].rotation_euler=(math.radians(-68)*k,0,math.radians(12)*k)","rig.pose.bones['spine.02'].rotation_euler=(math.radians(-10)*k,0,0)")
s=s.replace("frames.append({p.name:p.matrix.copy() for p in deform.pose.bones})",'''matrices={p.name:p.matrix.copy() for p in deform.pose.bones}
        if clip=='death':
            t=(f-1)/(count-1);k=t*t*(3-2*t)
            rotation=Matrix.Rotation(math.radians(-88)*k,4,'X') @ Matrix.Rotation(math.radians(7)*k,4,'Z')
            evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
            points=[rotation @ (mesh.matrix_world @ v.co) for v in evaluated.data.vertices]
            lift=max(0,-min(v.z for v in points))
            transform=Matrix.Translation((0,0,lift)) @ rotation
            matrices={name:transform @ m for name,m in matrices.items()}
        frames.append(matrices)''')
target.write_text(s,encoding='utf-8')
command=['C:/Project/rea-tools/blender-4.5.15-windows-x64/blender.exe','--background','--disable-autoexec',
 'C:/Project/game-research/art-sources/oga-mage-20261101-01/motion-preview-01/mage_motion_research.blend','--python-exit-code','1','--python',str(target)]
r=subprocess.run(command,capture_output=True,timeout=180)
data={'command':command,'actual_exit':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace'),
 'prior_attempt':'Godot03 rig loads and runs, but cast shoulder stretch and death floor penetration rejected. 04 lowers reach and applies whole-rig fall with evaluated-mesh ground clearance.'}
with (HERE/'mage-export04-execution.json').open('x',encoding='utf-8') as f:json.dump(data,f,indent=2)
print(json.dumps(data))
