shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, fog_disabled;
varying vec4 data;
void vertex(){data=INSTANCE_CUSTOM;}
float stroke(vec2 p,float width) {
 float taper=pow(clamp(1.0-abs(p.x),0.0,1.0),.65);
 float aa=max(fwidth(p.y),.008);
 return (1.0-smoothstep(width*taper,width*taper+aa,abs(p.y)))*step(abs(p.x),1.0);
}
void fragment(){
 vec2 p=(UV-.5)*2.0;
 float a=data.b*3.14159265;
 p=mat2(vec2(cos(a),sin(a)),vec2(-sin(a),cos(a)))*p;
 float age=clamp(data.r,0.0,1.0);
 float white=stroke(p,.022)*.95;
 vec2 q=mat2(vec2(.5,.866),vec2(-.866,.5))*p;
 white+=stroke(q*vec2(1.45,1.0),.018)*.72;
 float center=pow(max(0.0,1.0-length(p)*4.5),3.0);
 float halo=exp(-dot(p,p)*21.0)*.20;
 vec3 edge=mix(vec3(1.0,.40,.10),vec3(.30,.80,1.0),step(.25,data.g));
 edge=mix(edge,vec3(.61,.63,1.0),step(.75,data.g));
 float fade=pow(1.0-age,1.45);
 ALBEDO=(vec3(1.0,.97,.87)*(white+center*1.3)+edge*halo)*fade*1.8;
 ALPHA=clamp((white+center+halo)*fade,0.0,1.0);
}
