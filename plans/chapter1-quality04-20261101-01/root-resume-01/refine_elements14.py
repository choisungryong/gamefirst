from pathlib import Path
import shutil,json
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01/elements14';BACK=BASE/'before-refinement02';assert not BACK.exists();BACK.mkdir()
for name in ['chapter_elements_quality14.gd','comet_quality14.gdshader','impact_quality14.gdshader','arc_quality14.gdshader']:shutil.copy2(ROOT/'chapter1/view'/name,BACK/name)
p=ROOT/'chapter1/view/chapter_elements_quality14.gd';s=p.read_text(encoding='utf-8')
s=s.replace('ice.albedo_color=Color(.72,.94,1,.85)','ice.albedo_color=Color(.84,.98,1,.70)')
s=s.replace('ice.emission_energy_multiplier=.55','ice.emission_energy_multiplier=.70')
s=s.replace('func consume(events: Array) -> void:\n\tvar shard_budget := 8','func consume(events: Array) -> void:\n\tvar old_contact_count := contacts.size()\n\tvar shard_budget := 8')
s=s.replace('\tsuper.consume(events)\n\t# Replace','''	super.consume(events)
	# Frost/arc already carry a white release/impact center. Keep a few smaller
	# contact accents so dense chains do not become a screen-covering star pile.
	var contact_keep: Array[Dictionary]=[];var cold_budget := 3
	for i in contacts.size():
		if i>=old_contact_count and float(contacts[i].element)>=.3:
			if cold_budget<=0:continue
			cold_budget-=1
		contact_keep.append(contacts[i])
	contacts=contact_keep
	# Replace''')
s=s.replace('\tsuper.sync(run,delta)\n\t_sync_arcs','''	super.sync(run,delta)
	for i in contacts.size():
		if float(contacts[i].element)<.3:continue
		var transform := contact_batch.multimesh.get_instance_transform(i)
		transform.basis=transform.basis.scaled(Vector3.ONE*(.68 if float(contacts[i].element)<.8 else .55))
		contact_batch.multimesh.set_instance_transform(i,transform)
	_sync_arcs''')
s=s.replace('Color(.40,.78,1,strength*.72)','Color(.72,.92,1,strength*.60)')
s=s.replace('var normal: Vector3=(triangle[1]-triangle[0]).cross(triangle[2]-triangle[0]).normalized()','var normal: Vector3=(triangle[1]-triangle[0]).cross(triangle[2]-triangle[0]).normalized()\n\t\t\tif normal.dot(Vector3((a+b).x,0,(a+b).z))<0:normal=-normal')
p.write_text(s,encoding='utf-8')
(BASE/'arena02/VISUAL-REVIEW.ko.md').write_text('실제 core 이벤트 배치에서 빙결184/파쇄19/최대동시빙결11/번개cast5가 발생했다. 초기 효과는 낮은 파란 얼음 면이 짙고 흰contact가 겹쳐 중앙이 뭉개졌다. 실제 결과는 비교 JSON과 raw에 보존하고, 반투명 명도·외향 normal·원소별contact최대3/크기축소를 다음03에서 검수한다. 게임 수치/원작 자산 변경은 없다.\n',encoding='utf-8')
print(str(BACK))
