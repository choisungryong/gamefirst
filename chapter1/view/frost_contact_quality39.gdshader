shader_type spatial;
render_mode unshaded, cull_disabled, blend_mix, depth_draw_never;
varying vec4 hit_data;
void vertex(){hit_data=INSTANCE_CUSTOM;}
void fragment(){
 vec2 p=(UV-.5)*2.;
 float angle_=hit_data.b*3.14159265;
 p=mat2(vec2(cos(angle_),sin(angle_)),vec2(-sin(angle_),cos(angle_)))*p;
 float age=hit_data.r;
 // The existing actual-hit .13s accent becomes three short separated chips,
 // not another radial star. No new hit, contact count, or lifetime is created.
 float outward=age*.20;
 float left=abs(p.x+.16+outward)*.75+abs(p.y-.06)*3.;
 float right=abs(p.x-.19-outward)*.85+abs(p.y+.08)*3.4;
 float top=abs(p.x-.02)*3.5+abs(p.y-.15-outward)*.9;
 float chips=1.-smoothstep(.10,.13,min(min(left,right),top));
 float center=exp(-dot(p,p)*130.)*pow(1.-age,4.);
 float fade=pow(1.-age,1.2);
 ALBEDO=mix(vec3(.29,.65,.74),vec3(.91,.99,1.),center);
 EMISSION=vec3(.45,.80,.87)*center*.65;
 ALPHA=clamp(chips*fade+center,0.,1.);
 if(ALPHA<.01)discard;
}
