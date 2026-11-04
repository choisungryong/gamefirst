"""Collect existing benchmark summaries; this is not the independent raw auditor."""
import json
from pathlib import Path
from datetime import datetime, timezone

PROJECT = Path(__file__).resolve().parents[1]
EVIDENCE = PROJECT / "evidence" / "phase3"
GROUPS = {
    "matrix": "release-matrix-resume-20261028",
    "projectile_stress": "release-stress-20261028",
    "soak": "release-soak-20261028",
    "diagnostic": "release-decomposition-20261028",
}
EXPECTED = {"matrix": 18, "projectile_stress": 3, "soak": 1, "diagnostic": 3}


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def number(value):
    return f"{value:.3f}"


def main():
    if (EVIDENCE / "EVIDENCE-INDEX.json").exists() or (EVIDENCE / "MEASUREMENTS.ko.md").exists():
        raise FileExistsError("Preserve existing collected reports and later diagnostic addenda; choose a separate output before regenerating")
    build = load(EVIDENCE / "final-build.json")
    records = []
    summaries = {}
    for group, directory in GROUPS.items():
        listed = load(EVIDENCE / directory / "schedule-results.json")
        listed = listed if isinstance(listed, list) else [listed]
        if len(listed) != EXPECTED[group]:
            raise ValueError(f"Incomplete {group}: {len(listed)}")
        for record in listed:
            source = Path(record["directory"])
            summary = load(source / "summary.json")
            launch = load(source / "launch.json")
            if launch["exe_sha256"].lower() != build["exe_sha256"].lower():
                raise ValueError(f"Wrong EXE: {source}")
            if summary["embedded_source_manifest_sha256"].lower() != build["embedded_source_manifest_sha256"].lower():
                raise ValueError(f"Wrong source metadata: {source}")
            if not summary["valid_run"] or record["exit"] != 0:
                raise ValueError(f"Invalid collected execution: {source}")
            summaries[record["name"]] = summary
            records.append({
                "group": group,
                "name": record["name"],
                "directory": str(source),
                "summary": str(source / "summary.json"),
                "launch": str(source / "launch.json"),
                "frames": str(source / "frames.csv"),
                "physics": str(source / "physics.csv"),
                "capture": str(source / "frame.png"),
                "process_memory": str(source / "process-memory.csv"),
                "renderer": summary["rendering_method"],
                "workload": summary["workload"],
                "mode": summary["mode"],
                "requested": summary["requested"],
                "sample_seconds": summary["measured_sample_seconds"],
                "capture_elapsed_seconds": summary["capture_elapsed"],
                "frame_ms": summary["frame_ms"],
                "stutter_gt50": summary["stutter_gt50"],
                "valid": summary["valid_run"],
                "target_eligible": summary["target_eligible"],
                "target_pass": summary["target_pass"],
                "exe_sha256": launch["exe_sha256"],
                "configuration_digest": summary["configuration_digest"],
            })
    index = {
        "schema_version": 1,
        "collected_utc": datetime.now(timezone.utc).isoformat(),
        "basis": "Collected existing summaries/launches; independent raw validation is recorded separately.",
        "build": build,
        "excluded_partial_run": str(EVIDENCE / "release-matrix" / "forward_plus-skill-n300-r1"),
        "records": records,
    }
    (EVIDENCE / "EVIDENCE-INDEX.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    text = [
        "# 3단계 최종 실행본 측정 수집 결과",
        "",
        "2026-10-28 · 아래는 동일 최종 EXE의 수집된 summary를 정리한 표다. 독립 원시 CSV/PNG 감사·별도 GPU 재현·일반 실행본 QA 및 root 최종 승인과 구분한다.",
        "",
        "실제1920×1080, VSync끔/max_fps0, 워밍업10초 후 각60초×3. 현재 catalog의 실제 지속시전·발사·명중·피격 표현을 사용하며 HP1e9/마나매tick보정의 합성 고정 수 부하다. 일반 플레이 밸런스나 SACRATA 최종 품질 평가가 아니다.",
        "",
        "## 주 matrix 18회",
        "",
        "| renderer | 적 수 | p95 r1/r2/r3(ms) | p99 최대(ms) | 최악 프레임(ms) | >50ms 합계 | p95≤16.67 |",
        "|---|---:|---|---:|---:|---:|---|",
    ]
    for renderer in ("forward_plus", "gl_compatibility"):
        for count in (100, 300, 500):
            selected = [r for r in records if r["group"] == "matrix" and r["renderer"] == renderer and r["requested"] == count]
            p95s = " / ".join(number(r["frame_ms"]["p95"]) for r in selected)
            text.append(f"| {renderer} | {count} | {p95s} | {max(r['frame_ms']['p99'] for r in selected):.3f} | {max(r['frame_ms']['max'] for r in selected):.3f} | {sum(r['stutter_gt50'] for r in selected)} | {'3회 통과' if all(r['target_pass'] for r in selected) else '미달'} |")
    text += [
        "",
        "300적 주 기준은 두 renderer에서3회 모두 통과했다. 500적은 두 renderer에서3회 모두 미달한 스트레스 한계다. p95 기준 통과를 모든 프레임의16.67ms 보장이나 완전 고정60FPS로 확대하지 않는다.",
        "",
        "100적의 관측 비행탄은 최대1,300/500적은 밀집 즉시 명중으로 관측0이다. 실제 cast/release/hit/FX는 처리됐다. 이 matrix를4탄 동시화면가시 성능으로 부르지 않는다. 카메라 안 중심/보유fullrig 수와 occlusion 가시 픽셀 수/GPU skinning 작업 수도 구분한다.",
        "",
        "## 별도 300탄 요청 극한 스트레스",
        "",
        "| 회차 | p50/p95/p99/worst(ms) | 실제 활성탄 min/max | 입자 max | >50ms |",
        "|---|---|---|---:|---:|",
    ]
    for record in (r for r in records if r["group"] == "projectile_stress"):
        summary = summaries[record["name"]]
        values = " / ".join(number(record["frame_ms"][key]) for key in ("p50", "p95", "p99", "max"))
        text.append(f"| {record['name']} | {values} | {summary['bolts']['min']}/{summary['bolts']['max']} | {summary['fx_particles']['max']} | {record['stutter_gt50']} |")
    text += ["", "세 회차 모두 p95목표 미달이다. 요청300과 충돌 후 실제 활성탄 수는 다르며 현재 스킬 주 관문과 분리한다.", "", "## 10분 합성 지속 부하", ""]
    soak = next(r for r in records if r["group"] == "soak")
    summary = summaries[soak["name"]]
    text += [
        f"실제 샘플 {soak['sample_seconds']:.6f}초,300생존/300보유rig 유지. p50/p95/p99/worst는 {' / '.join(number(soak['frame_ms'][key]) for key in ('p50','p95','p99','max'))}ms, >50ms {soak['stutter_gt50']}회다.",
        "",
        f"nodes는 {summary['nodes']['min']:.0f}..{summary['nodes']['max']:.0f}, history최대{summary['history']['max']}, actors_created {summary['pool_counters']['actors_created']}, particles_created {summary['pool_counters']['particles_created']}/reused {summary['pool_counters']['particles_reused']}다. 이 경로는 투사체가 즉시 명중하므로 sprite pool 재사용을 장시간 검증한 조건은 아니다.",
        "",
        "process private 메모리는 초기2초565,493,760bytes에서 최종report시점1,180,581,888bytes로 증가했다. game node/pool/history 상한의 안정과 process 전체 메모리 증가는 별도 사실이다. 측정 raw 숫자셀은59,163×28+36,000×9=1,980,564개이며8byte값payload만 가정하면 약15.11MiB다. 실제Variant/배열·통계벡터·정렬·컨테이너/엔진/드라이버 비용은 이 하한에 포함하지 않는다. CSV파일 합계도 약10.35MiB이므로 private증가 전체를 계측버퍼로 수치상 설명한 것은 아니다. 미분리 잔차가 남아 있으며 메모리 누수0을 확정하지 않는다.",
        "",
        f"soak PNG는 warmup중 {soak['capture_elapsed_seconds']:.3f}초 캡처이며10분 종료 상태 사진이 아니다. 장시간 진행 근거는 전 구간 raw/tick/animation/pool 기록이다.",
        "",
        "## 짧은 최종 비용 분해",
        "",
        "| 모드 | 표본초 | p95(ms) | 보유rig min | 성능관문 |",
        "|---|---:|---:|---:|---|",
    ]
    for record in (r for r in records if r["group"] == "diagnostic"):
        summary = summaries[record["name"]]
        text.append(f"| {record['mode']} | {record['sample_seconds']:.6f} | {record['frame_ms']['p95']:.3f} | {summary['skinned_rigs']['min']} | 8초 진단;60초×3 아님 |")
    text += [
        "",
        "sim은 논리만 처리하고static은 시작 전 공유pose를 한 번 bake한 정적mesh,rig는 수동애니메이션을 실제 진행하는fullrig다. 각 비용의 비선형성과 겹침이 있으므로 차이를 단순 합산해 CPU/GPU 원인으로 단정하지 않는다.",
        "",
        "## 재현·보존·증거 위치",
        "",
        f"최종EXE SHA256 `{build['exe_sha256']}`. source/embeddedhash는 final-build.json,25개수집run과 raw/PNG/launch 경로는 EVIDENCE-INDEX.json에 있다. 기존100×3은원래폴더를 참조하며 summary없는partial300은 보존·완료건수 제외했다. 유한감독completion/stage-results는resume-20261028-control/에 저장됐다.",
        "",
        "장치: RTX2070SUPER8192MiB,driver610.88,Ryzen7 3700X,Windows11Pro26300,AMD Ryzen Balanced. 설정변경없이 재개 원문을 제어폴더에 저장했다. 본문 수치는 수집 요약이며 독립 감사의 원시 재계산 결과를 최종 승인 근거로 우선한다.",
        "",
        "새 REA/CASC/클래식/원작 관찰 결과는 없다. 이 단계는 독립 게임 구현·측정이다. 원작/과거 증거/백업/phase1·2실행본은 보존했고 SACRATA 최종 품질·D2R 전체 복원 완료로 주장하지 않는다.",
    ]
    (EVIDENCE / "MEASUREMENTS.ko.md").write_text("\n".join(text) + "\n", encoding="utf-8")
    print(json.dumps({"collected_runs": len(records), "valid_runs": sum(r["valid"] for r in records), "matrix_runs": 18, "scope": "summary collection, independent raw audit separate"}))


if __name__ == "__main__":
    main()
