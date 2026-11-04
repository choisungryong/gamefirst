from pathlib import Path
HERE=Path(__file__).parent
s=(HERE/'skeleton_preview03.gd').read_text(encoding='utf-8')
s=s.replace('const CLIPS := ["idle","walk","run","attack_slam","attack_fan","attack_cross","hit","death","idle_alert"]','const CLIPS := ["idle","walk","windup_slam","slam","windup_fan","fan","hit","death"]')
s=s.replace('res://art/skeleton_outlaw.glb','res://art/chained_demon_animated.glb').replace('camera.size=4.8','camera.size=6.0').replace('Vector3(0,1.15,0)','Vector3(0,1.6,0)')
s=s.replace('\n\tskeleton.set_bone_pose_scale(skeleton.find_bone("ORG-head"),Vector3.ONE*.72)','')
s=s.replace('CC0 research','CC-BY3.0 research').replace('SKELETON_PREVIEW_READY','DEMON_PREVIEW_READY').replace('Isolated author-clip research, not runtime or art approval; head scaled.72, hair/metaljaw removed','Own eight clips on Mophs rig, legacy material/weights repaired; research, not runtime/art approval')
target=HERE/'demon_preview04.gd';assert not target.exists();target.write_text(s,encoding='utf-8')
s=(HERE/'run_skeleton_preview03.py').read_text(encoding='utf-8')
s=s.replace('oga-skeleton-outlaw-20261101-01','oga-chained-demon-20261101-01').replace('godot-preview03','godot-preview04').replace('skeleton-outlaw-preview-20261101-03','chained-demon-preview-20261101-04')
s=s.replace('godot-convert02/derived/skeleton_outlaw.glb','motion-04/chained_demon_animated.glb').replace('art/skeleton_outlaw.glb','art/chained_demon_animated.glb').replace('skeleton_preview03.gd','demon_preview04.gd').replace('Skeleton author clips research','Chained demon own clips research')
target=HERE/'run_demon_preview04.py';assert not target.exists();target.write_text(s,encoding='utf-8')
print(str(target))
