shader_type spatial;
// Outline only: the hero's actual Sprite3D keeps normal depth testing.
// https://docs.godotengine.org/en/4.5/tutorials/shaders/shader_reference/spatial_shader.html
render_mode unshaded, cull_disabled, blend_mix, depth_draw_never, depth_test_disabled, fog_disabled;
uniform sampler2D source_tex : source_color, filter_linear;
uniform vec2 uv_min = vec2(0.0);
uniform vec2 uv_size = vec2(1.0);
uniform vec2 local_texel = vec2(.004);
uniform float strength = 0.0;
float silhouette(vec2 p) {
 if (p.x<0.0 || p.x>1.0 || p.y<0.0 || p.y>1.0) return 0.0;
 return texture(source_tex,uv_min+p*uv_size).a;
}
void vertex() {
 vec3 scale=vec3(length(MODEL_MATRIX[0].xyz),length(MODEL_MATRIX[1].xyz),length(MODEL_MATRIX[2].xyz));
 VERTEX*=scale;
 MODELVIEW_MATRIX=VIEW_MATRIX*mat4(INV_VIEW_MATRIX[0],INV_VIEW_MATRIX[1],INV_VIEW_MATRIX[2],MODEL_MATRIX[3]);
}
void fragment() {
 float body=silhouette(UV);
 float edge=0.0;
 for (int x=-1;x<=1;x++) {
  for (int y=-1;y<=1;y++) edge=max(edge,silhouette(UV+vec2(float(x),float(y))*local_texel*2.3));
 }
 // No filled silhouette or full-size luminous disc. The opaque body is removed.
 float outline=clamp(edge-body,0.0,1.0);
 ALBEDO=vec3(.92,.73,.43);
 EMISSION=vec3(.82,.55,.22)*outline*strength*.24;
 ALPHA=outline*strength*.60;
}
