The initial pure-test invocation exposed a strict GDScript warning treated as a
parse error in frame_probe.gd:62 (conditional Texture2D.get_size inferred Variant).
The script never sampled runtime performance. A dependent-script compile failure
left the SceneTree fixture alive; it was stopped with Ctrl+C (exit1). The source
now explicitly converts the render texture size to Vector2i. Subsequent runs are
recorded separately; this failure is retained rather than labeled a passing run.
