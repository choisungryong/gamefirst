from pathlib import Path
HERE=Path(__file__).parent
s=(HERE/'stage_warden12_fixture02.py').read_text(encoding='utf-8')
s=s.replace("OUT=BASE/'fixture02'","OUT=BASE/'fixture03'").replace('chapter1-warden-research-20261101-02','chapter1-warden-research-20261101-03')
s=s.replace("shutil.copy2(Path(__file__).with_name('warden_fixture12.gd'),STAGE/'warden_fixture.gd')",'''for name in ['chapter1/view/chapter_actors_quality12.gd','chapter1/art/chained_warden/v01/chained_demon_animated.glb','chapter1/art/chained_warden/v01/ATTRIBUTION.ko.md']:
 shutil.copy2(ROOT/name,STAGE/name)
shutil.copy2(Path(__file__).with_name('warden_fixture12.gd'),STAGE/'warden_fixture.gd')''')
s=s.replace("replace('fixture01/captures','fixture02/captures')","replace('fixture01/captures','fixture03/captures')").replace('AshenCloisterWardenResearch12','AshenCloisterWardenResearch12Fixture03')
s=s.replace("('fixture',['res://WardenFixture.tscn'","('check',['--headless','--check-only','--script','res://warden_fixture.gd']),('fixture',['res://WardenFixture.tscn'")
s=s.replace('--chapter1-quit-after=12.3','--chapter1-quit-after=15.3').replace('fixture02/captures','fixture03/captures')
s=s.replace("'explicit int local_tick fixes fixture parse failure'","'separate mask/chain/skin response, darker body and1.15 model scale; paused/frozen pose guard and73bone freeze check'")
target=HERE/'stage_warden12_fixture03.py';assert not target.exists();target.write_text(s,encoding='utf-8');print(str(target))
