shader_type spatial;
render_mode unshaded, cull_disabled, blend_add, depth_draw_never;
void fragment(){ALBEDO=COLOR.rgb;EMISSION=COLOR.rgb*.85;ALPHA=COLOR.a;}
