shader_type spatial;
// Spatial MODEL_NORMAL_MATRIX/COLOR/PBR and sampler syntax, Godot4.5:
// https://docs.godotengine.org/en/4.5/tutorials/shaders/shader_reference/spatial_shader.html
// Existing chapter_ground.gdshader supplies the texture/noise vocabulary.
uniform sampler2D flagstone : source_color, filter_linear_mipmap, repeat_enable;
uniform sampler2D soil : source_color, filter_linear_mipmap, repeat_enable;
varying vec3 stone_world;
varying vec3 stone_normal;
float hash21(vec2 p) { return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
float noise21(vec2 p) {
 vec2 a=floor(p),b=fract(p);b=b*b*(3.0-2.0*b);
 return mix(mix(hash21(a),hash21(a+vec2(1.,0.)),b.x),mix(hash21(a+vec2(0.,1.)),hash21(a+vec2(1.)),b.x),b.y);
}
void vertex() {
 stone_world=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
 stone_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);
}
void fragment() {
 vec3 n=pow(abs(normalize(stone_normal)),vec3(5.));n/=max(dot(n,vec3(1.)),.001);
 vec3 p=stone_world*.32;
 vec3 stone=texture(flagstone,p.yz).rgb*n.x+texture(flagstone,p.xz).rgb*n.y+texture(flagstone,p.xy).rgb*n.z;
 vec3 dust=texture(soil,stone_world.xz*.27+stone_world.y*.07).rgb;
 float mineral=noise21(stone_world.xy*2.1+stone_world.z*.31);
 float weather=noise21(stone_world.xz*.47+stone_world.y*.43);
 float grey=dot(stone,vec3(.30,.59,.11));
 vec3 tint=mix(vec3(dot(COLOR.rgb,vec3(.30,.59,.11))),COLOR.rgb,.30);
 vec3 dressed=mix(vec3(grey),stone,.30)*tint*vec3(1.28,1.23,1.08);
 dressed=mix(dressed,dressed*vec3(.79,1.02,.65)+dust*.10,smoothstep(.48,.78,weather)*.40);
 dressed*=mix(.87,1.15,mineral);
 ALBEDO=dressed;
 ROUGHNESS=.94;
 SPECULAR=.17;
}
