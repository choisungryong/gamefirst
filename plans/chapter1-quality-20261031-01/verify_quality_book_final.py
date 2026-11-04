"""Run the preserved static QA against the finalized draft using a fresh output."""
from pathlib import Path
source=Path(__file__).with_name('verify_quality_book.py').read_text(encoding='utf-8')
assert source.count('STATIC-QA-01.json')==1
source=source.replace('STATIC-QA-01.json','STATIC-QA-02.json')
exec(compile(source,__file__,'exec'))
