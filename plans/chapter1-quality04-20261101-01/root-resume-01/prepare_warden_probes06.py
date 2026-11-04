from pathlib import Path
HERE=Path(__file__).parent
s=(HERE/'run_warden_clock04.py').read_text(encoding='utf-8')
s=s.replace("OUT=BASE/'clock04'","OUT=BASE/'visibility06'").replace('chapter1-warden-clock-20261101-04','chapter1-warden-visibility-20261101-06')
s=s.replace('warden_clock_probe12.gd','warden_visibility_probe13.gd').replace('clock_probe.gd','visibility_probe.gd').replace('ClockProbe','VisibilityProbe')
s=s.replace('WardenResearch12Clock04','WardenResearch13Visibility06').replace('boss-research12/clock04','boss-research12/visibility06')
s=s.replace('Isolated actual-core/renderer recovery freeze probe','Current posed-capsule coverage and stopped-core death probe')
target=HERE/'run_warden_visibility06.py';assert not target.exists();target.write_text(s,encoding='utf-8');print(str(target))
s=(HERE/'run_warden_clock04.py').read_text(encoding='utf-8')
s=s.replace("OUT=BASE/'clock04'","OUT=BASE/'clock07'").replace('chapter1-warden-clock-20261101-04','chapter1-warden-clock-20261101-07')
s=s.replace('WardenResearch12Clock04','WardenResearch13Clock07').replace('boss-research12/clock04','boss-research12/clock07')
# The copied probe writes its fixed res:// output name, so adapt its staged text.
s=s.replace("shutil.copy2(Path(__file__).with_name('warden_clock_probe12.gd'),STAGE/'clock_probe.gd')","(STAGE/'clock_probe.gd').write_text(Path(__file__).with_name('warden_clock_probe12.gd').read_text(encoding='utf-8').replace('boss-research12/clock04','boss-research12/clock07'),encoding='utf-8')")
target=HERE/'run_warden_clock07.py';assert not target.exists();target.write_text(s,encoding='utf-8');print(str(target))
