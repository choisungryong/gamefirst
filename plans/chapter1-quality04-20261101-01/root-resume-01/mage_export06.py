from pathlib import Path
import subprocess,json
HERE=Path(__file__).resolve().parent
source=HERE/'mage_export_research05.py';target=HERE/'mage_export_research06.py';assert not target.exists()
s=source.read_text(encoding='utf-8').replace('/gltf-preview-05\'','/gltf-preview-06\'')
s=s.replace("(-sign*.23,-.10,-.13)","(-sign*.25,-.13,.02)")
s=s.replace(".36*math.cos(a),.15*max(0,math.sin(a))",".48*math.cos(a),.23*max(0,math.sin(a))")
s=s.replace("(-sign*.23,-.10-.15*math.cos(a),-.08+.03*math.sin(a))","(-sign*.25,-.13-.18*math.cos(a),.08+.07*math.sin(a))")
s=s.replace("shift('body',(0,0,.012+.018*math.cos(phase*2)))","shift('body',(0,-.05,.035-.025*math.cos(phase*2)))")
s=s.replace("math.radians(8),0,math.radians(3)*math.cos(phase)","math.radians(12),0,math.radians(3)*math.cos(phase)")
s=s.replace("rig.pose.bones['spine.02'].rotation_euler=(math.radians(-10)*k,0,0)","""rig.pose.bones['spine.02'].rotation_euler=(math.radians(-10)*k,0,0)
        shift('body',(0,0,-.24*k))
        for side,sign in [('L',1),('R',-1)]:
            shift('foot_control.'+side,(0,0,.24*k))
            shift('hand_target.'+side,(-sign*.14,-.12,-.08))""")
s=s.replace("'changes':'Legacy material conversion, own IK poses baked into deformation skeleton, metre root. Research only, not runtime adoption.'","'changes':'5 weight repairs; own stride2.1m run with raised swing, forward lean and bent arms, ready idle, knee-flexed ground-safe fall; baked IK and metre conversion. Research before runtime comparison.'")
target.write_text(s,encoding='utf-8')
command=['C:/Project/rea-tools/blender-4.5.15-windows-x64/blender.exe','--background','--disable-autoexec',
 'C:/Project/game-research/art-sources/oga-mage-20261101-01/motion-preview-01/mage_motion_research.blend','--python-exit-code','1','--python',str(target)]
r=subprocess.run(command,capture_output=True,timeout=180)
with (HERE/'mage-export06-execution.json').open('x',encoding='utf-8') as f:json.dump({'command':command,'actual_exit':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace')},f,indent=2)
print(json.dumps({'actual_exit':r.returncode,'stderr':r.stderr.decode('utf-8','replace'),'stdout_tail':r.stdout.decode('utf-8','replace')[-600:]}))
