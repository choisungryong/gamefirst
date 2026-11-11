shader_type spatial;
render_mode unshaded, cull_disabled, blend_mix, depth_draw_never;
varying vec4 impact_data;
void vertex(){impact_data=INSTANCE_CUSTOM;}
void fragment(){
 vec2 p=UV*2.-1.;
 float r=length(p);
 float age=impact_data.x;
 float angle_=atan(p.y,p.x);
 // Brief center snap, then six separated angular fracture spokes. The paid
 // radius and inherited .48s duration are unchanged; no broad luminous disk.
 float spoke=pow(abs(cos(angle_*3.+.18)),28.);
 float reach=mix(.20,.84,smoothstep(0.,.42,age));
 float tips=(1.-smoothstep(reach-.12,reach+.03,r))*smoothstep(.09,.23,r);
 float gaps=smoothstep(.38,.65,fract(r*5.5+angle_*.35));
 float fracture=spoke*tips*mix(.35,1.,gaps)*pow(1.-age,1.6);
 float core=exp(-r*28.)*pow(1.-age,7.);
 float shape=max(fracture,core);
 ALBEDO=mix(vec3(.17,.49,.59),vec3(.78,.94,.98),core+fracture*.4);
 EMISSION=vec3(.28,.57,.65)*fracture*.22+vec3(.8,.96,1.)*core*.8;
 ALPHA=clamp(shape*.92,0.,1.);
 if(ALPHA<.01)discard;
}
