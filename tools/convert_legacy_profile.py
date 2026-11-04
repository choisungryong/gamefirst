"""Explicit one-time converter. Game runtime never reads D2R or research files.

JSON catalog is the runtime definition source. Re-run only for an intentional
catalog migration; this is not automatic synchronization with research.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

# Identity anchors from the existing reviewed CASC extraction for build93847.
# This bounded converter rejects other bytes instead of attaching an old build label.
TABLE_HASHES_93847 = {
    'skills.txt': '56944cb6b6b0f3c57f7b690977987a732afeafc961fa9dc969e7796e54c93f3f',
    'monstats.txt': '8831fce35fc549a4849b13a1bd467eb34913f58b8269c0c1bbfa76aeabb6d32e',
    'treasureclassex.txt': '3abbfc59535e67cf52b0256b3518623edba072eb4235e7d1824a7f847abeca6d',
}


def convert(profile):
    p = profile['provisional_parameters']
    choice = {'status': 'design_choice', 'method': 'project_design',
              'note': 'Independent experiment choice; not recovered D2R logic'}
    supported = {
        'mana_cost': dict(choice, basis=['formula.mana.normal_branch', 'observation.RT-003']),
        'damage': dict(choice, basis=['formula.damage.level1']),
        'startup': dict(choice, basis=['observation.RT-007.visible_separation'],
                        note='Visible comparison target, not D2R internal release tick'),
        'cycle': dict(choice, basis=[]),
    }
    return {
        'schema_version': 1,
        'catalog_id': 'catalog.combat_baseline.v1',
        'definition_version': 1,
        'numeric_scale': 256,
        'simulation_hz': p['simulation_hz'],
        'provenance': choice,
        'stats': [
            {'id': 'stat.health', 'unit': 'health', 'scale': 256, 'provenance': choice},
            {'id': 'stat.mana', 'unit': 'mana', 'scale': 256, 'provenance': choice},
        ],
        'player': {
            'id': 'actor.caster', 'health_stat_id': 'stat.health',
            'mana_stat_id': 'stat.mana',
            'max_health_raw': int(profile['player']['life'] * 256),
            'max_mana_raw': profile['player']['mana_raw'],
            'move_speed_world_per_second': p['player_world_speed'],
            'spawn_world': p['spawn_player_world'], 'provenance': choice,
        },
        'skills': [{
            'id': 'skill.ember_bolt', 'projectile_id': 'projectile.ember_bolt',
            'cost': {'stat_id': 'stat.mana', 'raw': profile['firebolt']['mana_cost_raw'], 'unit': 'mana', 'scale': 256},
            'damage': {'stat_id': 'stat.health', 'min_raw': profile['firebolt']['damage_raw'][0], 'max_raw': profile['firebolt']['damage_raw'][1], 'unit': 'health', 'scale': 256, 'element': 'fire'},
            'startup_ticks': round(profile['firebolt']['visible_startup_seconds'] * p['simulation_hz']),
            'cycle_ticks': round(p['repeat_seconds'] * p['simulation_hz']),
            'provenance': supported,
        }],
        'projectiles': [{
            'id': 'projectile.ember_bolt',
            'speed_world_per_second': p['projectile_world_speed'],
            'lifetime_seconds': p['projectile_life_seconds'],
            'spawn_offset_world': p['projectile_spawn_offset'],
            'collision_radius_world': p['collision_radius'], 'provenance': choice,
        }],
        'enemies': [{
            'id': 'enemy.mire_walker', 'health_stat_id': 'stat.health',
            'max_health_raw': round(p['enemy_hp'] * 256),
            'move_speed_world_per_second': p['enemy_speed'],
            'spawn_world': p['spawn_enemy_world'],
            'attack': {'windup_seconds': p['enemy_attack_windup_seconds'],
                       'recovery_seconds': p['enemy_attack_recovery_seconds'],
                       'start_range_world': p['enemy_attack_start_range'],
                       'hit_range_world': p['enemy_attack_hit_range'],
                       'damage_raw': round(p['enemy_damage'] * 256)},
            'hurt_seconds': p['enemy_hurt_seconds'],
            'death_threshold_raw': p['death_threshold_raw'], 'provenance': choice,
        }],
        'experiment': {
            'skill_id': 'skill.ember_bolt', 'enemy_id': 'enemy.mire_walker',
            'world_bounds': p['world_bounds'], 'rng_seed': p['rng_seed'],
            'mana_regen_per_second': p['mana_regen_per_second'],
            'damage_selection': p['damage_selection'], 'charge_phase': p['charge_phase'],
            'atlas_playback_fps': p['atlas_playback_fps'],
            'proxy_cast_animation_speed': p['proxy_cast_animation_speed'],
            'provenance': choice,
        },
    }


def research_claims(tables):
    for name, expected in TABLE_HASHES_93847.items():
        observed = hashlib.sha256((tables / name).read_bytes()).hexdigest()
        if observed != expected:
            raise ValueError(f'Unsupported research source identity for build93847: {name}')
    claims = []
    selections = [('skills.txt', 'skill', 'Fire Bolt', ['mana', 'manashift', 'EMin', 'EMax', 'HitShift']),
                  ('monstats.txt', 'Id', 'zombie1', ['noRatio', 'ResFi'])]
    for name, key, value, fields in selections:
        path = tables / name
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        rows = list(csv.DictReader(path.read_text(encoding='utf-8-sig').splitlines(), delimiter='\t'))
        for index, row in enumerate(rows, 2):
            if row.get(key) == value:
                for field in fields:
                    if field not in row:
                        raise ValueError(f'Missing source column {field} in {name}')
                    claims.append({'id': f'{name}.{value}.{field}', 'method': 'local_casc_extract',
                                   'status': 'observed', 'raw': row[field], 'normalized': None,
                                   'unit': None, 'meaning_status': 'unknown',
                                   'locator': {'path': str(path), 'sha256': sha, 'line': index,
                                               'selector': {key: value}, 'column': field},
                                   'limitations': ['Observed table bytes, not D2R runtime value or native function']})
                break
        else:
            raise ValueError(f'Source row not found: {name} {key}={value}')
    path = tables / 'treasureclassex.txt'
    rows = list(csv.DictReader(path.read_text(encoding='utf-8-sig').splitlines(), delimiter='\t'))
    for index, row in enumerate(rows, 2):
        if row.get('Picks', '').startswith('-'):
            claims.append({'id': 'treasureclassex.first_signed_picks', 'method': 'local_casc_extract',
                           'status': 'observed', 'raw': row['Picks'], 'normalized': None,
                           'unit': None, 'meaning_status': 'unknown',
                           'locator': {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                                       'line': index, 'selector': {'Treasure Class': row['Treasure Class']}, 'column': 'Picks'},
                           'limitations': ['Negative source value preserved; roll semantics not established']})
            break
    return {'schema_version': 1, 'build': '93847', 'claims': claims}


def evidence_index(research_root):
    sources = [
        ('formula.mana.normal_branch', 'FORMULA-EVIDENCE.json', 'classic_reference', 'derived', 'Normal mana branch raw640, scale256; current D2R native equality unknown'),
        ('formula.damage.level1', 'FORMULA-EVIDENCE.json', 'classic_reference', 'derived', 'Level1 raw768-1536; current applied damage unknown'),
        ('observation.RT-003', 'RUNTIME-OBSERVATIONS.json', 'runtime_observation', 'observed', 'Earlier REA character UI tooltip, not latest READ equipment'),
        ('observation.RT-007.visible_separation', 'CAST-VISIBILITY.json', 'runtime_observation', 'derived', 'Visible motion to separated bolt, not native release tick'),
    ]
    result = []
    for id_, name, method, status, scope in sources:
        path = research_root / 'baseline' / name
        result.append({'id': id_, 'method': method, 'status': status, 'scope': scope,
                       'locator': {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}})
    return result


def main():
    parser = argparse.ArgumentParser()
    root = Path(__file__).resolve().parents[1]
    parser.add_argument('--profile', type=Path, default=root / 'evidence-profile.json')
    parser.add_argument('--tables', type=Path, default=Path(r'C:\Project\game-research\d2r-analysis\tables'))
    parser.add_argument('--output', type=Path, default=root / 'game_data' / 'catalog.json')
    parser.add_argument('--research-output', type=Path, default=root / 'research' / 'phase1-claims.json')
    args = parser.parse_args()
    profile = json.loads(args.profile.read_text(encoding='utf-8-sig'))
    catalog = convert(profile)
    catalog['migration_source_sha256'] = hashlib.sha256(args.profile.read_bytes()).hexdigest()
    claims = research_claims(args.tables)
    catalog['evidence_index'] = evidence_index(args.tables.parent)
    for path, value in [(args.output, catalog), (args.research_output, claims)]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'catalog': str(args.output), 'claims': len(claims['claims']),
                      'source_unchanged_sha256': catalog['migration_source_sha256']}))


if __name__ == '__main__':
    main()
