shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never;
// Bounded contact patches ground authored impostors without cascade shadows.
void fragment() {
 vec2 p=(UV-.5)*2.;
 float shape=max(0.,1.-dot(p,p));
 ALBEDO=vec3(.014,.018,.022);
 ALPHA=shape*shape*COLOR.a;
}
