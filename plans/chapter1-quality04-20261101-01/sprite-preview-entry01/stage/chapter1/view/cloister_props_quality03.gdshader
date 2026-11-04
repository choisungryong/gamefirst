shader_type spatial;
// Baked-camera 2.5D props share one texture and one ArrayMesh surface.
// Alpha scissor keeps depth ownership deterministic without transparent sorting.
// https://docs.godotengine.org/en/4.5/tutorials/shaders/shader_reference/spatial_shader.html
render_mode unshaded, cull_disabled;
uniform sampler2D atlas_texture : source_color, filter_linear_mipmap;
uniform vec2 hero_position = vec2(0.0);
varying vec2 world_xz;
float pool(vec2 p,vec2 center) {
 return pow(clamp(1.0-distance(p,center)/7.0,0.0,1.0),1.7);
}
void vertex() { world_xz=(MODEL_MATRIX*vec4(VERTEX,1.0)).xz; }
void fragment() {
 vec4 tex=texture(atlas_texture,UV);
 // Authored shadows remain legible; the six brazier positions share the ground's
 // warm pools instead of leaving all unshaded impostors evenly cold and bright.
 float warmth=0.0;
 for(int side=-1;side<=1;side+=2) {
  float x=float(side)*19.7;
  warmth=max(warmth,max(pool(world_xz,vec2(x,-14.0)),max(pool(world_xz,vec2(x,2.0)),pool(world_xz,vec2(x,18.0)))));
 }
 vec3 light_tint=mix(vec3(.87,.93,1.0),vec3(1.28,1.08,.81),warmth*.78);
 ALBEDO=tex.rgb*COLOR.rgb*light_tint;
 // Only tall perimeter art uses a bounded screen-door fade around the hero.
 // Low nonblocking foliage retains its density; no transparent sorting pass.
 float fade=COLOR.a*(1.0-smoothstep(.65,1.8,distance(world_xz,hero_position)))*.76;
 float screen_hash=fract(sin(dot(floor(FRAGCOORD.xy),vec2(12.9898,78.233)))*43758.5453);
 if(screen_hash<fade)discard;
 ALPHA=tex.a;
 ALPHA_SCISSOR_THRESHOLD=.18;
}
