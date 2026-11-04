from pathlib import Path
import json,struct,hashlib,copy,numpy as np
R=Path('C:/Project/d2r-combat-baseline');P=R/'chapter1/art/skeleton_outlaw/v01/skeleton_outlaw.glb';A=R/'chapter1/art/skeleton_outlaw/v02';O=R/'plans/chapter1-quality04-20261101-01/monster34/merge01';assert not A.exists() and not O.exists()
b=P.read_bytes();jn=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+jn]);binary=bytearray(b[28+jn:]);original_animation=copy.deepcopy(d['animations']);ct={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'};dim={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def access(index):
 a=d['accessors'][index];v=d['bufferViews'][a['bufferView']];width=dim[a['type']];dtype=np.dtype(ct[a['componentType']]);off=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',width*dtype.itemsize)
 return np.ndarray((a['count'],width),dtype=dtype,buffer=binary,offset=off,strides=(stride,dtype.itemsize)).copy()
skins=[access(s['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1).astype(float) for s in d['skins']];common=skins[0];nodes=[(i,x) for i,x in enumerate(d['nodes']) if 'mesh' in x];groups={};errors=[];sources=[];triangles=0
for ni,node in nodes:
 assert d['skins'][node['skin']]['joints']==d['skins'][0]['joints'];skin=skins[node['skin']];B=np.linalg.inv(common[0])@skin[0];bind_error=float(np.max(np.abs(common@B-skin)));assert bind_error<2e-6
 for primitive in d['meshes'][node['mesh']]['primitives']:
  assert primitive.get('mode',4)==4
  attrs={k:access(v) for k,v in primitive['attributes'].items()};vertices=attrs['POSITION'].astype(float);N=len(vertices);newv=(np.c_[vertices,np.ones(N)]@B.T)[:,:3].astype('<f4');newn=attrs['NORMAL'].astype(float)@np.linalg.inv(B[:3,:3]);newn/=np.maximum(np.linalg.norm(newn,axis=1,keepdims=True),1e-12);t=attrs['TANGENT'].copy();xyz=t[:,:3].astype(float)@B[:3,:3].T;xyz/=np.maximum(np.linalg.norm(xyz,axis=1,keepdims=True),1e-12);t[:,:3]=xyz
  attrs['POSITION']=newv;attrs['NORMAL']=newn.astype('<f4');attrs['TANGENT']=t.astype('<f4');attrs.setdefault('JOINTS_1',np.zeros((N,4),dtype='<u2'));attrs.setdefault('WEIGHTS_1',np.zeros((N,4),dtype='<f4'))
  error=0.0
  for part in [0,1]:
   joints=attrs['JOINTS_'+str(part)];weights=attrs['WEIGHTS_'+str(part)]
   for c in range(4):
    selected=weights[:,c]>1e-8
    if not np.any(selected):continue
    js=joints[selected,c].astype(int);v0=np.c_[vertices[selected],np.ones(np.count_nonzero(selected))];v1=np.c_[newv[selected].astype(float),np.ones(np.count_nonzero(selected))]
    expected=np.einsum('nij,nj->ni',skin[js],v0);actual=np.einsum('nij,nj->ni',common[js],v1);error=max(error,float(np.max(np.abs(expected-actual))))
  assert error<2e-6,(node.get('name'),error);errors.append(error)
  material=d['materials'][primitive['material']];texture=material['pbrMetallicRoughness']['baseColorTexture']['index'];image=d['textures'][texture]['source'];g=groups.setdefault(image,dict(attributes={},indices=[],count=0,material=primitive['material']));indices=access(primitive['indices']).reshape(-1).astype('<u4');triangles+=len(indices)//3
  for key,value in attrs.items():g['attributes'].setdefault(key,[]).append(value)
  g['indices'].append(indices+g['count']);g['count']+=N;sources.append(dict(name=node.get('name'),vertices=N,triangles=len(indices)//3,skin=node['skin'],bind_matrix_error=bind_error,vertex_bind_error=error))
def append_accessor(arr,component,type_):
 while len(binary)%4:binary.append(0)
 offset=len(binary);raw=arr.tobytes();binary.extend(raw);vi=len(d['bufferViews']);d['bufferViews'].append(dict(buffer=0,byteOffset=offset,byteLength=len(raw)));a=dict(bufferView=vi,componentType=component,count=len(arr),type=type_)
 if type_=='VEC3':a.update(min=arr.min(axis=0).tolist(),max=arr.max(axis=0).tolist())
 ai=len(d['accessors']);d['accessors'].append(a);return ai
primitives=[];materials=[]
for image,g in sorted(groups.items()):
 material=copy.deepcopy(d['materials'][g['material']]);material['name']='Outlaw34Body' if image==0 else 'Outlaw34Axe';material['pbrMetallicRoughness']['roughnessFactor']=.79;material['pbrMetallicRoughness']['metallicFactor']=.03 if image==0 else .1;mi=len(materials);materials.append(material);attributes={}
 for key,arrays in g['attributes'].items():
  array=np.concatenate(arrays);component=5123 if key.startswith('JOINTS') else 5126;array=array.astype('<u2' if component==5123 else '<f4');attributes[key]=append_accessor(array,component,'VEC'+str(array.shape[1]))
 indices=np.concatenate(g['indices']).astype('<u4');ia=append_accessor(indices.reshape(-1,1),5125,'SCALAR');primitives.append(dict(attributes=attributes,indices=ia,material=mi,mode=4))
d['meshes']=[dict(name='Outlaw34Merged',primitives=primitives)];d['materials']=materials;d['skins']=[d['skins'][0]]
for k,(ni,node) in enumerate(nodes):
 if k==0:node['mesh']=0;node['skin']=0;node['name']='Outlaw34Merged'
 else:node.pop('mesh');node.pop('skin',None)
assert len(groups)==2 and d['animations']==original_animation
while len(binary)%4:binary.append(0)
d['buffers'][0]['byteLength']=len(binary);j=json.dumps(d,separators=(',',':'),ensure_ascii=False).encode('utf-8')
while len(j)%4:j+=b' '
result=struct.pack('<III',0x46546c67,2,12+8+len(j)+8+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary
A.mkdir(parents=True);O.mkdir();(A/'skeleton_outlaw_merged.glb').write_bytes(result);report=dict(source_sha256=hashlib.sha256(b).hexdigest(),derived_sha256=hashlib.sha256(result).hexdigest(),meshes_before=len(nodes),meshes_after=1,skins_before=len(skins),skins_after=1,surfaces=2,triangles=triangles,max_vertex_bind_error=max(errors),sources=sources,clips_unchanged=len(original_animation),scope='Canonical bind-space mesh consolidation, original joint weights/UVs/triangles/clips/textures retained. Materials consolidated by exact texture image; body metallic.03/axe.1/roughness.79. Algebraic skin equivalence only, not Godot import/GPU/adoption/quality approval.')
(O/'RESULT.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(A/'DERIVATION.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(A/'ATTRIBUTION.ko.md').write_text('# Skeleton Outlaw 병합 시안\n\nCC0 KevDev. 원출처·라이선스·보존원본은 ../v01/ATTRIBUTION.ko.md 와 SOURCE.json 참조.\n\n8mesh/6skin을같은bind공간으로변환해1mesh/2surface/1skin으로묶었다. 원본삼각형·UV·스킨가중치·저작9클립·texture이미지는유지했다. 몸금속.03/도끼.1/거칠기.79로재질정리. DERIVATION.json은수학적bind검사이며실제엔진/움직임/제품품질승인이아니다. 현재제품33과미연결이다.\n',encoding='utf-8');assert hashlib.sha256(P.read_bytes()).hexdigest()==report['source_sha256'];print({k:v for k,v in report.items() if k not in ['sources','scope']})
