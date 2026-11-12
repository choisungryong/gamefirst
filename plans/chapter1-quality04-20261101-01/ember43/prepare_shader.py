"""Derive a fire-only shader variant; retain both nonfire branches verbatim."""
from pathlib import Path

root=Path(__file__).resolve().parents[3]
source=(root/'chapter1/view/comet_quality14.gdshader').read_text(encoding='utf-8')
start=source.index(' float tip=')
end=source.index(' if(bolt_data.y>.3')
replacement=''' // Fire nose remains at the existing paid UV origin; no geometry shift.
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
'''
derived=source[:start]+replacement+source[end:]
assert derived[derived.index(' if(bolt_data.y>.3'):]==source[end:]
destination=root/'chapter1/view/ember_core_quality43.gdshader'
with destination.open('x',encoding='utf-8') as output:output.write(derived)
print('Created fire variant; cold/hostile branches unchanged')
