# Successor37 independent static review · 2026-11-06

Scope: read-only source/proof review; no engine, GPU, build, capture, copy or deletion. One small review document added. Product36 source freeze and current nine user pins match; catalogs differ only arc evolution_name after explicit normalization.

## Required fix before successor activation

[P2] run_growth_quality37.gd:18-30 accesses nested candidate values before validating their shape. Its public configure(candidate: Variant, ...) previously inherited Growth.configure's Catalog.validate-first contract. A dictionary such as {skills:[17],xp_thresholds:[]} reaches skill.get on an integer; a dictionary carrying the approved arc record with xp_thresholds:17 reaches duplicate on an integer. These should return false with errors, not trigger a GDScript runtime error. Production start currently supplies validated predecessor data, so normal39+retry21 proofs do not expose this gap. Run GrowthCatalog.validate(candidate) first (and preserve its errors/old state on failure) before traversing or copying nested fields. Add a small negative proof for malformed skills and XP types when disk work resumes. No product fix made in this review.

## Confirmed design and proof coverage

- ChapterRun37 replaces the otherwise unused initial Growth object, with no added post-start configure or epoch manipulation. Existing base and chapter start are still the two authoritative configure calls.
- New Growth deep copies incoming data, updates only the exact arc name, preserves incoming FULL_XP, and rejects any other successor dictionary difference. Old cached _catalog is consulted only for the two inherited start configurations, not later UI effects, so its historical name does not leak into effective_skill/offer authority.
- Text proof directly validates both catalogs and exact one-field difference, branch3, start epochs2/restart4, all3 primary normal1200frame snapshots and all3 spawn/loot/growth RNG states. Protected evolution fixture verifies tokens/card IDs/choices and effective evolved arc name/effects. XP grants are explicitly fixture-only, not normal gameplay evidence.
- Retry proof dirties state then same-object starts seed90132; checks epoch4/FULL_XP/cache/whole snapshot/three RNG states. Existing output exit0 and empty stderr support the39+21 valid-input cases; there are no malformed-candidate negative cases.
- Loop short-circuit can leave rng_same true after an earlier snapshot mismatch, but frames_same then fails and final exit1 still prevents false success.

## Masonry37c static review

- World37c directly inherits31d and scopes ShaderMaterial replacement to RearMasonry22 and RearArches22. Nonrear labels follow base behavior;37/37b global material tint side effects are avoided.
- Geometry37b is ultimately RefCounted (cloister_world_quality03), created without setup/root assignment; only geometry methods are called. No orphan Node or owner back-reference is introduced by this helper.
- Shader uses world-space coordinates and normal-derived triplanar weights, existing flagstone/soil texture sources and instance COLOR. No simulation/profile access. No definite material/lifecycle correctness defect found by static review.
- Actual37c GPU was interrupted and has no terminal RESULT/capture review. Headless import/check alone does not prove real driver shader compilation, visual benefit, shadow consistency or performance. Do not adopt37c yet.

## Safe activation sequence after disk space is available

1. Fix nested-input validation in new37 Growth and independently verify targeted negative/positive cases; leave36 frozen.
2. Fresh continuation of interrupted37c study using preserved source, new unique output directory; inspect actual same-camera captures, rear-only material/proxy invariants and fullCore/anchors equality. Avoid rerunning completed31d/37b baseline without a new concern.
3. Exclusive resource cost study only if visual improvement warrants candidate adoption; previous03 costs overlapped possible headless work and are exploratory.
4. New candidate source/EXE assembly/package must include successor JSON/Growth and chosen World dependencies; verify whole frozen dependency graph and current ADDENDUM02 pins. New effective arc name must be observed in real HUD.
5. Final same-EXE focused1080p formal3 runs and full manual/audio gates remain separate; no completion claim from static/proof review.