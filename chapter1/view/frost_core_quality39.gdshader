shader_type spatial;
render_mode unshaded, cull_disabled, blend_mix, depth_draw_never;
// Frost-only replacement batch. Stable facets have no wall-clock TIME motion.
varying vec4 bolt_data;
void vertex(){
 bolt_data=INSTANCE_CUSTOM;
 vec3 scale=vec3(length(MODEL_MATRIX[0].xyz),length(MODEL_MATRIX[1].xyz),length(MODEL_MATRIX[2].xyz));
 VERTEX*=scale;
 float a=bolt_data.x*6.2831853-3.14159265;
 VERTEX.xy=mat2(vec2(cos(a),sin(a)),vec2(-sin(a),cos(a)))*VERTEX.xy;
 MODELVIEW_MATRIX=VIEW_MATRIX*mat4(INV_VIEW_MATRIX[0],INV_VIEW_MATRIX[1],INV_VIEW_MATRIX[2],MODEL_MATRIX[3]);
}
void fragment(){
 vec2 p=(UV-.5)*2.;
 // A short solid spear with a bright central seam and a dark lower facet.
 // Its nose remains at the same paid point used by the previous frost shader.
 float width=max(0.,.19-abs(p.x+.30)*.36);
 float aa=max(fwidth(p.y),.006);
 float body=(1.-smoothstep(width,width+aa,abs(p.y)))*smoothstep(-.91,-.85,p.x)*(1.-smoothstep(.13,.17,p.x));
 float seam=(1.-smoothstep(.008,.029,abs(p.y+p.x*.018)))*body;
 float upper=smoothstep(-.015,.015,p.y+p.x*.13);
 vec3 facet=mix(vec3(.055,.22,.31),vec3(.48,.82,.88),upper);
 ALBEDO=mix(facet,vec3(.83,.98,1.),seam*.85);
 EMISSION=vec3(.35,.67,.75)*seam*.65;
 ALPHA=body*.96;
 if(ALPHA<.01)discard;
}
