"""Compare locally rendered own-game movies. No remote media or product edits."""
from pathlib import Path
import importlib.util
import json
import shutil
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("quality03_package", HERE/"package_quality03.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
assert len(sys.argv) == 4, "Usage: compare_movies.py OLD_CAPTURE_ID NEW_CAPTURE_ID UNIQUE_COMPARISON_ID"
old_id, new_id, comparison_id = sys.argv[1:]
assert all(p.re.fullmatch(r"[a-z0-9-]+", x) for x in sys.argv[1:])
proof = HERE/"movies"/comparison_id
p.fresh_dir(proof)
old = p.read(HERE/"movies"/old_id/"movie-manifest.json")
new = p.read(HERE/"movies"/new_id/"movie-manifest.json")
assert old["variant"] == "old" and new["variant"] == "new"
assert old["seed"] == new["seed"] == 90131
assert old["offline_fixed_fps"] == new["offline_fixed_fps"] == 30
for manifest in (old,new):
    assert p.sha(manifest["mp4"]["path"]) == manifest["mp4"]["sha256"]
exe = p.read(p.PROOF/"build.json")
assert p.sha(exe["exe"]) == exe["sha256"]
ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
assert ffmpeg and ffprobe and Path("C:/Windows/Fonts/arial.ttf").is_file()
font = "fontfile='C\\:/Windows/Fonts/arial.ttf'"
# Top padding preserves all game HUD pixels. One audio stream is explicitly labelled.
left = "[0:v]pad=iw:ih+48:0:48:black,drawtext="+font+":text='OLDER CANDIDATE 02 - OFFLINE 30FPS':x=18:y=13:fontsize=20:fontcolor=white[l]"
right = "[1:v]pad=iw:ih+48:0:48:black,drawtext="+font+":text='QUALITY CANDIDATE 03 - OFFLINE 30FPS - AUDIO 03':x=18:y=13:fontsize=20:fontcolor=white[r]"
out = proof/"candidate02-vs03-20s-60s-offline.mp4"
p.run("compare", [ffmpeg,"-n","-ss","20","-t","40","-i",old["mp4"]["path"],
    "-ss","20","-t","40","-i",new["mp4"]["path"],"-filter_complex",left+";"+right+";[l][r]hstack=inputs=2[v]",
    "-map","[v]","-map","1:a:0","-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
    "-c:a","aac","-b:a","192k","-movflags","+faststart",out],proof,timeout=600)
probe = p.run("ffprobe",[ffprobe,"-v","error","-show_format","-show_streams","-of","json",out],proof)
metadata = json.loads(probe["stdout"])
assert abs(float(metadata["format"]["duration"])-40) < .5
for manifest in (old,new):
    variant = manifest["variant"]
    for second in (20,40,60,75):
        dest = proof/(variant+"-frame-%03d.png" % second)
        p.run(variant+"-frame-%03d" % second,[ffmpeg,"-n","-ss",str(second),"-i",manifest["mp4"]["path"],
            "-frames:v","1",dest],proof,timeout=60)
        assert dest.is_file()
    p.check_pins(Path(manifest["stage"]),manifest["source_sha256"])
assert p.sha(exe["exe"]) == exe["sha256"]
p.write(proof/"comparison-manifest.json", {"old_manifest":str(HERE/"movies"/old_id/"movie-manifest.json"),
    "new_manifest":str(HERE/"movies"/new_id/"movie-manifest.json"),"old_new_same_seed":90131,
    "excerpt_source_seconds":[20,60],"duration_seconds":40,"audio_source":"candidate03 only, labelled in top padding",
    "comparison":{"path":str(out),"sha256":p.sha(out),"bytes":out.stat().st_size},"probe":metadata,
    "frame_extracts":{path.name:p.sha(path) for path in proof.glob("*.png")},
    "new_exe_sha256":p.sha(exe["exe"]),"preservation":p.preservation(),
    "scope":"Own-game offline fixed30FPS same-input visual comparison; no real-time FPS, manual-play, audio hearing, or quality approval"})
print(json.dumps({"comparison":str(out),"frames":8,"offline_not_performance":True}))
