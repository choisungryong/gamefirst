shader_type spatial;
render_mode unshaded, cull_disabled, blend_add, depth_draw_never, fog_disabled;
// Preserve instance scale when billboarding (Godot4.5 spatial shader built-ins).
// https://docs.godotengine.org/en/4.5/tutorials/shaders/shader_reference/spatial_shader.html
varying vec4 bolt_data;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+1.),f.x),f.y);}
void vertex(){
 bolt_data=INSTANCE_CUSTOM;
 vec3 scale=vec3(length(MODEL_MATRIX[0].xyz),length(MODEL_MATRIX[1].xyz),length(MODEL_MATRIX[2].xyz));VERTEX*=scale;
 float a=bolt_data.x*6.2831853-3.14159265;
 VERTEX.xy=mat2(vec2(cos(a),sin(a)),vec2(-sin(a),cos(a)))*VERTEX.xy;
 MODELVIEW_MATRIX=VIEW_MATRIX*mat4(INV_VIEW_MATRIX[0],INV_VIEW_MATRIX[1],INV_VIEW_MATRIX[2],MODEL_MATRIX[3]);
}
void fragment(){
 vec2 p=vec2((UV.x-.68)*2.,(UV.y-.5)*2.);
 float n=noise(vec2(p.x*9.-TIME*16.+bolt_data.w*7.,p.y*11.));
 // Fire nose remains at the existing paid UV origin; no geometry shift.
 float tip=exp(-dot(p*vec2(5.2,4.8),p*vec2(5.2,4.8)));
 float along=clamp((p.x+1.32)/1.45,0.,1.);
 float width=mix(.055,.25,along)*(1.-smoothstep(.02,.38,p.x));
 float center=sin(p.x*12.-TIME*21.+bolt_data.w*5.)*.035*(1.-along);
 float tail=(1.-smoothstep(width*.25,width,abs(p.y+center)))*smoothstep(-1.36,-1.05,p.x)*(1.-smoothstep(.06,.30,p.x));
 float filament=(1.-smoothstep(.008,.040,abs(p.y+center)))*smoothstep(-1.15,-.45,p.x)*(1.-smoothstep(.0,.16,p.x));
 vec2 rim=smoothstep(vec2(.02),vec2(.10),UV)*(1.-smoothstep(vec2(.90),vec2(.98),UV));
 float support=rim.x*rim.y;
 float shape=max(tail*(.38+n*.48),tip)*support;
 vec3 color=mix(vec3(.78,.055,.004),vec3(1.,.34,.018),clamp(n+along*.30,0.,1.));
 vec3 core=(vec3(1.,.86,.46)*tip*1.75+vec3(1.,.52,.10)*filament*.35)*support;
 if(bolt_data.y>.3 && bolt_data.y<.8){
  // Keep the paid point at the white nose; the faceted body trails behind.
  p=vec2((UV.x-.5)*2.,(UV.y-.5)*2.);
  float extent=max(0.,.21-abs(p.x+.32)*.39);
  float aa=max(fwidth(p.y),.008);
  float lance=(1.-smoothstep(extent,extent+aa,abs(p.y)))*smoothstep(-1.,-.82,p.x)*(1.-smoothstep(.08,.14,p.x));
  float spine=(1.-smoothstep(.014,.055,abs(p.y)))*smoothstep(-.88,-.7,p.x)*(1.-smoothstep(.03,.13,p.x));
  float ridge=smoothstep(-.025,.025,p.y+p.x*.12);
  shape=lance;
  color=mix(vec3(.05,.32,.56),vec3(.32,.79,.96),ridge);
  core=vec3(.76,.96,1.)*spine*1.65;
 }else if(bolt_data.y>.8){
  float shaft=(1.-smoothstep(.025,.06,abs(p.y)))*smoothstep(-.65,-.48,p.x)*(1.-smoothstep(.15,.27,p.x));
  float head=(1.-smoothstep(.0,.025,abs(p.y)-max(0.,.13-abs(p.x-.05)*.60)))*step(-.13,p.x)*step(p.x,.27);
  shape=max(shaft,head);color=vec3(.85,.16,.065);core=vec3(.32,.07,.025)*head;
 }
 ALBEDO=color*shape;EMISSION=(color*shape+core)*(1.5+bolt_data.z*.8);ALPHA=clamp(shape,0.,1.);
}
