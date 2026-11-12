shader_type spatial;
render_mode unshaded, cull_disabled, blend_mix, depth_draw_never, fog_disabled;
varying vec4 ember_data;
float hash43(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float noise43(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash43(i),hash43(i+vec2(1,0)),f.x),mix(hash43(i+vec2(0,1)),hash43(i+1.),f.x),f.y);}
void vertex(){
 ember_data=INSTANCE_CUSTOM;
 vec3 scale43=vec3(length(MODEL_MATRIX[0].xyz),length(MODEL_MATRIX[1].xyz),length(MODEL_MATRIX[2].xyz));
 VERTEX*=scale43;
 MODELVIEW_MATRIX=VIEW_MATRIX*mat4(INV_VIEW_MATRIX[0],INV_VIEW_MATRIX[1],INV_VIEW_MATRIX[2],MODEL_MATRIX[3]);
}
void fragment(){
 float age=clamp(ember_data.x,0.,1.);
 vec2 p=UV*2.-1.;
 float n=noise43(vec2(p.x*5.,p.y*6.+age*8.)+ember_data.w*11.);
 float detail=noise43(vec2(p.x*10.,p.y*12.+age*13.)+ember_data.w*17.);
 vec2 rim=smoothstep(vec2(.025),vec2(.16),UV)*(1.-smoothstep(vec2(.84),vec2(.975),UV));
 float support=rim.x*rim.y;
 float height=1.-UV.y;
 float warp=p.x+(n-.5)*(.13+.20*height);
 float width=mix(.70,.08,pow(height,1.35));
 float tongue=(1.-smoothstep(width*.44,width,abs(warp)))*(1.-smoothstep(.62,.93,height+(detail-.5)*.19));
 float dome=1.-smoothstep(.35,.95,length(vec2(p.x*.95,(p.y+.10)*1.04))+(n-.5)*.14);
 float body=support*dome;
 // One early cream-hot center resolves into separate, low red embers.
 // All motion uses the inherited paid instance age, including pause/resume.
 float ignition=(1.-smoothstep(.03,.24,age))*exp(-dot(p-vec2(0,.27),p-vec2(0,.27))*15.);
 float flame=body*tongue*pow(1.-age,2.)*mix(.45,1.,detail);
 float erosion=smoothstep(.38+age*.34,.64+age*.25,detail);
 float embers=body*erosion*smoothstep(.10,.32,age)*(1.-smoothstep(.58,.98,age));
 vec3 coal=vec3(.15,.018,.003);
 ALBEDO=mix(coal,vec3(.92,.16,.012),clamp(flame*1.8,0.,1.));
 EMISSION=vec3(1.,.34,.025)*flame*2.0+vec3(1.,.82,.40)*ignition*support*2.2+vec3(.80,.065,.004)*embers*.75;
 ALPHA=clamp(body*(tongue*.29*pow(1.-age,1.8)+embers*.14)+ignition*support*.26,0.,.60);
}
