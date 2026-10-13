"""Offline checks of frozen public artifacts; no provider calls or new semantic eval."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

EVALS = Path(__file__).resolve().parent
LABELS = ('STRONG', 'PARTIAL', 'WEAK', 'NOT_CLEARLY_SUPPORTED')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    discovery = EVALS / 'discovery'
    result = read(discovery / 'results/discovery_eval_v1_20261008T235717Z.json')
    require(sha(discovery / 'cases_v1.json') == result['input_sha256'], 'Discovery source hash mismatch')
    require(result['summary']['case_count'] == 8, 'Discovery count changed')
    print('Discovery: frozen source hash matches, 8 cases; recorded location review pending.')

    requirements = EVALS / 'requirement_extraction'
    manifest = read(requirements / 'manifest.json')
    cases = read(requirements / 'cases_v1.json')['cases']
    case_by_id = {c['case_id']: c for c in cases}
    require(len(manifest['cases']) == len(case_by_id) == 8, 'Requirement case count/IDs changed')
    for case in manifest['cases']:
        path = requirements / 'cases' / case['filename']
        require(sha(path) == case['sha256'], f"Requirement hash mismatch: {case['case_id']}")
        require(path.read_text() == case_by_id[case['case_id']]['jd_text'], f"Runner/source text mismatch: {case['case_id']}")
    print('Requirement extraction: 8 frozen source hashes and runner texts match.')

    matching = EVALS / 'matching_evaluation'
    evidence_path = matching / 'fixed_inputs/01_input_fixed_candidate_evidence_v2.json'
    requirements_path = matching / 'fixed_inputs/02_input_representative_requirements_v2.json'
    evidence = read(evidence_path)['evidence_units']
    reqs = read(requirements_path)['requirements']
    gold = read(matching / 'gold_set/03_gold_output_human_adjudicated_mappings_v2.json')['records']
    eids = {e['evidence_id'] for e in evidence}
    rids = {r['requirement_id'] for r in reqs}
    refs = {g['requirement_id']: g['gold_support_level'] for g in gold}
    require(len(evidence) == len(eids) == 120, 'Evidence count/ID mismatch')
    require(len(reqs) == len(rids) == len(gold) == len(refs) == 32, 'Requirement/Gold count/ID mismatch')
    require(rids == set(refs), 'Gold requirement IDs differ from inputs')
    require(set(refs.values()) <= set(LABELS), 'Unknown Gold support label')
    for filename in ('matcher_predictions_v2.json', 'matcher_predictions_v2_promptfix1.json'):
        run = read(matching / 'results' / filename)
        require(run['input_files']['candidate_evidence']['sha256'] == sha(evidence_path), 'Recorded evidence hash mismatch')
        require(run['input_files']['representative_requirements']['sha256'] == sha(requirements_path), 'Recorded requirement hash mismatch')
        mappings = run['final']['mappings']
        pred = {m['requirement_id']: m['support_level'] for m in mappings}
        require(len(mappings) == len(pred) == 32 and set(pred) == rids, 'Prediction requirement coverage/IDs mismatch')
        require(set(pred.values()) <= set(LABELS), 'Unknown prediction support label')
        for mapping in mappings:
            require(all(e['evidence_id'] in eids for e in mapping['evidence_matches']), 'Prediction references unknown evidence')
        correct = sum(refs[k] == pred[k] for k in refs)
        f1s = []
        for label in LABELS:
            tp = sum(refs[k] == pred[k] == label for k in refs)
            fp = sum(refs[k] != label and pred[k] == label for k in refs)
            fn = sum(refs[k] == label and pred[k] != label for k in refs)
            f1s.append(2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0)
        print(f'{filename}: {correct}/32 exact ({correct/32:.1%}), macro F1 {sum(f1s)/4:.3f}')

    snapshot = EVALS / 'evidence_extraction/source_snapshots/README_before_portfolio_cleanup.md'
    expanded_gold = read(EVALS / 'evidence_extraction/gold_set/job_agent_evidence_gold_v2.json')
    require(sha(snapshot) == '8c93789571b642c36bdfc34145f12443504eec73fdaf11dc15d553177864e375', 'Pre-cleanup source snapshot changed')
    require(len(expanded_gold['evidence_units']) == 50, 'Expanded evidence annotation count changed')
    print('Provenance limitation: expanded Gold historical source hash differs from the supplied README snapshot; see evidence evaluation README.')
    print('Artifact integrity checks passed. No live model evaluation was run.')


if __name__ == '__main__':
    main()
