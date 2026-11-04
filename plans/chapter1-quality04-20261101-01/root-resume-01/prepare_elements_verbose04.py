from pathlib import Path
HERE=Path(__file__).parent
s=(HERE/'run_elements_arena03.py').read_text(encoding='utf-8').replace('chapter1-elements-20261101-03','chapter1-elements-20261101-04').replace("OUT=BASE/'elements14/arena03'","OUT=BASE/'elements14/arena04'").replace('Elements14Arena03','Elements14Arena04')
s=s.replace("('caps',['--headless','res://ElementsCaps.tscn'","('caps',['--headless','--verbose','res://ElementsCaps.tscn'")
p=HERE/'run_elements_arena04.py';assert not p.exists();p.write_text(s,encoding='utf-8');print(str(p))
