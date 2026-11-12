"""Add an isolated cache exercise oracle, preserving all earlier fixtures."""
from pathlib import Path

stage = Path('C:/Project/game-research/build-staging/actor42-refactor-exact02')
files = {
 'count42.gd': '''extends "res://chapter1/view/chapter_actors_quality42.gd"
var calls42 := 0
var hits42 := 0
func _overlaps_hero(actor: Node3D,camera: Camera3D) -> bool:
 calls42+=1
 if _overlap42_active and _overlap42_ready:hits42+=1
 return super._overlaps_hero(actor,camera)
''',
 'viewcache42.gd': '''extends "res://chapter1/chapter_one_input21.gd"
func _init():
 super._init()
 actors=preload("res://count42.gd").new()
'''
}
fixture = (stage/'extended.gd').read_text(encoding='utf-8')
fixture = fixture.replace('res://view42b.gd','res://viewcache42.gd')
fixture = fixture.replace(' print("FULL_EXTENDED_PASS', ''' var candidate=views[1].actors
 assert(candidate.calls42>0 and candidate.hits42>0,"Cache must actually be exercised")
 assert(not candidate._overlap42_active and not candidate._overlap42_ready,"Cache must not escape sync")
 candidate.reset()
 assert(not candidate._overlap42_active and not candidate._overlap42_ready,"Reset must clear cache")
 print("CACHE_PASS calls=",candidate.calls42," hits=",candidate.hits42)
 print("FULL_EXTENDED_PASS''')
files['cache.gd'] = fixture
for name, text in files.items():
    with (stage/name).open('x', encoding='utf-8') as output:
        output.write(text)
print('Prepared isolated cache fixture')
