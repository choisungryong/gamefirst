"""Independent ledger/hash/WAV checks; packaging and subjective audio quality separate."""
from pathlib import Path
import hashlib
import json
import re
import sys
import wave

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "evidence/phase7/presentation-resume-20261030-02/ASSET-LEDGER.json"
checks = 0
failures = []
def check(ok, label):
    global checks
    checks += 1
    if not ok: failures.append(label)
def main():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    records = ledger["records"]
    paths = [row["path"] for row in records]
    check(len(set(paths)) == len(paths), "ledger contains no duplicate identities")
    for row in records:
        path = ROOT / row["path"]
        check(path.is_file(), "ledger file exists: " + row["path"])
        if not path.is_file(): continue
        check(hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"], "ledger current hash: " + row["path"])
        if str(row.get("license") or "").startswith("assets/"):
            check((ROOT/row["license"]).is_file(), "license text exists: " + row["license"])
    wavs = sorted((ROOT/"assets/expedition/audio").glob("*.wav"))
    check(len(wavs) == 10, "nine cues plus one ambient WAV")
    for path in wavs:
        check(path.relative_to(ROOT).as_posix() in paths, "WAV has provenance record: " + path.name)
        with wave.open(str(path), "rb") as stream:
            check(stream.getcomptype() == "NONE" and stream.getnchannels() in (1,2) and stream.getsampwidth() == 2 and 8000 <= stream.getframerate() <= 96000 and stream.getnframes() > 0, "finite supported PCM stream: " + path.name)
    # Follow every literal GDScript dependency from the public expedition entry.
    pending = [ROOT/"expedition_view.gd"]
    seen = set()
    resource_literals = set()
    while pending:
        path = pending.pop()
        if path in seen: continue
        seen.add(path)
        for value in re.findall(r'"(res://[^"\n]+)"', path.read_text(encoding="utf-8")):
            resource_literals.add(value)
            if value.endswith(".gd") and (ROOT/value[6:]).is_file(): pending.append(ROOT/value[6:])
    check(not any("classic" in p.lower() or "diablo" in p.lower() or "atlas" in p.lower() for p in resource_literals), "reachable expedition script resource literals exclude research atlas")
    if "--prove-failure" in sys.argv: check(False, "intentional phase7 asset auditor failure proof")
    result = {"scope":"Ledger byte identity, licenses present, WAV format and literal expedition dependency inspection; no export-package exclusion or art/audio quality claim", "ledger":str(LEDGER),"checks":checks,"failures":failures,"wav_count":len(wavs),"reachable_scripts":len(seen),"success":not failures}
    print(json.dumps(result,ensure_ascii=False))
    raise SystemExit(0 if not failures else 1)
if __name__ == "__main__": main()
