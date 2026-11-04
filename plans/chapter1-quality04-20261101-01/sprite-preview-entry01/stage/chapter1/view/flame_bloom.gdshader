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
 float age=clamp(bloom_data.x,0.,1.);vec2 p=UV*2.-1.;
 float n=noise(vec2(p.x*4.,p.y*5.+age*7.)+bloom_data.w*9.);
 float detail=noise(vec2(p.x*9.,p.y*11.+age*12.)+bloom_data.w*17.);
 // Explicit support reaches zero before every quad edge. The silhouette and
 // emissive energy share this support, so no hot billboard corners survive.
 vec2 rim=smoothstep(vec2(.015),vec2(.18),UV)*(1.-smoothstep(vec2(.82),vec2(.985),UV));
 float edge=rim.x*rim.y;
 float height=1.-UV.y;
 float warp=p.x+(n-.5)*(.17+.22*height);
 float width=mix(.76,.12,pow(height,1.25));
 float sides=1.-smoothstep(width*.55,width,abs(warp));
 float dome=1.-smoothstep(.45,.93,length(vec2(p.x*.9,(p.y+.12)*1.04))+(n-.5)*.20);
 float tongue=sides*(1.-smoothstep(.57,.93,height+(detail-.5)*.24));
 float body=edge*dome;
 float burn=pow(1.-age,1.7);
 float heat=body*tongue*burn*mix(.42,1.,detail);
 float core=pow(clamp(tongue*(1.-abs(warp)/max(width,.01)),0.,1.),3.)*body*burn;
 vec3 smoke=mix(vec3(.035,.030,.026),vec3(.095,.070,.047),n);
 ALBEDO=mix(smoke,vec3(.95,.17,.008),clamp(heat*1.4,0.,1.));
 EMISSION=vec3(1.,.24,.008)*heat*2.4+vec3(1.,.78,.30)*core*3.2;
 ALPHA=body*(1.-age)*(.12+.43*tongue)*mix(.55,1.,detail);
}
