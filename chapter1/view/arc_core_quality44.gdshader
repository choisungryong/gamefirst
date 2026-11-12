shader_type spatial;
render_mode unshaded, cull_disabled, blend_add, depth_draw_never, fog_disabled;
void fragment(){
 float across=abs(UV.y-.5)*2.;
 float aa=max(fwidth(across),.012);
 float core=1.-smoothstep(.055,.15+aa*.30,across);
 float sheath=pow(max(0.,1.-across),2.8)*.32;
 float fade=clamp(COLOR.a,0.,1.);
 // COLOR.a is the existing paid link-age fade. No independent time or phase.
 // Keep continuity at every quad joint: UV.x is not an endpoint fade here.
 vec3 blue=mix(COLOR.rgb,vec3(.32,.43,1.),.30);
 vec3 glow=blue*sheath*fade+vec3(.86,.92,1.)*core*1.65*fade*fade;
 ALBEDO=glow;
 EMISSION=glow*1.10;
 ALPHA=clamp(sheath*fade+core*fade*fade,0.,1.);
}
