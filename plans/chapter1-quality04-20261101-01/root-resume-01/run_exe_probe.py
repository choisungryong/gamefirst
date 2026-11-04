from pathlib import Path
import subprocess,json,sys
HERE=Path(__file__).resolve().parent
label=sys.argv[1];exe=Path(sys.argv[2]);command=[str(exe)]+sys.argv[3:]
assert not (HERE/(label+'-execution.json')).exists()
r=subprocess.run(command,capture_output=True,timeout=120)
data={'command':command,'actual_exit':r.returncode}
for kind,raw in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (HERE/(label+'-'+kind+'.bin')).open('xb') as f:f.write(raw)
 codec='utf-8'
 try:value=raw.decode(codec)
 except UnicodeDecodeError:codec='cp949';value=raw.decode(codec,'replace')
 data[kind]=value;data[kind+'_codec']=codec
with (HERE/(label+'-execution.json')).open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2)
print(json.dumps({'actual_exit':r.returncode,'stderr':data['stderr'],'stdout_tail':data['stdout'][-9000:]},ensure_ascii=False))
