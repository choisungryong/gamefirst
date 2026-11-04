from pathlib import Path
HERE=Path(__file__).parent;ROOT=Path('C:/Project/d2r-combat-baseline');OUT=ROOT/'plans/chapter1-quality04-20261101-01/full14'
s=(OUT/'run_runtime.py').read_text(encoding='utf-8').replace('mode=sys.argv[1];run_id=sys.argv[2]','mode="preview";run_id="gpu-cold01"').replace("HERE=Path(__file__).resolve().parent","HERE=Path('C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/full14')")
s=s.replace("'--chapter1-quit-after=520'","'--chapter1-quit-after=520','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131'")
p=OUT/'run_gpu_cold01.py';assert not p.exists();p.write_text(s,encoding='utf-8');print(str(p))
