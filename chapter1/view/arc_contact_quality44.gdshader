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

 // Fire has a short directional spark, not two full-width white crossbars.
 // Cold/arc retain the existing branch above; the paid contact age is unchanged.
 if(data.g<.25){
  float spark=stroke(p*2.65,.026)*(1.-smoothstep(.02,.72,age));
  float hot=exp(-dot(p,p)*110.)*pow(1.-age,2.);
  float ember=exp(-dot(p,p)*35.)*pow(1.-age,1.6);
  ALBEDO=vec3(1.,.77,.34)*spark*fade*1.25+vec3(1.,.91,.62)*hot*1.4+vec3(.95,.17,.012)*ember*.40;
  ALPHA=clamp(spark*fade+hot+ember*.30,0.,1.);
 }

 // A short kink at the actual arc contact. Existing fire/cold paths stay above.
 if(data.g>.75){
  float kink=abs(p.x-.035)*.34-.045;
  float thread=(1.-smoothstep(.022,.060,abs(p.y-kink)))*(1.-smoothstep(.30,.52,abs(p.x)));
  float center43=exp(-dot(p,p)*120.);
  float fade44=pow(1.-age,1.8);
  ALBEDO=(vec3(.79,.88,1.)*thread*1.7+vec3(.28,.42,1.)*center43*.55)*fade44;
  ALPHA=clamp((thread+center43*.35)*fade44,0.,1.);
 }
}
