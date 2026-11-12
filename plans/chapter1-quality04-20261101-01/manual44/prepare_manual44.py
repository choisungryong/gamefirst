"""Reuse the native-input observer; it never drives or modifies the run."""
from pathlib import Path

here=Path(__file__).resolve().parent
source=(here.parent/'root-resume-01/manual26_observer.gd').read_text(encoding='utf-8')
source=source.replace('MANUAL26','MANUAL44').replace('package26','package44').replace('view._wall_age+5','view._wall_age+12')
marker='\tvar logger := InputLog.new();logger.view=view;root.add_child(logger)'
source=source.replace(marker,'''\tif view._pilot or not view._profile_off:
\t\tpush_error("Manual44 requires actual native input and disabled user persistence");quit(2);return
'''+marker)
with (here/'manual44_observer.gd').open('x',encoding='utf-8') as output:output.write(source)
print('Prepared read-only manual observer; no engine/start/input')
