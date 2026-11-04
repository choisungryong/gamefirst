# Raw frame interval probe contract

Status: implemented and CPU/headless contract-tested only. No formal real-time GPU
run was executed by this owner. Candidate04 export and three-run gate remain pending.

The first instruction in Chapter1._process invokes the optional observer. It takes
Time.get_ticks_usec, then records the interval since the previous callback start.
This is a raw monotonic wall interval including pacing and CPU/render-loop work.
It is not a hardware GPU timer, engine delta, frame render duration, or a promise
of fixed60FPS. Probe overhead is included in subsequent intervals.

The observer waits for the FIRST playing callback. Menu waiting consumes no warmup.
Root must focus the menu and click Start before the ten-second warmup begins.
The first interval is zero and discarded. Phase0 is warmup; phase3 crosses the
ten-second boundary and is retained raw but excluded from the measured distribution.
Phase1 comprises whole intervals starting at/after ten seconds, including the last
whole interval that crosses seventy seconds. It is never clipped or omitted to
hide a long final interval. Therefore measured coverage can differ slightly from
exact60s; its actual sum and first/last timestamps are reported. Coverage below59s
is invalid. Quantiles use nearest rank ceil(N*p)-1 without trimming.

Each raw row records sequence, monotonic elapsed/interval microseconds, phase,
window focus, run mode, simulation tick, retained enemy/projectile/orb/ground-item
counts, window and actual viewport-texture size, process/physics/drawn-frame IDs.
Retained enemy count includes retained corpses and is not claimed to be alive count.
Final game state includes controller metrics/growth/equipment. No state is injected.

Storage is preallocated to180000 rows (25.9MB of int64 payload). Exhaustion ends the
probe as explicitly invalid sample_capacity_exceeded; old rows are retained and
never overwritten or silently substituted. Raw CSV and summary are written once
AFTER completion, rejection, overflow, or early scene exit. The sample window does
not perform observer file I/O. Initial metadata is written before arming.

Formal eligibility requires actual1920x1080 window AND render texture, Forward+,
VSync disabled, uncapped Engine.max_fps0, time_scale1, explicit --delta-smoothing
disable, normal pilot enabled, focus handling enabled, and no armed frame in a
mode other than playing/choice. All warmup+sample rows count for focus/size/mode
eligibility. Headless, fixed FPS, movie, disabled rendering, PNG capture, input
logging, and wall-age QA quit are rejected. A permitted new output directory is
created with metadata/raw/invalid summary for configuration rejection. Existing
directories/files or disallowed paths are never overwritten. Only NEW subdirectories
under this quality04 evidence root or EXE/qa-probe are accepted.

--chapter1-frame-probe-quit is optional and has no default effect. With exactly one
nonempty probe output flag it waits for probe.done (after flush), then uses existing
audio.reset +150ms audio-server release and quits. Menu delay cannot consume its
seventy-second window. Do not use --chapter1-start in formal runs.

CPU verification: contract-test-02 has actual0/stderr-empty injected-clock21 checks,
scene --check-only actual0, and Python syntax checks. Injected examples are boundary
fixtures, not performance samples. INCIDENT-01 preserves the initial recovered
Variant inference parse failure. Test source pins are in result.json; source owners
may still change other files before the final package freeze.

The runner independently recomputes CSV intervals, phases, quantiles, hashes,
eligibility, exit/log status. Each attempt uses a new ID; invalid attempts remain.
Exactly three unique eligible runs of the same EXE are required for the aggregate
16.67ms p95 gate. This is representative normal-pilot load; no180-enemy maximum-load
or manual-play/sound-hearing/quality approval follows from it. Previous quality03
diagnostic01 (truncated15000) and diagnostic02 (120FPS paced) are not reused.

Authoritative Godot4.5 APIs reviewed2026-11-01:

- [Monotonic Time.get_ticks_usec](https://docs.godotengine.org/en/4.5/classes/class_time.html#class-time-method-get-ticks-usec)
- [Window.has_focus](https://docs.godotengine.org/en/4.5/classes/class_window.html#class-window-method-has-focus)
- [Engine.get_write_movie_path and frame IDs](https://docs.godotengine.org/en/4.5/classes/class_engine.html)
- [RenderingServer rendering method/driver/adapter](https://docs.godotengine.org/en/4.5/classes/class_renderingserver.html)
- [Texture2D.get_size returns Vector2](https://docs.godotengine.org/en/4.5/classes/class_texture2d.html#class-texture2d-method-get-size) (explicit Vector2i conversion in probe)
- [Command-line options](https://docs.godotengine.org/en/4.5/tutorials/editor/command_line_tutorial.html) and local4.5.1 --help confirm fixed-fps disables real-time synchronization and movie forces fixed FPS.
