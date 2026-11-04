"""Read-only asset/source attribution snapshot for the expedition presentation."""
from pathlib import Path
import hashlib
import json
import wave

root = Path(__file__).resolve().parents[1]
destination = root / 'evidence/phase7/presentation-resume-20261030-02/ASSET-LEDGER.json'
if destination.exists():
    raise RuntimeError('Preserve prior asset ledger')
records = []
groups = [
    ('assets/actors/Mage*', 'KayKit Adventurers', 'assets/licenses/adventurers-LICENSE.txt'),
    ('assets/actors/Skeleton_Minion*', 'KayKit Skeletons', 'assets/licenses/skeletons-LICENSE.txt'),
    ('assets/environment/*.glb', 'KayKit Dungeon', 'assets/licenses/dungeon-LICENSE.txt'),
    ('assets/expedition/audio/*.wav', 'Original project synthesis; no external samples', 'CC0-1.0 project dedication'),
]
for pattern, source, license_name in groups:
    for path in sorted(root.glob(pattern)):
        if path.suffix == '.import':
            continue
        row = {'path': path.relative_to(root).as_posix(),
               'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
               'source': source, 'license': license_name,
               'usage': 'expedition runtime'}
        if path.suffix == '.wav':
            with wave.open(str(path), 'rb') as stream:
                row['wav'] = {'sample_rate': stream.getframerate(), 'channels': stream.getnchannels(),
                              'sample_width': stream.getsampwidth(), 'frames': stream.getnframes()}
        records.append(row)
for relative in ['presentation/expedition_world.gd', 'presentation/expedition_hud.gd',
                 'presentation/expedition_effects.gd', 'presentation/expedition_loot.gd',
                 'presentation/expedition_audio.gd', 'tools/generate_phase7_audio.py',
                 'tools/generate_phase7_ambience.py']:
    path = root / relative
    records.append({'path': relative, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                    'source': 'Original project code/procedural geometry', 'usage': 'expedition presentation or source generator'})
destination.write_text(json.dumps({'scope': 'Attribution and actual current hashes; final art quality not approved',
    'research_assets': 'Original Diablo atlas preserved in repository; not referenced by Expedition view/presenters. Full-project export packaging must separately exclude research-only assets.',
    'fonts': 'Godot theme font with operating-system CJK fallback; no Windows font copied or redistributed',
    'limitations': 'KayKit characters remain proxy art. Original WAVs are synthetic cues and ambience, not a produced reference soundtrack.',
    'records': records}, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'{len(records)} records: {destination}')
