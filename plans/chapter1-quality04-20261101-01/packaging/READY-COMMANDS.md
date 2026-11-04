# Candidate04 commands awaiting root source freeze / GPU allocation

All paths below are relative to C:/Project/d2r-combat-baseline. Python executable:
C:/Users/twins/AppData/Local/Programs/Python/Python310/python.exe.
No commit/push/upload. Existing candidate03/02/phase7, old stage/evidence, and user
profiles remain pinned. PREPARATION.json records successful selected preservation.

After ALL source owners finish, root makes the final source freeze (new file only):

```powershell
& 'C:/Users/twins/AppData/Local/Programs/Python/Python310/python.exe' plans/chapter1-quality04-20261101-01/packaging/package_quality04.py freeze --output plans/chapter1-quality04-20261101-01/packaging/FINAL-SOURCE-FREEZE.json
& 'C:/Users/twins/AppData/Local/Programs/Python/Python310/python.exe' plans/chapter1-quality04-20261101-01/packaging/package_quality04.py build --freeze plans/chapter1-quality04-20261101-01/packaging/FINAL-SOURCE-FREEZE.json
```

The freeze captures explicit prior70 runtime closure + frame_probe.gd +
hero_occlusion_rim.gdshader (72), plus source project/preset pins. Build copies
only that closure into a unique OUTSIDE-project stage:
C:/Project/game-research/build-staging/chapter1-c2-candidate-20261101-04.
Only staged project/preset differ; stage74 pins are audited after headless import,
release export, PCK closure/checksum audit and packaged headless fallback smoke.
The output is builds/chapter1/chapter1-c2-candidate-20261101-04. No screenshot/movie
action exists in this workflow. No staging or export has yet been performed.

After sole GPU allocation by root, start ONE formal run (menu awaits root CUA):

```powershell
& 'C:/Users/twins/AppData/Local/Programs/Python/Python310/python.exe' plans/chapter1-quality04-20261101-01/measurement/run_probe.py run --run-id formal01
```

The runner returns PID immediately to stdout while waiting for the game process;
the tool may yield a session. Root focuses the native menu and clicks its first
fire-start button. Do not activate another application, resize, capture PNG or use
movie during10s warmup +60s sample. Probe flushes and cleanly quits after completion;
runner records actual exit and independently audits raw CSV. Timeout300s is an
explicit failed attempt and never fabricated into a complete run. Check execution,
stderr, independent-audit and probe.summary before continuing. Each new attempt
must get a new ID (including after failures).

Repeat sequentially with formal02 and formal03, reserving sole GPU each time.
Only after all three are complete:

```powershell
& 'C:/Users/twins/AppData/Local/Programs/Python/Python310/python.exe' plans/chapter1-quality04-20261101-01/measurement/run_probe.py aggregate --runs formal01 formal02 formal03 --output THREE-RUN-GATE-01.json
```

Output verdicts report eligibility separately from p95 threshold. Even all-three
passing is a representative real-time interval gate, not fixed60FPS,180-enemy
stress, SACRATA quality, or1장 full-completion approval.
