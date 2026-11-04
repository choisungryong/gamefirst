shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never;
void fragment() {
 float r=length((UV-.5)*2.);
 ALBEDO=vec3(.015,.025,.025);
 ALPHA=(1.-smoothstep(.15,1.,r))*.46;
}
