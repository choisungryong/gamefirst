shader_type spatial;
render_mode unshaded, fog_disabled, depth_draw_never, depth_test_disabled, cull_back;
// Godot4.5 reversed Z: greater depth is nearer. Only hidden fragments tint.
// https://docs.godotengine.org/en/4.5/tutorials/shaders/advanced_postprocessing.html
uniform sampler2D scene_depth : hint_depth_texture, repeat_disable, filter_nearest;
uniform vec4 tint : source_color = vec4(0.95,0.72,0.30,0.34);
void fragment() {
 float opaque_depth=textureLod(scene_depth,SCREEN_UV,0.0).r;
 if(FRAGCOORD.z+0.000008>=opaque_depth) { discard; }
 ALBEDO=tint.rgb;
 ALPHA=tint.a;
}
