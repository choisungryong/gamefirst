"""Bounded migration identity/transaction tests; no D2R installation access."""
import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'tools' / 'convert_legacy_profile.py'
spec = importlib.util.spec_from_file_location('phase1_converter', TOOL)
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)


class ConverterChecks(unittest.TestCase):
    def test_conversion_is_deterministic_and_does_not_modify_research_profile(self):
        profile = json.loads((ROOT / 'evidence-profile.json').read_text())
        before = copy.deepcopy(profile)
        first = converter.convert(profile)
        self.assertEqual(first, converter.convert(profile))
        self.assertEqual(before, profile)
        self.assertEqual(first['skills'][0]['cost']['raw'], 640)
        self.assertEqual(first['enemies'][0]['max_health_raw'], 2304)
        self.assertEqual(first['provenance']['status'], 'design_choice')

    def test_different_table_bytes_cannot_inherit_old_build_or_overwrite_outputs(self):
        fixture = (ROOT / 'evidence' / 'phase5' / 'verification' / 'converter-negative-fixture').resolve()
        self.assertTrue(fixture.is_relative_to((ROOT / 'evidence' / 'phase5' / 'verification').resolve()))
        fixture.mkdir(parents=True, exist_ok=True)
        (fixture / 'skills.txt').write_text('unrecognized source bytes', encoding='utf-8')
        output = fixture / 'catalog-sentinel.json'
        research = fixture / 'claims-sentinel.json'
        output.write_text('preserve-catalog', encoding='utf-8')
        research.write_text('preserve-claims', encoding='utf-8')
        current_catalog = (ROOT / 'game_data' / 'catalog.json').read_bytes()
        run = subprocess.run([sys.executable, str(TOOL), '--tables', str(fixture),
                              '--output', str(output), '--research-output', str(research)],
                             text=True, capture_output=True, timeout=10)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('Unsupported research source identity', run.stderr)
        self.assertEqual(output.read_text(), 'preserve-catalog')
        self.assertEqual(research.read_text(), 'preserve-claims')
        self.assertEqual((ROOT / 'game_data' / 'catalog.json').read_bytes(), current_catalog)


if __name__ == '__main__':
    unittest.main()
