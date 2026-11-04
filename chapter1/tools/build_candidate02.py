"""New immutable candidate using the preserved candidate01 builder implementation."""
from pathlib import Path
import importlib.util
import sys

sys.dont_write_bytecode=True
source=Path(__file__).with_name('build_candidate.py')
spec=importlib.util.spec_from_file_location('chapter1_preserved_builder',source)
builder=importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
builder.BUILD_ID='chapter1-c2-candidate-20261031-02'
builder.STAGE=Path('C:/Project/game-research/build-staging')/builder.BUILD_ID
builder.OUTPUT=builder.ROOT/'builds/chapter1'/builder.BUILD_ID
builder.PROOF=builder.ROOT/'plans/chapter1-c2-20261031-01/package-candidate02'

if __name__=='__main__':builder.main()
