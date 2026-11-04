from pathlib import Path
import hashlib,json,urllib.request,zipfile,shutil,time
NAME='blender-4.5.15-windows-x64.zip'
URL='https://download.blender.org/release/Blender4.5/'
BASE=Path('C:/Project/rea-tools');DOWNLOAD=BASE/'downloads'
DEST=BASE/'blender-4.5.15-windows-x64'
PROOF=Path(__file__).resolve().parent/'blender-toolchain.json'
DOWNLOAD.mkdir(exist_ok=True)
archive=DOWNLOAD/NAME;checksums=DOWNLOAD/'blender-4.5.15.sha256'
assert not archive.exists() and not checksums.exists() and not DEST.exists() and not PROOF.exists(),'Preserve earlier downloads/toolchain'
assert shutil.disk_usage(BASE).free>3*1024**3
started=time.time()
req=urllib.request.Request(URL+checksums.name,headers={'User-Agent':'AshenCloister-toolchain-setup'})
with urllib.request.urlopen(req,timeout=60) as response:data=response.read()
with checksums.open('xb') as f:f.write(data)
expected=[s.split()[0] for s in data.decode().splitlines() if s.split()[-1].lstrip('*')==NAME]
assert len(expected)==1 and len(expected[0])==64
digest=hashlib.sha256();count=0;next_report=50*1024**2
req=urllib.request.Request(URL+NAME,headers={'User-Agent':'AshenCloister-toolchain-setup'})
with urllib.request.urlopen(req,timeout=180) as response,archive.open('xb') as output:
    while True:
        block=response.read(4*1024**2)
        if not block:break
        output.write(block);digest.update(block);count+=len(block)
        if count>=next_report:
            print(json.dumps({'downloaded_mb':round(count/1024**2)}),flush=True);next_report+=50*1024**2
assert digest.hexdigest()==expected[0],{'actual':digest.hexdigest(),'expected':expected[0]}
with zipfile.ZipFile(archive) as z:
    members=z.infolist()
    for member in members:
        target=(BASE/member.filename).resolve()
        assert target.is_relative_to(DEST.resolve()),member.filename
    assert sum(m.file_size for m in members)<3*1024**3
    z.extractall(BASE)
exe=DEST/'blender.exe';assert exe.is_file()
with PROOF.open('x',encoding='utf-8') as f:
    json.dump({'official_directory':URL,'archive':str(archive),'bytes':count,'sha256':digest.hexdigest(),'official_checksum_match':True,'checksum_file':str(checksums),'extracted_directory':str(DEST),'exe_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'seconds':time.time()-started,'scope':'Portable official Blender dependency; no system installation/environment edits; untrusted blend files will use --disable-autoexec'},f,indent=2)
print(json.dumps({'ready':str(exe),'sha256_verified':True,'seconds':time.time()-started}))
