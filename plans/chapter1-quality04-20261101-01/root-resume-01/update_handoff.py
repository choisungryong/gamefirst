from pathlib import Path
import hashlib,json
ROOT=Path('C:/Project/d2r-combat-baseline');OUT=Path(__file__).resolve().parent
path=ROOT/'HANDOFF.md';old=path.read_bytes()
expected=Path('C:/Project/game-research/implementation-backups/chapter1-quality04-root-resume-before-20261101-01/source/HANDOFF.md').read_bytes()
assert old==expected,'Do not overwrite a later handoff'
prefix='''# 2026-11-01 최신 진행 — 목표 active · 품질04 구현/검증 · 실제 리깅 아트 검토

사용자 지시대로 SACRATA 지향 군중 전투/타격과 디아블로식 장비·기술 성장의5–8분짜리1장 전체를 목표로 계속 진행 중이다. 목표는 active이며, 대표90초·기술검사·새 후보를 전체 완료로 표시하지 않는다.

먼저 `plans/chapter1-quality04-20261101-01/WIP-HANDOFF.ko.md`와 root-resume-01/ 증거를 읽는다. 현재 실행 후보06은 `builds/chapter1/chapter1-c2-candidate-20261101-06/AshenCloister-Chapter1.exe`(SHA dd59675a89e88b8a02cc8b3e0539f5129d68d6afe2d14c4390c73bb0ac101fbe)이며 이전03/04/05를 보존했다. 실제 군중 간격·영웅 outline·동작 보간·명중 accent·음향 gain과 공격 중 재배치 결함을 수정했다. 후보04 GPU90초는82.5667초/867처치 승리였으나 SACRATA 품질 승인은 아니다.

성능06의 실제70초 raw는 내부렌더2304×1296/윈도1920×1080 때문에 엄격한1080조건과 불일치하여 무효로 보존했다. p952.827ms를 정식3회 통과로 표시하지 않는다. AI8보행 시도03도 발 교대 미달로 거절했다. 공개 Flare HD와 thecubber의 OGA rigged mage는 라이선스/품질 검토 후보이며 런타임 미채택이다. 모델 변환 도구는 공식 portable Blender4.5.15를 체크섬 검증하여 준비 중이다.

보조 agents의 사용량 제한으로 root가 직접 이어가고 있다. 새 agents 반복 생성은 피한다. 옛 테스트는 출력 경로를 확인하지 않고 재실행하지 말고, headless editor import는 외부 최소 staging에서만 한다. 기존 변경·실패·증거·프로필을 보존하며 커밋/업로드/구매/보호되는 원작자산 복사를 하지 않는다. 아래 이전 HANDOFF 바이트는 그대로 남는다.

---

'''
new=prefix.encode('utf-8')+old
path.write_bytes(new)
assert path.read_bytes().endswith(old)
with (OUT/'HANDOFF-PRESERVATION.json').open('x',encoding='utf-8') as f:
    json.dump({'old_sha256':hashlib.sha256(old).hexdigest(),'new_sha256':hashlib.sha256(new).hexdigest(),'exact_old_suffix':True,'old_backup':'C:/Project/game-research/implementation-backups/chapter1-quality04-root-resume-before-20261101-01/source/HANDOFF.md'},f,indent=2)
