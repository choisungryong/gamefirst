from pathlib import Path
from PIL import Image
import json,hashlib
ROOT=Path(r"C:\Project\d2r-combat-baseline"); ART=ROOT/"chapter1/art"
EVID=ROOT/"plans/chapter1-c2-20261031-01/art"
prompts=json.loads((EVID/"GENERATION-PROMPTS.json").read_text(encoding="utf-8"))["prompts"]
prompts["elite_actions"]=json.loads((EVID/"ELITE-ACTION-PROMPT.json").read_text(encoding="utf-8"))["prompt"]
base=r"C:\Users\twins\.codex\generated_images\01a18dbd-c8b9-7ea0-a8f0-42956fd4b51d"
specs=[
 ("terrain/cloister_ground_v01.png","terrain","09c69a53-68ac-4fcb-9875-dfaa8bc98973",[],"candidate_ground_material"),
 ("actors/battle_mage_walk_4x4_v01.png","hero_initial","7d80c7ce-5025-414f-86b8-970cc809d1e5",[],"preserved_rejected_layout_proof"),
 ("actors/hero.png","hero_repack","3d074285-9364-442a-aaa1-09ae387fb3cc",["actors/battle_mage_walk_4x4_v01.png"],"playable_2_5d_candidate"),
 ("actors/hero_actions.png","hero_actions","4217486e-5a43-45b4-8e33-949f4aac6bc6",["actors/hero.png"],"playable_2_5d_candidate"),
 ("actors/walker.png","walker","09874ab1-5a4b-4af0-a09a-c5dc8cc7712a",None,"playable_2_5d_candidate"),
 ("actors/ranged.png","ranged","e31f7df6-4633-4107-8297-4c5c864e38cb",None,"playable_2_5d_candidate"),
 ("actors/charger.png","charger","b174cbea-4dca-418c-9106-c3a40b64b9e4",None,"playable_2_5d_candidate"),
 ("actors/walker_actions.png","walker_actions","7e81fbd2-9402-4358-bd1d-173a5d7f44bb",["actors/walker.png"],"playable_2_5d_candidate"),
 ("actors/ranged_actions.png","ranged_actions","1d61e19f-2e65-42c3-80bd-d731a7f993f4",["actors/ranged.png"],"playable_2_5d_candidate"),
 ("actors/charger_actions.png","charger_actions","d4d97772-875d-4052-9ec3-8a42307b011f",["actors/charger.png"],"playable_2_5d_candidate"),
 ("actors/elite.png","elite","45f68cd2-97c8-4d2c-b4a0-a8c8b4064cc4",[],"playable_2_5d_candidate"),
 ("actors/elite_actions.png","elite_actions","4468bbb4-5f29-46b3-abb6-909372d66ef6",["actors/elite.png"],"playable_2_5d_candidate")]
assets=[]
for rel,key,gid,refs,status in specs:
 p=ART/rel; im=Image.open(p); orig=Path(base)/("exec-"+gid+".png")
 assets.append({"path":"chapter1/art/"+rel,"format":"PNG raster","width":im.width,"height":im.height,"mode":im.mode,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"original_generation_path":str(orig),"original_preserved":orig.exists(),"original_sha256":hashlib.sha256(orig.read_bytes()).hexdigest() if orig.exists() else None,"prompt_key":key,"prompt":prompts[key],"reference_inputs":refs,"reference_note":"Earlier generation call reference list was not retained in compacted context; no external/protected asset was copied." if refs is None else "Only independent generated local reference assets, when listed.","status":status,"authoring":"Built-in OpenAI image_gen.imagegen during authorized project development; model identifier not exposed.","license":"Generated project asset; no third-party asset license asserted. Not labeled CC0. No protected source-game code/art copied."})
metas=[]
for p in sorted((ART/"actors").glob("*.json")):
 metas.append({"path":str(p.relative_to(ROOT)).replace("\\","/"),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
ledger={"schema":1,"date_local":"2026-10-31","scope":"Chapter1 C2 first playable 2.5D art candidate; final quality approval pending","generation_mode":"built-in image_gen.imagegen; no CLI/API fallback; transparency preserved; no image pixels altered by analysis scripts","approval":"Root approved adult dark-fantasy 2.5D style for first playable candidate only, preserving rigged GLB alternative brief.","assets":assets,"metadata":metas,"limitations":["Raster sprite atlases, not rigged 3D models.","Four directions with four walk keyframes each; dedicated idle clip absent (held walk keyframe).","Cast/attack, hit and death have four actual poses each, south facing only.","PPM/feet anchors are initial calibration. Runtime view agent must inspect actual world scale and contact alignment.","No authored directional action clips, model rigs, animation blending or new independent equipment-on-body variants.","Terrain seamlessness was requested, but actual engine seam/tiling test has not been performed by art agent.","Initial battle_mage_walk_4x4_v01 is preserved as a layout proof and should not be runtime uniform-grid cropped."],"researched_not_adopted":[{"name":"Quaternius RPG Character Pack","url":"https://quaternius.com/packs/rpgcharacters.html","license_observation":"Official page identifies CC0; rigged animated low-poly format route. Not downloaded or adopted because appearance did not meet adult grounded target."},{"name":"Gobkit free inventory","url":"https://gobkit.com/api/free","license_observation":"Official inventory exposes downloadable GLBs and pack licenses. No model downloaded or adopted; no blanket license assumed."}],"preservation_manifest":"C:/Project/game-research/implementation-backups/chapter1-c2-before-20261031-01/manifest.json"}
(ART/"ASSET-LEDGER.json").write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"assets":len(assets),"meta":len(metas),"copies_match":all(x["sha256"]==x["original_sha256"] for x in assets)},indent=2))

