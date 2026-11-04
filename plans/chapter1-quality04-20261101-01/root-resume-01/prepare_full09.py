from pathlib import Path
ROOT=Path('C:/Project/d2r-combat-baseline');old=ROOT/'plans/chapter1-quality04-20261101-01/full08';dest=old.with_name('full09')
assert not dest.exists();dest.mkdir()
s=(old/'package_full08.py').read_text(encoding='utf-8').replace('candidate08','candidate09').replace('20261101-08','20261101-09').replace('Quality08','Quality09')
(dest/'package_full09.py').write_text(s,encoding='utf-8')
(dest/'RUN.ko.md').write_text((old/'RUN.ko.md').read_text(encoding='utf-8').replace('후보08','후보09')+'\n고정FPS QA 종료에서 오디오 서버가 해제할 실제 시간을 기다리도록 종료 경로를 수정했습니다.\n',encoding='utf-8')
(dest/'run_runtime.py').write_text((old/'run_runtime.py').read_text(encoding='utf-8'),encoding='utf-8')
print(str(dest))
