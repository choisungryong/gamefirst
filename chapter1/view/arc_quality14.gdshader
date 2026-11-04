shader_type spatial;
render_mode unshaded, cull_disabled, blend_add, depth_draw_never, fog_disabled;
void fragment(){
 float distance_=abs(UV.y-.5)*2.;
 float halo=pow(max(0.,1.-distance_),2.)*.65;
 float core=1.-smoothstep(.08,.26,distance_);
 float fade=COLOR.a;
 vec3 glow=COLOR.rgb*halo+vec3(.88,.96,1.)*core*1.7;
 ALBEDO=glow*fade;EMISSION=glow*fade*1.15;ALPHA=clamp((halo+core)*fade,0.,1.);
}
