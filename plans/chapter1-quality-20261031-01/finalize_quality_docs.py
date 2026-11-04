from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, shutil
ROOT=Path(__file__).resolve().parents[2]
PROOF=Path(__file__).resolve().parent
BOOK=PROOF/'book-v03'
DIST=BOOK/'dist'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def writej(p,data):
    assert not p.exists(),str(p)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    draft=BOOK/'drafts/before-browser-final-01';assert not draft.exists();draft.mkdir()
    for p in [ROOT/'HANDOFF.md',PROOF/'STATUS.ko.md',DIST/'validation.html']:shutil.copy2(p,draft/p.name)
    images={p.name:{'sha256':sha(p),'bytes':p.stat().st_size} for p in (BOOK/'browser-qa').glob('*.png')}
    assert set(images)=={'desktop-comparison.png','narrow-cover.png'}
    report='''# 도감 v03 root 브라우저 확인

2026-11-01, Asia/Seoul. **root가 IAB에서 직접 조작했고 이 보고서 작성자는 root의 전달과 저장된2PNG를 읽어 정리했다.** 기존 v02 전체 또는 새 v03의 모든 화면·모바일·인쇄·실청취를 검수했다는 뜻은 아니다.

- 기본 좁은443×882 viewport의 표지: 내용 scrollWidth428px, 수평 넘침 없이 표지/전후 비교가 들어왔다. 별도 모바일 전체 페이지 검수는 아니다.
-1440×900 desktop: scrollWidth1425px, 수평 넘침 없음. 표지 전후 비교 slider를 키보드로50→51로 바꾸고 실제 DOM 값을 확인했다.
- 환경 페이지의5개 실제 이미지가 모두 naturalWidth>0으로 로드됐고, 카드/JSON 링크가 보였다. 동작 페이지의 이미지와 효과 페이지의 이미지도 로드되고 수평 넘침이 없었다.
-8개 내비게이션 페이지를 방문해 제목을 확인했다. 장비 표의 실제4개 이름과 효과를 검토했다.
- 비교 영상의 native control에 Space 입력을 보냈다. paused:false,duration40,width2560,height768,error:null,readyState4를 확인했고 currentTime20.194→37.223 진행과 실제 비교 프레임을 봤다. 이는 일부 재생 표본이며 전체40초 프레임별 검수나 음향 청취가 아니다.
- 음향 페이지의20개 audio control을 확인했다. 첫 fire_0에 Space를 보내 duration0.42,paused:false,readyState1,error:null 상태를 확인했다. 실제 청취·모든20개 재생·믹스 승인을 뜻하지 않는다.90초 영상 두 개의 native player는 재생하지 않았다.

`browser-qa/desktop-comparison.png`와 `narrow-cover.png`는 root가 새 경로에 저장한 CUA 캡처다. SHA256/크기는 `BROWSER-QA.json`을 따른다. 작성자는 두 이미지를 읽고 실제 화면이 도감의 비교/좁은 표지임을 확인했다. 해당 스크린샷은 모든 DOM 상태를 담는 전체 녹화가 아니다.

별도의 `STATIC-QA-02.json`은8HTML/로컬 참조 누락0/20audio/복사 해시와 이전v02의104파일 불변, `HTTP-QA-01.json`은69개 로컬 리소스의 HEAD200/동일Content-Length를 확인했다. favicon.ico의 브라우저 자동 요청404는 도감에서 참조한 리소스 누락과 구분한다. 영상 요청 중 클라이언트 연결 중단 로그도 있었으며 브라우저의 확인된 재생 상태와 구분한다. 전체 서버 session 로그는 도구 출력에서 잘렸으므로 완전한 파일 로그로 주장하지 않는다.

root는 소유한 IAB 탭을 닫고 viewport를 복원했다. 임시 서버는 관리 세션93943에 Ctrl+C를 보내 의도적으로 종료(actual exit1)했으며 후속127.0.0.1:8768 접속은 URLError로 실패해 중지를 확인했다. 브라우저 테스트 동안 제품 원본/실행 파일은 수정하지 않았다.
'''
    (BOOK/'BROWSER-QA.ko.md').write_text(report,encoding='utf-8')
    writej(BOOK/'BROWSER-QA.json',{'source':'Root actual IAB actions reported through collaboration plus two independently inspected screenshots','images':images,'pages_visited':8,'narrow_cover_viewport':[443,882],'narrow_scroll_width':428,'desktop_viewport':[1440,900],'desktop_scroll_width':1425,'slider_keyboard':[50,51],'comparison_player':{'duration':40,'width':2560,'height':768,'ready_state':4,'paused':False,'error':None,'current_time_samples':[20.194,37.223]},'audio_controls':20,'first_fire_player':{'duration':0.42,'paused':False,'ready_state':1,'error':None},'limits':['Partial comparison replay only','No actual audio hearing','No playback of two90sec players','Narrow cover only, not full mobile','No full print verification'],'temporary_tab_closed':True,'viewport_restored':True})
    writej(BOOK/'HTTP-STOP.json',{'managed_exec_session':93943,'stop':'Ctrl+C after root closed owned IAB tab','actual_exit':1,'expected_interruption':True,'followup_http':'URLError, server no longer accepts127.0.0.1:8768','full_session_log_persisted':False,'tool_output_was_truncated':True,'resource_HEAD_QA':'HTTP-QA-01.json has69status200/exactbytes','observed_log_notes':['Automatic favicon.ico404','Client abort while video requests were cancelled'],'scope':'Owned local read-only preview stopped; no process-wide kill or user app closure.'})
    p=PROOF/'STATUS.ko.md';text=p.read_text(encoding='utf-8')
    old='정적 검사8HTML/로컬 참조 누락0/20audio/복사 해시 일치다. 실제 브라우저 화면·모바일·재생·인쇄 검수 완료를 주장하지 않는다.'
    new='정적 검사8HTML/로컬 참조 누락0/20audio/복사 해시 일치, 로컬HTTP69리소스200/동일크기를 확인했다. [root 브라우저 확인](book-v03/BROWSER-QA.ko.md)은1440×900표지·slider키50→51/8페이지제목·환경/동작/효과 이미지·실제 장비 표·비교 영상 일부 재생(20.194→37.223초)/첫 fire 재생 요청을 포함한다. 좁은443×882는 표지만 확인했다. 두90초 player·모든20음향·전체모바일·인쇄·실청취 승인은 아니다. 소유 IAB 탭을 닫고 viewport를 복원했으며 임시 루프백 서버를 중지했다.'
    assert old in text;text=text.replace(old,new);p.write_text(text,encoding='utf-8')
    p=ROOT/'HANDOFF.md';text=p.read_bytes()
    old='현재는 작성 직후이며 실제 브라우저 시각 검수는 별도 후속이다.'.encode('utf-8')
    new='root는1440×900표지·slider키50→51·8페이지제목·환경/동작/효과이미지·실제장비표·비교영상일부재생과첫fire재생요청을 확인했다. 좁은443×882는표지만,90초player2개/모든20음향/전체모바일/인쇄/실청취는미검수다. `book-v03/BROWSER-QA.ko.md`와2PNG를 따른다. 소유탭/viewport를 정리하고 임시서버를 중지했다.'.encode('utf-8')
    assert text.count(old)==1;text=text.replace(old,new,1);p.write_bytes(text)
    original=Path('C:/Project/game-research/implementation-backups/chapter1-quality03-docs-before-20261101-01/HANDOFF.md').read_bytes();assert text.endswith(original)
    p=DIST/'validation.html';text=p.read_text(encoding='utf-8')
    marker='<h2>근거 문서</h2>'
    addition='<h2>도감 브라우저 확인</h2><p>root가8개 페이지 제목과 데스크톱 표지/키보드 비교 slider, 환경·동작·효과 이미지와 장비 표를 확인했습니다. 비교 영상 일부 재생(20.194→37.223초)과 첫 fire 재생 요청을 확인했습니다. 좁은443×882는 표지만 확인했고90초 영상·모든20음향·전체 모바일/인쇄·실청취 승인은 아닙니다. <a href="../BROWSER-QA.ko.md">브라우저 검수 범위</a>를 따릅니다.</p>'
    assert text.count(marker)==1;text=text.replace(marker,addition+marker);p.write_text(text,encoding='utf-8')
    source=(PROOF/'verify_quality_book.py').read_text(encoding='utf-8').replace('STATIC-QA-01.json','STATIC-QA-03.json')
    namespace={'__file__':str(PROOF/'verify_quality_book.py'),'__name__':'__main__'}
    exec(compile(source,str(PROOF/'verify_quality_book.py'),'exec'),namespace)
    freeze=json.loads((PROOF/'package03/FINAL-SOURCE-FREEZE.json').read_text(encoding='utf-8'))
    bad=[x for x,h in freeze.items() if sha(ROOT/x)!=h];assert not bad,bad
    prior=json.loads(Path('C:/Project/game-research/implementation-backups/chapter1-quality03-docs-before-20261101-01/manifest.json').read_text(encoding='utf-8'))
    old_bad=[x for x,h in prior['old_book_v02'].items() if sha(ROOT/x)!=h];assert not old_bad,old_bad
    files={p.relative_to(DIST).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(DIST.rglob('*')) if p.is_file()}
    writej(BOOK/'BOOK-ARTIFACTS.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'entry':'dist/index.html','role':'Quality03 supplement; links preserved v02 for original39briefs/reference observations, not same-coverage replacement','files':files,'counts':{'html':8,'png':21,'wav':20,'mp4':3,'json':10,'txt':3,'md':2,'css':1,'js':1},'portable_scope':'Art/audio/MP4/native screenshots are internal copies. Historical v02, source reports and executable links require project tree. No standalone ZIP claimed.','browser_QA':'BROWSER-QA.ko.md; root actual scope and explicit limits','quality_approval':False,'full_chapter_complete':False})
    writej(PROOF/'FINAL-DOCS-PRESERVATION.json',{'success':True,'runtime_freeze_files_checked':len(freeze),'runtime_mismatches':bad,'old_v02_files_checked':len(prior['old_book_v02']),'old_v02_mismatches':old_bad,'old_handoff_sha256':hashlib.sha256(original).hexdigest(),'handoff_exact_suffix':True,'current_handoff_sha256':sha(ROOT/'HANDOFF.md'),'status_sha256':sha(PROOF/'STATUS.ko.md'),'book_artifacts_sha256':sha(BOOK/'BOOK-ARTIFACTS.json'),'book_files':len(files),'scope':'Current docs/book and selected runtime/v02 preservation. Not all historical evidence, quality completion, full chapter, hearing, formal performance or leak0.'})
    print(json.dumps({'success':True,'book_files':len(files),'runtime_freeze_mismatches':0,'old_v02_mismatches':0,'handoff_exact_suffix':True,'server_stopped':True}))
if __name__=='__main__':main()
