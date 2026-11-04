from pathlib import Path
import shutil
HERE=Path(__file__).parent;ROOT=Path('C:/Project/d2r-combat-baseline');OUT=ROOT/'plans/chapter1-quality04-20261101-01/full14/profile-process01'
p=HERE/'profile_process14.gd';shutil.copy2(p,OUT/'probe-before-reserved-name-fix.gd')
s=p.read_text(encoding='utf-8').replace('var namespace :=','var qa_user_dir :=').replace('namespace.ends_with','qa_user_dir.ends_with').replace('"namespace":namespace','"namespace":qa_user_dir').replace('ProcessQA20261101A','ProcessQA20261101B');p.write_text(s,encoding='utf-8')
s=(HERE/'run_profile_process14.py').read_text(encoding='utf-8').replace('profile-process01','profile-process02').replace('chapter1-profile-process-20261101-01','chapter1-profile-process-20261101-02').replace('ProcessQA20261101A','ProcessQA20261101B')
p=HERE/'run_profile_process14_02.py';assert not p.exists();p.write_text(s,encoding='utf-8')
(OUT/'FAILURE.ko.md').write_text('QA프로브가예약어namespace를지역변수로써서ParseError였다. 제품core는변경하지않았다. 원시실행/수정전프로브/stage/QA사용자폴더A를보존하고qa_user_dir로고친새stage/사용자폴더B에서02검수한다. 원래사용자저장미접근.\n',encoding='utf-8')
