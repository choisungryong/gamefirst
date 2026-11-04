from pathlib import Path
import json,re,hashlib
ROOT=Path('C:/Project/d2r-combat-baseline')
OUT=Path(__file__).resolve().parent
paths=['chapter1/chapter_view.gd','chapter1/view/cloister_world.gd','chapter1/view/cloister_world_quality03.gd','chapter1/view/cloister_actors.gd','chapter1/view/cloister_effects.gd','chapter1/view/cloister_hud.gd','chapter1/presentation/combat_audio.gd','chapter1/view/flame_bloom.gdshader','chapter1/view/cloister_props_quality03.gdshader','chapter1/view/cloister_ground_quality03.gdshader']
patterns={
 'filesystem_writes':r'FileAccess\.WRITE|make_dir|save_png|store_string|remove_absolute|rename_absolute',
 'process_network':r'OS\.(execute|create_process|shell_open)|HTTPRequest|HTTPClient',
 'presenter_core_assignment':r'run\.[A-Za-z_]+\s*=(?!=)|run\.(hero|enemies|projectiles|items).*\s=(?!=)',
 'unbounded_loop':r'\bwhile\b',
 'legacy_quality_reference':r'cloister_ground_v01|expedition_audio|hero_run_v01|attempts/',
 'allocation':r'\.new\('}
result={'files':{},'scope':'Static text candidates manually reviewed; a match is not automatically a defect.'}
for name in paths:
 p=ROOT/name;text=p.read_text(encoding='utf-8');lines=text.splitlines()
 result['files'][name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'matches':{label:[{'line':i,'text':line.strip()} for i,line in enumerate(lines,1) if re.search(pattern,line)] for label,pattern in patterns.items()}}
target=OUT/'anti-pattern-scan.json';assert not target.exists()
target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'files':len(paths),'output':str(target)}))
