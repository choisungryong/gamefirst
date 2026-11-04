from pathlib import Path
import shutil
ROOT=Path('C:/Project/d2r-combat-baseline');HERE=Path(__file__).parent;OUT=ROOT/'plans/chapter1-quality04-20261101-01/cold16/prototype01'
shutil.copy2(HERE/'prototype_cold16.gd',OUT/'probe-before-id-fix.gd');shutil.copy2(ROOT/'chapter1/core/chapter_run_quality16.gd',OUT/'rule-source.gd')
s=(HERE/'prototype_cold16.gd').read_text(encoding='utf-8').replace('run.enemies.clear();run.events.clear()','run.enemies.clear();run.events.clear();run._enemy_sequence=0')
s=s.replace('var run=fixture();var paid := context(run);run._damage_enemy(1,paid,0)','var run=fixture();check(run.enemies.keys()==[1,2,3,4],"fixture owns expected fresh ids");var paid := context(run);run._damage_enemy(1,paid,0)')
s=s.replace('var pacing: Array=[]','''if not failures.is_empty():
		print("COLD16_FIXTURE_FAILED ",JSON.stringify(failures));quit(1);return
	var pacing: Array=[]''')
anchor='\t\tcheck(game.mode=="victory" and game.tick>=300*60 and game.tick<=480*60,"5–8minute normal pacing "+id_)'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
		if id_!="chapter1.skill.frost":
			var old=Old.new();old.start(90131,id_);var old_pilot=Pilot.new();old_pilot.run=old
			for i in 40000:
				var move: Vector2=old_pilot.decide();old.step(move)
				if old.mode in ["victory","defeat"]:break
			check(old.snapshot()==game.snapshot(),"full unchanged non-cold core "+id_)
''')
s=s.replace('cold16/prototype01/result.json','cold16/prototype02/result.json')
p=HERE/'prototype_cold16_02.gd';assert not p.exists();p.write_text(s,encoding='utf-8')
s=(HERE/'run_prototype_cold16.py').read_text(encoding='utf-8').replace('cold16/prototype01','cold16/prototype02').replace("with_name('prototype_cold16.gd')","with_name('prototype_cold16_02.gd')");p=HERE/'run_prototype_cold16_02.py';assert not p.exists();p.write_text(s,encoding='utf-8')
(OUT/'FIXTURE-FAILURE.ko.md').write_text('첫probe는start가만든12개초기적의enemy_sequence를초기화하지않고새배치4개를추가했으나ID1~4를가정해잘못된표적을검사했다. 원시실패/프로브/rule소스/정상pacing데이터를보존하고02는배치ID를0부터다시만든뒤직접검증한다. 제품규칙16은이수정으로바꾸지않는다. 첫pacing의냉기397.7초/shatter840은관찰값이며직접규칙검사가실패한상태를완료로쓰지않는다.\n',encoding='utf-8')
print(str(p))
