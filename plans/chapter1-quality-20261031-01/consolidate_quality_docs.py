from pathlib import Path
import json, shutil, hashlib
ROOT=Path(__file__).resolve().parents[2]
PROOF=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    backup=PROOF/'book-v03/drafts/before-consolidation-01';assert not backup.exists();backup.mkdir()
    for p in [PROOF/'STATUS.ko.md',ROOT/'HANDOFF.md',PROOF/'book-v03/dist/validation.html']:shutil.copy2(p,backup/p.name)
    p=PROOF/'STATUS.ko.md';text=p.read_text(encoding='utf-8')
    prefix=text.split('새90초720p/고정30FPS')[0]
    tail='## 도감과 보존'+text.split('## 도감과 보존',1)[1].split('## 영상 완료 후속 기록',1)[0]
    middle='''[root 직접 조작 관찰](native-runtime-03/native-20261101-01/OBSERVATIONS.ko.md)은1440×810 메뉴/성장/정지복원·Space 회피대기·장비 비교/장착무회복·Mtoast·실제17.85초/80처치/Lv5/HP0/154 패배·R초기화120/120·창X 종료actual0/stderr0bytes다.20PNG와 실행/해시 원시를 보존했다. 수동 진화·세기술·정예 승리·OS WASD hold·긴좌클릭 이동·실청취는 확정하지 않았다. 관찰용으로 주로 정지한 수동 실행의 조기 패배를 승률이나 난이도로 일반화하지 않는다. 영웅 주변 적 겹침과 잦은 초반 성장 화면의 흐름은 개선 대상으로 남았다. 자동 모드 PNG가 모든 장착 직후를 찍지는 않으며 일부 즉시 변화는 root의 당시 CUA 관찰에 근거한다.

[품질03 전체90초](book-v03/dist/movies/new-720p30-offline.mp4)와 [이전 후보02 전체90초](book-v03/dist/movies/old-720p30-offline.mp4)는720p/고정30FPS 오프라인 렌더다. 두 후보의 기존 정상 입력/선택/장착 드라이버는78.15초/813처치/Lv12/화염진화4·냉기3·번개3/HP7210raw로 같은 승리 결과를 냈다. [같은20–60초 전후 비교40초](book-v03/dist/movies/candidate02-vs03-20s-60s-offline.mp4)는2560×768로 나란히 배치하고 소리는 후보03만 사용했다고 영상 상단에 표시한다. MP4는 도감 내부에 동일 해시 사본으로 보존하며 원시 AVI/명령/로그/ffprobe는 package03/movies에 남는다. 새 영상의2700frame 강제 종료 ObjectDB/9resource 경고와 이전 영상의 앱90초 정상 종료+3000frame guard/경고 없음은 구분한다. **고정 FPS 영상은 수동 플레이·실제 GPU 성능·실청취·누수0 증거가 아니다.**

[성능 진단02](performance-diagnostic-02/README.ko.md)는 동일EXE/실제1920×1080/Forward+/VSync해제·delta smoothing해제·max-fps120/normal pilot70초를 기록했다. actual0/stderr0,elapsed70/8344표본(<15000)/engine delta p958.333ms/698처치/Lv12/maxalive59/peakprojectile28이다. root의 실제 초점 확인은32초 한 시점이며 전체 프레임 초점 기록은 아니다.120FPS pacing과 엔진 delta, 단일 실행, 첫10초 미제외·60초×3 미수행·최대180적 부하 미검증이므로 정식 성능 통과가 아니다. 진단01은 uncapped로15000표본 상한을 채워 초반 일부만 기록했으므로 p951.389ms를 전체70초의 결과나 개선율로 쓰지 않는다. 원시를 보존했다.

'''
    p.write_text(prefix+middle+tail,encoding='utf-8')
    book=PROOF/'book-v03/dist/validation.html';text=book.read_text(encoding='utf-8')
    old='<tr><td>정식 성능·청취</td><td>열림</td><td>짧은 PNG QA p95약20ms나 고정 FPS movie를60FPS 통과로 표시하지 않음.</td></tr>'
    new='<tr><td>성능 진단02</td><td>동일EXE1080p/70초 actual0 ·8344표본</td><td>max-fps120의 엔진delta p958.333ms. 초점32초 한시점·단일실행·준비10초 미제외, 정식 통과 아님.</td></tr><tr><td>정식 성능·청취</td><td>열림</td><td>진단01은15000표본 상한으로 초반만 기록. 해당p951.389ms·짧은 PNG QA·고정FPSmovie를60FPS 통과나 개선율로 쓰지 않음.</td></tr>'
    assert old in text;text=text.replace(old,new)
    text=text.replace('<h2>근거 문서</h2>','<h2>근거 문서</h2><p><a href="../../performance-diagnostic-02/README.ko.md">비정식70초 성능 진단02와 한계</a></p>')
    book.write_text(text,encoding='utf-8')
    h=ROOT/'HANDOFF.md';text=h.read_bytes()
    marker='짧은 QA의 p95약20ms나 movie30FPS를 목표16.67ms 통과로 부르지 않는다.'.encode('utf-8')
    supplement='짧은 QA의 p95약20ms나 movie30FPS를 목표16.67ms 통과로 부르지 않는다. 비정식 성능진단02는1080p/70초/8344표본/engine delta p958.333ms/actual0이나 max-fps120 pacing·단일실행·초점32초 한시점·준비10초 미제외 조건이다. 진단01의 uncapped15000표본 상한 p951.389ms는 초반 일부라 전체70초나 개선율로 쓰지 않는다. 정식 성능은 열려 있다.'.encode('utf-8')
    assert text.count(marker)==1;text=text.replace(marker,supplement,1);h.write_bytes(text)
    original=Path('C:/Project/game-research/implementation-backups/chapter1-quality03-docs-before-20261101-01/HANDOFF.md').read_bytes();assert text.endswith(original)
    print('Consolidated current STATUS; added nonformal performance limits; original HANDOFF exact suffix preserved.')
if __name__=='__main__':main()
