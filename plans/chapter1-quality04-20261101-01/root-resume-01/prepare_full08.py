from pathlib import Path
ROOT=Path('C:/Project/d2r-combat-baseline');old=ROOT/'plans/chapter1-quality04-20261101-01/full07';dest=old.with_name('full08')
assert not dest.exists();dest.mkdir()
s=(old/'package_full07.py').read_text(encoding='utf-8').replace('candidate07','candidate08').replace('20261101-07','20261101-08').replace('Quality07','Quality08')
s=s.replace("'chapter1/view/chapter_ground.gdshader']","'chapter1/view/chapter_ground.gdshader', 'chapter1/view/chapter_actors.gd']")
s=s.replace('len(set(result))==82','len(set(result))==83')
s=s.replace("[exe,'--headless','--','--chapter1-profile-off'","[exe,'--headless','--fixed-fps','60','--','--chapter1-profile-off'")
s=s.replace("'--chapter1-quit-after=2'],60)","'--chapter1-quit-after=30'],60)")
needle="write(PROOF/'imported-resource-proof.json',{'audio':audio,'ready':ready,'scope':'Headless load only; not GPU/visual/audio approval'})"
assert s.count(needle)==1
extra='''
    results=[json.loads(line.split('FULL_CHAPTER_RUNTIME_RESULT ',1)[1]) for line in smoke['stdout'].splitlines() if 'FULL_CHAPTER_RUNTIME_RESULT ' in line]
    assert results and results[-1]['tick']>1200 and results[-1]['growth']['level']>=2 and results[-1]['equipped'],'Release normal policy must progress and equip past the first choice'
    write(PROOF/'release-policy-smoke.json',{'result':results[-1],'scope':'30simsec fixed-fps/headless normal driver, not actual GPU/manual/performance'})
    execute('release-behavior-probe',[exe,'--headless','--script',ROOT/'plans/chapter1-quality04-20261101-01/root-resume-01/release_behavior_probe.gd'],60)
'''
s=s.replace(needle,needle+'\n'+extra)
(dest/'package_full08.py').write_text(s,encoding='utf-8')
(dest/'RUN.ko.md').write_text((old/'RUN.ko.md').read_text(encoding='utf-8').replace('후보07','후보08')+'\n후보08은 릴리스 선택/장비 호출 누락을 수정하고, 작은 영웅 표식과 초반12마리/완만한 첫10초를 적용했습니다.\n',encoding='utf-8')
s=(old/'run_runtime.py').read_text(encoding='utf-8');(dest/'run_runtime.py').write_text(s,encoding='utf-8')
print(str(dest))
