shader_type spatial;
render_mode unshaded, fog_disabled, depth_draw_never, depth_test_disabled, cull_back;
// Godot4.5 reversed Z: greater depth is nearer. Only hidden fragments tint.
// https://docs.godotengine.org/en/4.5/tutorials/shaders/advanced_postprocessing.html
uniform sampler2D scene_depth : hint_depth_texture, repeat_disable, filter_nearest;
uniform vec4 tint : source_color = vec4(0.95,0.72,0.30,0.34);
void fragment() {
 float opaque_depth=textureLod(scene_depth,SCREEN_UV,0.0).r;
 vec4 scene_view=INV_PROJECTION_MATRIX*vec4(SCREEN_UV*2.0-1.0,opaque_depth,1.0);
 vec4 fragment_view=INV_PROJECTION_MATRIX*vec4(SCREEN_UV*2.0-1.0,FRAGCOORD.z,1.0);
 float scene_distance=-scene_view.z/scene_view.w;
 float fragment_distance=-fragment_view.z/fragment_view.w;
 // World-space tolerance avoids tinting the visible mesh's own depth.
 if(fragment_distance<=scene_distance+0.035) { discard; }
 ALBEDO=tint.rgb;
 ALPHA=tint.a;
}
