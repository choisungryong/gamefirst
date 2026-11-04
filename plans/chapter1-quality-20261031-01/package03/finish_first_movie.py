"""Encode preserved first AVI; explicitly retain and disclose forced-exit warnings."""
from pathlib import Path
import importlib.util
import json
import re
import shutil
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("quality03_package", HERE/"package_quality03.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
proof = HERE/"movies/new-20261101-01"
execution = p.read(proof/"movie-execution.json")
assert execution["actual_exit"] == 0
assert "2700 frames at 30 FPS" in execution["stdout"]
assert "ERROR: 9 resources still in use at exit" in execution["stderr"]
assert "SCRIPT ERROR" not in execution["stderr"] and "Parse Error" not in execution["stderr"]
lines = [line for line in execution["stderr"].splitlines() if line.strip()]
assert len(lines) == 4 and lines[0].startswith("WARNING: ObjectDB instances leaked at exit")
assert lines[1].strip() == "at: cleanup (core/object/object.cpp:2514)"
assert lines[2].startswith("ERROR: 9 resources still in use at exit")
assert lines[3].strip() == "at: clear (core/io/resource.cpp:795)"
results = [json.loads(line.split("CHAPTER1_RUNTIME_RESULT ",1)[1]) for line in execution["stdout"].splitlines()
           if "CHAPTER1_RUNTIME_RESULT " in line]
assert len(results) == 1 and results[0]["mode"] == "victory" and results[0]["elapsed"] == 78.15
assert results[0]["kills"] == 813 and results[0]["pilot"] is True
raw = proof/"new-720p30-offline.avi"
assert raw.stat().st_size > 1024*1024
stage_pins = p.read(p.PROOF/"staging-manifest.json")
p.check_pins(p.STAGE,stage_pins)
exe = p.read(p.PROOF/"build.json")
assert p.sha(exe["exe"]) == exe["sha256"]
ffmpeg,ffprobe = shutil.which("ffmpeg"),shutil.which("ffprobe")
mp4 = proof/"new-720p30-offline.mp4"
p.run("encode",[ffmpeg,"-n","-i",raw,"-t","90","-c:v","libx264","-preset","medium","-crf","19",
    "-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-movflags","+faststart",mp4],proof,timeout=900)
probe = p.run("ffprobe",[ffprobe,"-v","error","-show_format","-show_streams","-of","json",mp4],proof)
metadata = json.loads(probe["stdout"])
video = [s for s in metadata["streams"] if s["codec_type"] == "video"]
audio = [s for s in metadata["streams"] if s["codec_type"] == "audio"]
assert len(video) == len(audio) == 1 and video[0]["width"] == 1280 and video[0]["height"] == 720
assert abs(float(metadata["format"]["duration"])-90) < .5
p.write(proof/"movie-manifest.json",{"variant":"new","stage":str(p.STAGE),"seed":90131,
    "pilot":"unchanged normal-input/choice/equip driver; no HP/XP/item/kill injection","offline_fixed_fps":30,
    "frames_requested":2700,"raw_avi":{"path":str(raw),"sha256":p.sha(raw),"bytes":raw.stat().st_size},
    "mp4":{"path":str(mp4),"sha256":p.sha(mp4),"bytes":mp4.stat().st_size},"probe":metadata,
    "source_sha256":stage_pins,"runtime_results":results,"new_exe_sha256":p.sha(exe["exe"]),
    "forced_exit_warning_preserved":execution["stderr"],"tool_first_result":"Strict error guard rejected forced-exit cleanup warning; valid AVI subsequently encoded append-only under root instruction",
    "scope":"Offline fixed30FPS visual/audio comparison; not real-time performance, manual play, full chapter, sound-hearing, quality approval, or leak0 claim"})
p.write(proof/"preservation.json",p.preservation())
print(json.dumps({"movie":str(mp4),"forced_exit_warning_preserved":True,"runtime_mode":"victory","runtime_elapsed":78.15}))
