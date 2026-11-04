shader_type spatial;
render_mode unshaded, cull_disabled;
uniform float age=0.0;
void vertex() {
 vec3 world=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
 float wind=sin(world.x*.61+world.z*.39+age*1.8)*.026+sin(world.x*1.2-world.z*.44+age*2.7)*.012;
 VERTEX.x+=wind*UV.y*UV.y;
 VERTEX.z+=wind*.62*UV.y*UV.y;
}
void fragment() {
 // Match the authored-light perimeter props, with darker roots and soft tips.
 // Thin physical blades lost their shape under the current low ambient light.
 ALBEDO=COLOR.rgb*mix(.85,1.20,UV.y);
}
