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


def verify_discovery(discovery):
    manifest = read(discovery / 'canonical_run.json')
    input_path = discovery / manifest['input_file']
    result_path = discovery / manifest['result_file']
    require(sha(input_path) == manifest['input_sha256'], 'Discovery source hash mismatch')
    require(sha(result_path) == manifest['result_sha256'], 'Discovery result hash mismatch')
    data, result = read(input_path), read(result_path)
    cases, outputs = data['cases'], result['cases']
    ids = {c['case_id'] for c in cases}
    output_by_id = {c['case_id']: c for c in outputs}
    require(len(cases) == len(ids) == data['case_count'] == 9, 'Discovery input count/IDs mismatch')
    require(len(outputs) == len(output_by_id) == result['case_count'] == 9 and ids == set(output_by_id), 'Discovery result count/IDs mismatch')
    require(result['eval_version'] == data['version'], 'Discovery version mismatch')
    totals = dict(case_passes=0, case_total=len(cases), case_execution_errors=0,
                  candidate_evaluable_cases=0, classifier_correct=0, classifier_total=0,
                  candidate_tp=0, candidate_fp=0, candidate_fn=0, title_correct=0,
                  company_correct=0, matched_candidates=0, provider_id_correct=0, provider_id_total=0)
    def norm(value):
        return ' '.join(str(value or '').casefold().split())
    for case in cases:
        output = output_by_id[case['case_id']]
        expected, jobs = case['expected_jobs'], output['jobs']
        require(output['expected_job_related'] == case['expected_job_related'], 'Discovery expected classification mismatch')
        require(output['expected_job_count'] == len(expected), 'Discovery expected count mismatch')
        require(output['predicted_job_count'] == len(jobs), 'Discovery prediction count mismatch')
        require(output['eval_bucket'] == case.get('eval_bucket'), 'Discovery bucket mismatch')
        error = output['error'] is not None
        predicted = output['predicted_job_related']
        require(predicted is None or type(predicted) is bool, 'Invalid Discovery classifier value')
        classifier_ok = predicted is not None and predicted == case['expected_job_related']
        totals['classifier_total'] += int(predicted is not None)
        totals['classifier_correct'] += int(classifier_ok)
        totals['case_execution_errors'] += int(error)
        included = output['candidate_metrics_included']
        require(type(included) is bool and included == (not error), 'Discovery execution/metric inclusion mismatch')
        require(predicted is not None or error, 'Discovery missing classification without error')
        require(predicted is not False or not jobs, 'Discovery negative classification has candidates')
        used = set()
        case_tp = case_fn = 0
        if included:
            totals['candidate_evaluable_cases'] += 1
            for expected_job in expected:
                stable_id = norm(expected_job.get('source_item_id'))
                available = [i for i in range(len(jobs)) if i not in used]
                match = next((i for i in available if stable_id and norm(jobs[i].get('source_item_id')) == stable_id), None)
                if match is None and stable_id:
                    match = next((i for i in available if stable_id in (jobs[i].get('source_url') or '')), None)
                if match is None:
                    match = next((i for i in available if norm(jobs[i]['title']) == norm(expected_job['title']) and norm(jobs[i]['company']) == norm(expected_job['company'])), None)
                if match is None:
                    case_fn += 1
                    continue
                used.add(match)
                job = jobs[match]
                require(job['source'] == case['source'] and job['source_message_id'] == case['message_id'], 'Discovery source provenance mismatch')
                case_tp += 1
                totals['title_correct'] += int(norm(job['title']) == norm(expected_job['title']))
                totals['company_correct'] += int(norm(job['company']) == norm(expected_job['company']))
                if stable_id:
                    totals['provider_id_total'] += 1
                    totals['provider_id_correct'] += int(norm(job.get('source_item_id')) == stable_id or stable_id in (job.get('source_url') or ''))
            totals['candidate_tp'] += case_tp
            totals['candidate_fn'] += case_fn
            totals['candidate_fp'] += len(jobs) - len(used)
            totals['matched_candidates'] += case_tp
        passed = not error and classifier_ok and included and case_fn == 0 and len(jobs) == case_tp == len(expected)
        require(output['case_pass'] == passed, 'Discovery per-case pass flag mismatch')
        totals['case_passes'] += int(passed)
    def ratio(a, b):
        return a / b if b else 0.0
    totals['case_pass_rate'] = ratio(totals['case_passes'], totals['case_total'])
    totals['classifier_accuracy'] = ratio(totals['classifier_correct'], totals['classifier_total'])
    precision = ratio(totals['candidate_tp'], totals['candidate_tp'] + totals['candidate_fp'])
    recall = ratio(totals['candidate_tp'], totals['candidate_tp'] + totals['candidate_fn'])
    totals.update(candidate_precision=precision, candidate_recall=recall,
                  candidate_f1=ratio(2 * precision * recall, precision + recall))
    require(result['summary'] == totals, 'Discovery summary differs from recomputed case metrics')
    print(f"Discovery: {len(cases)} cases; hashes and recomputed metrics match; {totals['case_passes']}/{len(cases)} cases passed. Location review remains manual.")


def main():
    verify_discovery(EVALS / 'discovery')

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
