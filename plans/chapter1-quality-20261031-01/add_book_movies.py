from pathlib import Path
import json, hashlib, shutil
ROOT=Path(__file__).resolve().parents[2]
PROOF=Path(__file__).resolve().parent
DIST=PROOF/'book-v03/dist'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def writej(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    draft=PROOF/'book-v03/drafts/before-movies-01'
    assert not draft.exists()
    draft.mkdir(parents=True)
    for p in [DIST/'validation.html',ROOT/'HANDOFF.md',PROOF/'STATUS.ko.md']:shutil.copy2(p,draft/p.name)
    moviebase=PROOF/'package03/movies'
    records=[]
    for kind,folder,key,target in [('new','new-20261101-01','mp4','new-720p30-offline.mp4'),('old','old-20261101-01','mp4','old-720p30-offline.mp4'),('comparison','comparison-20261101-01','comparison','candidate02-vs03-20s-60s-offline.mp4')]:
        mp=moviebase/folder/('comparison-manifest.json' if kind=='comparison' else 'movie-manifest.json')
        m=json.loads(mp.read_text(encoding='utf-8'));src=Path(m[key]['path'])
        assert sha(src)==m[key]['sha256']
        dest=DIST/'movies'/target;assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
        assert sha(dest)==m[key]['sha256']
        shutil.copy2(mp,DIST/'movies'/(kind+'-manifest.json'))
        records.append({'kind':kind,'source':str(src),'copy':'movies/'+target,'sha256':sha(dest),'bytes':dest.stat().st_size})
    comp=moviebase/'comparison-20261101-01'
    for filename in ['new-frame-020.png','new-frame-040.png','new-frame-060.png','new-frame-075.png','old-frame-020.png','old-frame-040.png','old-frame-060.png','old-frame-075.png','terminal-state-comparison.json']:shutil.copy2(comp/filename,DIST/'movies'/filename)
    p=DIST/'validation.html';text=p.read_text(encoding='utf-8')
    old='<div id="movie-links"><p class="note">영상 인코딩·비교 파일은 제작 중이며, 실제 파일 검증 후 이 영역에 추가합니다.</p></div>'
    new='''<div id="movie-links"><h3>같은20–60초, 이전 후보와 품질03</h3><video controls preload="none" src="movies/candidate02-vs03-20s-60s-offline.mp4">비교 영상을 재생할 수 없습니다.</video><p class="subtle">40초/2560×768/30FPS. 왼쪽 후보02, 오른쪽 품질03. 소리는 후보03만 사용하며 영상 상단에 표시했습니다. 오프라인 렌더입니다.</p><h3>품질03 전체90초</h3><video controls preload="none" poster="movies/new-frame-040.png" src="movies/new-720p30-offline.mp4">새 후보 영상을 재생할 수 없습니다.</video><p class="subtle">1280×720/고정30FPS. 실제 전투78.15초/813처치 승리.2700frame 강제 종료의 ObjectDB/9resource 경고는 원시에 남겼습니다.</p><details><summary>이전 후보02 전체90초</summary><video controls preload="none" poster="movies/old-frame-040.png" src="movies/old-720p30-offline.mp4"></video><p class="subtle">이전 후보도 같은78.15초/813처치/Lv12/HP7210raw 결과입니다. 종료 방식은 앱90초 정상 종료+3000frame guard로 정리했으며 경고가 없었습니다.</p></details><p><a href="movies/new-manifest.json">새 영상·해시</a> · <a href="movies/old-manifest.json">이전 영상·해시</a> · <a href="movies/comparison-manifest.json">비교 편집·해시</a> · <a href="movies/terminal-state-comparison.json">종료 상태 비교</a></p></div>'''
    assert old in text;text=text.replace(old,new)
    p.write_text(text,encoding='utf-8')
    status=PROOF/'STATUS.ko.md';text=status.read_text(encoding='utf-8')
    text+='''\n## 영상 완료 후속 기록\n\n[같은20–60초 전후 비교40초](book-v03/dist/movies/candidate02-vs03-20s-60s-offline.mp4), [품질03 전체90초](book-v03/dist/movies/new-720p30-offline.mp4), [이전 후보02 전체90초](book-v03/dist/movies/old-720p30-offline.mp4)를 도감에 연결했다. MP4는 도감 내부에 동일 해시 사본으로 보존했다. 원시 AVI/명령/로그/ffprobe는 package03/movies에 남는다.\n\n전후 두 일반 드라이버의 실제 종료 상태는78.15초/813처치/Lv12/HP7210raw/화염진화4·냉기3·번개3으로 같다. 비교 영상은20–60초40초를2560×768/고정30FPS로 나란히 배치하고 소리는 후보03만 사용했다고 상단에 표시한다. 새 영상 강제 종료 경고와 이전 영상 앱 종료의 경고 없음은 별도 기록하며 누수0으로 일반화하지 않는다. ffprobe/MP4 길이·오디오 스트림 확인은 실제 청취나 수동 플레이의 근거가 아니다.\n'''
    status.write_text(text,encoding='utf-8')
    handoff=ROOT/'HANDOFF.md';text=handoff.read_bytes()
    old='연속 영상은 `package03/movies/`에서 제작 중이다.'.encode('utf-8')
    new='연속 영상은 `package03/movies/`에서 완료했다. 새/이전90초와20–60초 전후 비교40초 MP4를 새 도감 내부 movies/에 해시 일치 사본으로 연결했다. 두 후보의 종료 상태78.15초/813처치/Lv12/HP7210raw와 기술 랭크가 같다. 비교 음향은 후보03만 사용했다고 영상 상단에 표시했다.'.encode('utf-8')
    assert text.count(old)==1;text=text.replace(old,new,1);handoff.write_bytes(text)
    original=Path('C:/Project/game-research/implementation-backups/chapter1-quality03-docs-before-20261101-01/HANDOFF.md').read_bytes()
    assert text.endswith(original)
    writej(PROOF/'book-v03/MOVIE-COPIES.json',{'files':records,'scope':'Local MP4 copies match source manifests. Offline rendering, not manual play or performance.'})
    print(json.dumps({'movie_copies':len(records),'video_players':3,'handoff_exact_suffix':True}))
if __name__=='__main__':main()
