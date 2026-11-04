"""Read-only scoped preservation check after legacy-report output incident.

Original GPU raw per-file hashes were not universally pinned. Presence and
modification times do not prove their original byte identity.
"""
import hashlib
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/phase4/verification/preservation-scope-audit.json"
SNAPSHOT = Path(r"C:\Project\game-research\implementation-backups\phase3-final-source-20261027")


def sha(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


manifest = json.loads((ROOT / "evidence/phase3/source-manifest.json").read_text(encoding="utf-8-sig"))
source_rows = []
for item in manifest:
    path = SNAPSHOT / item["path"]
    actual = sha(path) if path.is_file() else None
    source_rows.append({"path": str(path), "expected_sha256": item["sha256"].lower(),
                        "actual_sha256": actual, "matches_pin": actual == item["sha256"].lower()})
build = json.loads((ROOT / "evidence/phase3/final-build.json").read_text(encoding="utf-8-sig"))
exe = Path(build["path"])
exe_hash = sha(exe)
index = json.loads((ROOT / "evidence/phase3/EVIDENCE-INDEX.json").read_text(encoding="utf-8-sig"))
raw_rows = []
for record in index["records"]:
    for key in ("summary", "launch", "frames", "physics", "capture", "process_memory"):
        if key not in record:
            continue
        path = Path(record[key])
        exists = path.is_file()
        raw_rows.append({"record": record["name"], "kind": key, "path": str(path),
                         "exists": exists, "length": path.stat().st_size if exists else None,
                         "last_write_local": datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat() if exists else None})
report = {"scope": "Pinned phase3 source snapshot and EXE byte verification; main indexed raw file presence/time only",
          "source_snapshot": source_rows, "source_all_match": all(row["matches_pin"] for row in source_rows),
          "exe": {"path": str(exe), "expected_sha256": build["exe_sha256"].lower(),
                  "actual_sha256": exe_hash, "matches_pin": exe_hash == build["exe_sha256"].lower()},
          "indexed_record_count": len(index["records"]), "indexed_raw_files": raw_rows,
          "indexed_raw_all_present": all(row["exists"] for row in raw_rows),
          "limitation": "Indexed raw per-file original hashes were not universally pinned; existence/mtime cannot establish all original bytes unchanged. Two legacy-scene auxiliary JSON reports were rewritten and are explicitly excluded from original-byte preservation claims."}
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({key: report[key] for key in ("source_all_match", "exe", "indexed_record_count", "indexed_raw_all_present", "limitation")}))
