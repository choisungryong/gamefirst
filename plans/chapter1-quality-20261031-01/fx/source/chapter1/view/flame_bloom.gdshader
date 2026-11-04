shader_type spatial;
render_mode unshaded, cull_disabled, blend_mix, depth_draw_never, fog_disabled;
varying vec4 bloom_data;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+1.),f.x),f.y);}
void vertex(){
 bloom_data=INSTANCE_CUSTOM;
 vec3 scale=vec3(length(MODEL_MATRIX[0].xyz),length(MODEL_MATRIX[1].xyz),length(MODEL_MATRIX[2].xyz));VERTEX*=scale;
 MODELVIEW_MATRIX=VIEW_MATRIX*mat4(INV_VIEW_MATRIX[0],INV_VIEW_MATRIX[1],INV_VIEW_MATRIX[2],MODEL_MATRIX[3]);
}
void fragment(){
 float age=bloom_data.x;vec2 p=UV*2.-1.;float n=noise(vec2(p.x*4.,p.y*5.+age*6.)+bloom_data.w*9.);
 float dome=1.-smoothstep(.52,.96,length(p*vec2(1.,.85)+vec2(0.,age*.35))+(n-.5)*.23);
 float fire=pow(1.-age,1.6)*(1.-smoothstep(-.4,.65,p.y+n*.35-age*.9));float heat=fire*dome;
 vec3 smoke=mix(vec3(.045,.038,.032),vec3(.13,.105,.08),n);
 ALBEDO=mix(smoke,vec3(1.,.20,.006),clamp(fire*1.7,0.,1.));
 EMISSION=vec3(1.,.36,.015)*heat*3.3+vec3(1.,.82,.36)*pow(heat,4.)*2.;ALPHA=dome*(1.-age)*.64;
}
