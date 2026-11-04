"""New immutable quality03 packaging/movie workflow. Never edits product sources.

Godot 4.5.1 local --help is the CLI authority; movie writing forces fixed FPS.
An offline movie is not a real-time performance or manual-play measurement.
No build/movie action runs by importing this module or by running `prepare`.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys

ROOT = Path("C:/Project/d2r-combat-baseline")
HERE = Path(__file__).resolve().parent
BUILD_ID = "chapter1-c2-candidate-20261101-03"
STAGE = Path("C:/Project/game-research/build-staging") / BUILD_ID
OUTPUT = ROOT / "builds/chapter1" / BUILD_ID
PROOF = HERE / "build"
ENGINE = Path("C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe")
OLD_PROOF = ROOT / "plans/chapter1-c2-20261031-01/package-candidate02"
OLD_STAGE = Path("C:/Project/game-research/build-staging/chapter1-c2-candidate-20261031-02")
OLD_EXE = ROOT / "builds/chapter1/chapter1-c2-candidate-20261031-02/AshenCloister-Chapter1.exe"
BACKUP = Path("C:/Project/game-research/implementation-backups/chapter1-quality03-before-20261031-02/manifest.json")
SCOPE = "C2 representative encounter; not full5-8min chapter, SACRATA-quality approval, manual play, or formal performance"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    path = Path(path)
    assert not path.exists(), "Preserve prior evidence: " + str(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fresh_dir(path):
    assert not path.exists(), "Choose a new path; preserve existing: " + str(path)
    path.mkdir(parents=True)


def runtime_paths():
    # Explicit adopted closure. No glob can accidentally adopt a rejected art attempt.
    names = {"chapter1/Chapter1.tscn", "chapter1/chapter_view.gd", "chapter1/data/growth.json",
             "combat/combat_resolver.gd", "combat/stat_block.gd", "chapter1/presentation/combat_audio.gd"}
    names.update("chapter1/core/" + s + ".gd" for s in ("combat_run", "growth_catalog", "run_growth"))
    names.update("chapter1/view/" + s + ".gd" for s in (
        "cloister_world", "cloister_world_quality03", "cloister_actors", "cloister_effects", "cloister_hud", "element_emblem"))
    names.update("chapter1/view/" + s + ".gdshader" for s in (
        "comet", "impact", "foot_shadow", "flame_bloom", "element_particle",
        "cloister_ground_quality03", "cloister_props_quality03", "cloister_contact_quality03"))
    for role in ("hero", "walker", "ranged", "charger", "elite"):
        names.update("chapter1/art/actors/" + role + suffix for suffix in (".png", "_actions.png", ".json"))
    for name in ("ground_flagstone", "ground_soil", "cloister_props", "cloister_foliage", "hero_cast"):
        names.add("chapter1/art/quality03/" + name + "_v01.png")
        if name in ("cloister_props", "cloister_foliage", "hero_cast"):
            names.add("chapter1/art/quality03/" + name + "_v01.json")
    for cue, count in {"fire":3,"cold":2,"lightning":1,"impact":3,"death":3,"explosion":1,"hurt":1,
                       "drop":1,"pickup":1,"equip":1,"step":2}.items():
        names.update("chapter1/art/quality03_audio/%s_%d.wav" % (cue, i) for i in range(count))
    names.add("chapter1/art/quality03_audio/ambience.wav")
    names.add("chapter1/art/quality03_audio/AUDIO-LEDGER.json")
    names.update("chapter1/art/quality03_audio/LICENSE-Kenney-%s.txt" % s for s in ("Impact", "RPG", "Sci-fi"))
    for name in names:
        assert (ROOT/name).is_file(), "Missing explicit dependency: " + name
    assert len([p for p in names if p.endswith(".wav")]) == 20
    assert len([p for p in names if p.startswith("chapter1/art/quality03/") and p.endswith(".png")]) == 5
    return sorted(names)


def preservation():
    baseline = read(ROOT/"evidence/phase7/builds/phase7-candidate-20261030-01/source-manifest.json")
    core = {r["path"]:r["sha256"] for r in read(ROOT/"chapter1/evidence/core-pilot-20261031-03/source-manifest.json")}
    backup = read(BACKUP)
    checks = {}
    for label, pins in (("baseline51", baseline), ("core9", core),
                        ("prior_exes", {p:r["sha256"] for p,r in backup["fixed_files"].items()}),
                        ("user_profiles", {p:r["sha256"] for p,r in backup["native_profiles"].items()})):
        mismatch = [p for p,digest in pins.items() if not (ROOT/p).is_file() or sha(ROOT/p) != digest]
        checks[label] = {"count":len(pins), "mismatches":mismatch}
    old_stage_pins = read(OLD_PROOF/"staging-manifest.json")
    checks["candidate02_stage44"] = {"count":len(old_stage_pins), "mismatches":[
        p for p,digest in old_stage_pins.items() if not (OLD_STAGE/p).is_file() or sha(OLD_STAGE/p) != digest]}
    assert all(not row["mismatches"] for row in checks.values()), checks
    return checks


def run(label, command, folder, timeout=300):
    assert not (folder/(label+"-execution.json")).exists()
    result = subprocess.run([str(p) for p in command], capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=timeout)
    record = {"command":[str(p) for p in command], "actual_exit":result.returncode,
              "stdout":result.stdout, "stderr":result.stderr}
    write(folder/(label+"-execution.json"), record)
    assert result.returncode == 0, label+" failed; inspect preserved execution record"
    assert not re.search(r"(?:SCRIPT ERROR|ERROR:|Parse Error)", result.stdout+result.stderr), label+" logged errors"
    return record


def prepare():
    paths = runtime_paths()
    # This is a provisional dependency inventory, not a source freeze while owners work.
    report = {"build_id":BUILD_ID, "stage":str(STAGE), "output":str(OUTPUT), "source_paths":paths,
              "source_count":len(paths), "preservation":preservation(), "scope":SCOPE,
              "provisional":True, "excluded":["attempts/", "hero_run*", "tests/", "evidence/", "tools/",
                 "protected reference assets", "old synthetic expedition audio", "old terrain PNG"],
              "ffmpeg":shutil.which("ffmpeg"), "ffprobe":shutil.which("ffprobe")}
    help_result = subprocess.run([str(ENGINE),"--help"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert help_result.returncode == 0
    report["movie_cli_help"] = [line.strip() for line in help_result.stdout.splitlines()
        if any(term in line for term in ("--write-movie", "--fixed-fps", "--disable-vsync", "--quit-after"))]
    write(HERE/"PREPARATION.json", report)
    print(json.dumps({"ready":True,"runtime_source_count":len(paths),"no_export_or_gpu_run":True}))


def freeze(destination):
    write(destination, {p:sha(ROOT/p) for p in runtime_paths()+["project.godot", "export_presets.cfg"]})
    print(json.dumps({"freeze":str(destination),"sha256":sha(destination)}))


def check_pins(base, pins):
    mismatch = [p for p,digest in pins.items() if not (base/p).is_file() or sha(base/p) != digest]
    assert not mismatch, {"base":str(base),"mismatches":mismatch}


def build(freeze_path):
    # Root must schedule this after source owners freeze. No implicit rebuild/overwrite.
    pins = read(freeze_path)
    paths = runtime_paths()
    assert set(pins) == set(paths+["project.godot", "export_presets.cfg"]), "Freeze closure differs"
    check_pins(ROOT, pins)
    before = preservation()
    for folder in (STAGE, OUTPUT, PROOF):
        fresh_dir(folder)
    write(PROOF/"source-manifest.json", {p:pins[p] for p in paths})
    write(PROOF/"freeze-input.json", {"path":str(Path(freeze_path).resolve()),"sha256":sha(freeze_path)})
    for p in paths:
        target = STAGE/p
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/p, target)
    project = (ROOT/"project.godot").read_text(encoding="utf-8")
    assert project.count('run/main_scene="res://Baseline.tscn"') == 1
    assert project.count('config/name="D2R Combat Baseline"') == 1
    project = project.replace('run/main_scene="res://Baseline.tscn"','run/main_scene="res://chapter1/Chapter1.tscn"')
    project = project.replace('config/name="D2R Combat Baseline"',
        'config/name="Ashen Cloister Chapter1 C2 Quality03"\nconfig/use_custom_user_dir=true\nconfig/custom_user_dir_name="AshenCloisterChapter1C2Quality03"')
    (STAGE/"project.godot").write_text(project, encoding="utf-8")
    resources = ["res://"+p for p in paths if Path(p).suffix in (".gd", ".gdshader", ".tscn", ".png", ".wav")]
    preset = (ROOT/"export_presets.cfg").read_text(encoding="utf-8")
    assert 'export_filter="all_resources"' in preset
    assert 'include_filter="assets/licenses/*.txt,game_data/*.json"' in preset
    preset = preset.replace('name="Windows Desktop"','name="Chapter1 Quality03 Windows"')
    preset = preset.replace('export_filter="all_resources"','export_filter="selected_resources"\nexport_files=PackedStringArray('+', '.join(json.dumps(p) for p in resources)+')')
    preset = preset.replace('include_filter="assets/licenses/*.txt,game_data/*.json"',
        'include_filter="chapter1/data/*.json,chapter1/art/actors/*.json,chapter1/art/quality03/*.json,chapter1/art/quality03_audio/*.json,chapter1/art/quality03_audio/LICENSE-*.txt"')
    (STAGE/"export_presets.cfg").write_text(preset, encoding="utf-8")
    staged = {p:sha(STAGE/p) for p in paths+["project.godot", "export_presets.cfg"]}
    write(PROOF/"staging-manifest.json", staged)
    write(PROOF/"closure.json", {"build_id":BUILD_ID,"runtime_source_files":paths,"source_count":len(paths),"stage_count":len(staged),"stage":str(STAGE),"output":str(OUTPUT),"scope":SCOPE})
    exe = OUTPUT/"AshenCloister-Chapter1.exe"
    run("import", [ENGINE,"--headless","--path",STAGE,"--editor","--import"], PROOF)
    run("export", [ENGINE,"--headless","--path",STAGE,"--export-release","Chapter1 Quality03 Windows",exe], PROOF)
    check_pins(ROOT, pins)
    check_pins(STAGE, staged)
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("preserved_phase7_pck_parser", ROOT/"tools/build_phase7.py")
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    package = parser.pck_entries(exe)
    packed = {r["path"].removeprefix("res://"):r for r in package["entries"]}
    for p in paths:
        ext = Path(p).suffix
        expected = p+".import" if ext in (".png", ".wav") else p+".remap" if ext in (".gd", ".tscn") else p
        assert expected in packed or (ext == ".gdshader" and p+".remap" in packed), "Dynamic dependency omitted: "+expected
        if ext in (".json", ".txt"):
            assert packed[p]["sha256"] == pins[p], "Packaged metadata/license differs: "+p
    forbidden = ("evidence/", "research/", "tests/", "tools/", "attempts/", "hero_run", "Baseline.tscn", "baseline_view", "assets/expedition/", "terrain/cloister_ground", "presentation/expedition_audio")
    bad = [p for p in packed if any(term.lower() in p.lower() for term in forbidden)]
    assert not bad, bad
    package.update({"exe_sha256":sha(exe),"forbidden_matches":bad,"success":True,"scope":"PCK payload checksums and explicit closure only; runtime and quality separate"})
    write(PROOF/"pck-audit.json", package)
    smoke = run("packaged-headless-smoke", [exe,"--headless","--","--chapter1-start","--chapter1-pilot","--chapter1-qa-ignore-focus","--chapter1-seed=90131","--chapter1-quit-after=2"], PROOF, timeout=60)
    audio = [json.loads(line.split("CHAPTER1_AUDIO ",1)[1]) for line in smoke["stdout"].splitlines() if "CHAPTER1_AUDIO " in line]
    ready = [json.loads(line.split("CHAPTER1_READY ",1)[1]) for line in smoke["stdout"].splitlines() if "CHAPTER1_READY " in line]
    assert len(audio) == 1 and audio[0]["raw_fallbacks"] == [], audio
    assert len(ready) == 1 and ready[0]["raw_texture_fallbacks"] == [], ready
    write(PROOF/"imported-resource-proof.json", {"audio":audio[0],"ready":ready[0],"scope":"Packaged headless resource load only; no GPU, sound-hearing, or visual quality approval"})
    credits = OUTPUT/"credits"
    credits.mkdir()
    for p in paths:
        if Path(p).name.startswith("LICENSE-") or Path(p).name == "AUDIO-LEDGER.json":
            shutil.copy2(ROOT/p, credits/Path(p).name)
    for p in ("chapter1/art/ASSET-LEDGER.json", "chapter1/art/quality03/ASSET-LEDGER-v04.json"):
        shutil.copy2(ROOT/p, credits/Path(p).name)
    shutil.copy2(HERE/"RUN.ko.md", OUTPUT/"RUN.ko.md")
    after = preservation()
    assert before == after
    write(PROOF/"preservation.json", {"before":before,"after":after,"success":True,"scope":"Selected baseline51/core9/exe2/userprofile2/oldstage44 pins; not all historical evidence"})
    write(PROOF/"build.json", {"exe":str(exe),"sha256":sha(exe),"bytes":exe.stat().st_size,"entry_count":len(packed),"source_count":len(paths),"stage":str(STAGE),"entrypoint":"res://chapter1/Chapter1.tscn","scope":SCOPE})
    print(json.dumps(read(PROOF/"build.json")))


def movie(variant, capture_id):
    assert re.fullmatch(r"[a-z0-9-]+", capture_id), "Use a plain unique capture ID"
    # AVI and converted MP4 are both preserved. Abort before writing when disk low.
    assert shutil.disk_usage("C:/").free > 18 * 1024**3, "Need >18GiB free; do not delete previous evidence automatically"
    proof = HERE/"movies"/capture_id
    fresh_dir(proof)
    if variant == "old":
        pinned = read(OLD_PROOF/"staging-manifest.json")
        check_pins(OLD_STAGE, pinned)
        stage = Path("C:/Project/game-research/build-staging")/("chapter1-quality03-old-movie-"+capture_id)
        fresh_dir(stage)
        for p in pinned:
            target = stage/p
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(OLD_STAGE/p, target)
        check_pins(stage, pinned)
        run("import", [ENGINE,"--headless","--path",stage,"--editor","--import"], proof)
    else:
        stage = STAGE
        pinned = read(PROOF/"staging-manifest.json")
        check_pins(stage, pinned)
    raw = proof/(variant+"-720p30-offline.avi")
    command = [ENGINE,"--path",stage,"--resolution","1280x720","--write-movie",raw,
        "--fixed-fps","30","--disable-vsync","--quit-after","3000","--",
        "--chapter1-start","--chapter1-pilot","--chapter1-qa-ignore-focus","--chapter1-seed=90131",
        "--chapter1-quit-after=90"]
    # Movie writer renders offline, not a native OS player or real-time FPS sample.
    run("movie", command, proof, timeout=1800)
    check_pins(stage, pinned)
    if variant == "old":
        check_pins(OLD_STAGE, pinned)
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    assert ffmpeg and ffprobe and raw.is_file()
    mp4 = proof/(variant+"-720p30-offline.mp4")
    run("encode", [ffmpeg,"-n","-i",raw,"-t","90","-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-movflags","+faststart",mp4], proof, timeout=900)
    probe = run("ffprobe", [ffprobe,"-v","error","-show_format","-show_streams","-of","json",mp4], proof)
    metadata = json.loads(probe["stdout"])
    video = [r for r in metadata["streams"] if r["codec_type"] == "video"]
    audio = [r for r in metadata["streams"] if r["codec_type"] == "audio"]
    assert len(video) == 1 and video[0]["width"] == 1280 and video[0]["height"] == 720
    assert len(audio) == 1 and abs(float(metadata["format"]["duration"])-90) < .5
    write(proof/"movie-manifest.json", {"variant":variant,"stage":str(stage),"seed":90131,"pilot":"unchanged normal-input/choice/equip driver; no HP/XP/item/kill injection",
        "offline_fixed_fps":30,"frame_guard":3000,"application_quit_seconds":90,"display_mp4_trim_seconds":90,"raw_avi":{"path":str(raw),"sha256":sha(raw),"bytes":raw.stat().st_size},"mp4":{"path":str(mp4),"sha256":sha(mp4),"bytes":mp4.stat().st_size},"probe":metadata,
        "source_sha256":pinned,"scope":"Offline fixed30FPS visual/audio comparison; not real-time performance, manual play, full chapter, or actual sound-hearing approval"})
    write(proof/"preservation.json", preservation())
    print(json.dumps({"movie":str(mp4),"proof":str(proof),"offline_not_performance":True}))


def main():
    parser = argparse.ArgumentParser(__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("prepare")
    p = sub.add_parser("freeze")
    p.add_argument("destination", type=Path)
    p = sub.add_parser("build")
    p.add_argument("--source-freeze", type=Path, required=True)
    p = sub.add_parser("movie")
    p.add_argument("--variant", choices=("old", "new"), required=True)
    p.add_argument("--capture-id", required=True)
    args = parser.parse_args()
    if args.action == "prepare":
        prepare()
    elif args.action == "freeze":
        freeze(args.destination)
    elif args.action == "build":
        build(args.source_freeze)
    elif args.action == "movie":
        movie(args.variant, args.capture_id)


if __name__ == "__main__":
    main()
