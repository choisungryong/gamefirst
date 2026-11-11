shader_type spatial;
render_mode unshaded, cull_disabled, blend_mix, depth_draw_never;
varying float age;
void vertex(){age=INSTANCE_CUSTOM.x;}
void fragment(){
 vec2 p=UV*2.-1.;
 // Four small facets at release; no full-screen flash or persistent aura.
 float diamond=abs(p.x)+abs(p.y);
 float edge=(1.-smoothstep(.38,.44,diamond))*smoothstep(.22,.30,diamond);
 float center=exp(-dot(p,p)*80.);
 float fade=pow(1.-age,2.);
 ALBEDO=mix(vec3(.27,.61,.70),vec3(.91,.99,1.),center);
 EMISSION=vec3(.4,.75,.83)*center*.65;
 ALPHA=clamp((edge*.75+center)*fade,0.,1.);
 if(ALPHA<.01)discard;
}
