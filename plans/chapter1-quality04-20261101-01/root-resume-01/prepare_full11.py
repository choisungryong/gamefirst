from pathlib import Path
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OLD=BASE/'full10';OUT=BASE/'full11'
assert not OUT.exists();OUT.mkdir()
s=(OLD/'package_full10.py').read_text(encoding='utf-8').replace('candidate10','candidate11').replace('20261101-10','20261101-11').replace('Quality10','Quality11')
s=s.replace("(STAGE/'export_presets.cfg').write_text(preset,encoding='utf-8')","assert preset.count(',*.md')==1\n    preset=preset.replace(',*.md','')\n    (STAGE/'export_presets.cfg').write_text(preset,encoding='utf-8')")
(OUT/'package_full11.py').write_text(s,encoding='utf-8')
(OUT/'run_runtime.py').write_text((OLD/'run_runtime.py').read_text(encoding='utf-8'),encoding='utf-8')
(OUT/'RUN.ko.md').write_text((OLD/'RUN.ko.md').read_text(encoding='utf-8').replace('후보10','후보11')+'\n후보10의 모델 출처 MD 누락을 고쳤으며 해당 실패 실행은 보존했습니다.\n',encoding='utf-8')
p=ROOT/'chapter1/art/rigged_mage/v01/ATTRIBUTION.ko.md'
(OUT/'ATTRIBUTION-before-package11.ko.md').write_bytes(p.read_bytes())
p.write_text(p.read_text(encoding='utf-8').replace('후보10에서 영웅 표현으로 사용합니다.','표현 개선 후보11에서 영웅 표현으로 사용합니다.'),encoding='utf-8')
print(str(OUT))
