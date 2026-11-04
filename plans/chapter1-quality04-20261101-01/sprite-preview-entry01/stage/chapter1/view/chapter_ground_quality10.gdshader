shader_type spatial;
// Godot 4.5 spatial shader built-ins and sampler syntax:
// https://docs.godotengine.org/en/4.5/tutorials/shaders/shader_reference/spatial_shader.html
uniform sampler2D flagstone : source_color, filter_linear_mipmap, repeat_enable;
uniform sampler2D soil : source_color, filter_linear_mipmap, repeat_enable;
uniform bool has_flagstone = false;
uniform bool has_soil = false;
varying vec2 world_xz;

float hash21(vec2 p) { return fract(sin(dot(p, vec2(127.1,311.7))) * 43758.5453); }
float noise21(vec2 p) {
 vec2 a=floor(p), b=fract(p); b=b*b*(3.0-2.0*b);
 return mix(mix(hash21(a),hash21(a+vec2(1.,0.)),b.x),mix(hash21(a+vec2(0.,1.)),hash21(a+vec2(1.)),b.x),b.y);
}
vec3 stone_sample(vec2 uv) {
 // Offset entire texture samples, not their derivatives. Narrow smooth blends
 // remove the repeated sheet boundary without turning grout into four ghosts.
 vec2 cell=floor(uv), f=smoothstep(vec2(.37),vec2(.63),fract(uv));
 vec2 dx=dFdx(uv),dy=dFdy(uv);
 vec2 o00=vec2(hash21(cell),hash21(cell+71.3))*7.;
 vec2 o10=vec2(hash21(cell+vec2(1.,0.)),hash21(cell+vec2(72.3,71.3)))*7.;
 vec2 o01=vec2(hash21(cell+vec2(0.,1.)),hash21(cell+vec2(71.3,72.3)))*7.;
 vec2 o11=vec2(hash21(cell+vec2(1.)),hash21(cell+72.3))*7.;
 return mix(mix(textureGrad(flagstone,uv+o00,dx,dy).rgb,textureGrad(flagstone,uv+o10,dx,dy).rgb,f.x),mix(textureGrad(flagstone,uv+o01,dx,dy).rgb,textureGrad(flagstone,uv+o11,dx,dy).rgb,f.x),f.y);
}
void vertex() { world_xz=(MODEL_MATRIX*vec4(VERTEX,1.0)).xz; }
void fragment() {
 vec2 p=world_xz;
 float zone=clamp(floor((p.x+24.)/48.),0.,2.);
 p.x-=zone*48.;
 float coarse=noise21(p*.14);
 float weather=noise21(p*.38+23.7);
 float court=max(abs(p.x)-6.5,abs(p.y+1.0)-8.0)+(coarse-.5)*2.4;
 float courtyard=1.-smoothstep(-.9,1.8,court);
 float nave=1.-smoothstep(2.6,4.4,abs(p.x+sin(p.y*.16)*.45)+(weather-.5)*.8);
 float crossing=1.-smoothstep(2.2,3.7,abs(p.y+2.+sin(p.x*.14)*.3));
 float paving=clamp(max(courtyard*.94,max(nave,crossing)),0.,1.);
 float nave_court=1.-smoothstep(12.,16.,max(abs(p.x),abs(p.y)*.85));
 float sanctuary=1.-smoothstep(17.,20.,length(p));
 paving=mix(paving,nave_court,step(.5,zone));
 paving=mix(paving,sanctuary,step(1.5,zone));
 paving=max(paving,1.-smoothstep(2.7,3.5,abs(p.y)));
 vec3 stone=has_flagstone?stone_sample(p*.175):vec3(.24,.25,.25);
 vec3 earth=has_soil?texture(soil,p*.21+vec2(.13,.37)).rgb:vec3(.14,.16,.13);
 // The terrain is quiet enough for warm fire and icy silhouettes to carry combat.
 stone=mix(vec3(dot(stone,vec3(.3,.59,.11))),stone,.72)*vec3(.64,.68,.71);
 earth=mix(vec3(dot(earth,vec3(.3,.59,.11))),earth,.7)*vec3(.72,.76,.66);
 // Damp moss joins the cutout foliage to the soil without a flat black verge.
 float moss=smoothstep(.43,.76,noise21(p*.44+41.))*smoothstep(.24,.7,coarse);
 earth=mix(earth,earth*vec3(.79,1.10,.72),moss*.48);
 vec3 surface=mix(earth,stone,paving);
 surface*=mix(.84,1.08,coarse);
 if(zone>1.5) {
  float rings=1.-smoothstep(.035,.09,abs(fract((length(p)-2.)/3.)-.5));
  surface=mix(surface*vec3(.9,.91,1.04),vec3(.24,.20,.13),rings*.40*paving);
 }
 ALBEDO=surface;
	// Small lighting relief from the independently generated stone image. This
	// changes only shading; the walkable floor remains the Chapter09 plane.
	float h=dot(stone,vec3(.3,.59,.11))*.12*paving;
	vec2 px=dFdx(world_xz),py=dFdy(world_xz);
	float determinant=px.x*py.y-px.y*py.x;
	if(abs(determinant)>.0000001) {
	 float hx=(dFdx(h)*py.y-dFdy(h)*px.y)/determinant;
	 float hz=(dFdy(h)*px.x-dFdx(h)*py.x)/determinant;
	 vec3 world_normal=normalize(vec3(-hx,1.0,-hz));
	 NORMAL=normalize((VIEW_MATRIX*vec4(world_normal,0.0)).xyz);
	}
 ROUGHNESS=mix(.96,.88,paving);
 SPECULAR=.14;
}
