import json
import os
import sys

results_expected = {
    'cfnullness': {
        'stack_trace': 29,
        'covered_lines': 56,
        'code_diff': 29,
        'report_diff': 18
    },
    'eradicate': {
        'stack_trace': 30,
        'covered_lines': 62,
        'code_diff': 30,
        'report_diff': 21
    },
    'infer': {
        'stack_trace': 16,
        'covered_lines': 37,
        'code_diff': 11,
        'report_diff': 12
    },
    'nullaway': {
        'stack_trace': 4,
        'covered_lines': 26,
        'code_diff': 5,
        'report_diff': 21
    },
    'sbht': {
        'stack_trace': 20,
        'covered_lines': 34,
        'code_diff': 4,
        'report_diff': 13
    },
    'sblt': {
        'stack_trace': 56,
        'covered_lines': 71,
        'code_diff': 12,
        'report_diff': 21
    }
}

def _validate_input(argv):
    if len(argv) != 2:
        print('Incorrect number of arguments provided.')
        sys.exit(1)
    bug_cand_fp = argv[1]
    if not os.path.isfile(bug_cand_fp):
        print('The bug_cand_fp argument is not a file or does not exist. Exiting.')
        sys.exit(1)
    return bug_cand_fp 

def count_artifacts(warnings):
    artifacts = set()
    for warning in warnings:
        artifacts = artifacts | set([warning['image_tag']])
    return len(artifacts)

def main(argv=None):
    argv = argv or sys.argv

    bug_cand_fp = _validate_input(argv)
    with open(bug_cand_fp) as f:
        bug_can_json = json.load(f)

    for tool in bug_can_json.keys():
        print(tool)
        for method in bug_can_json[tool].keys():
            repro = count_artifacts(bug_can_json[tool][method])
            expect = results_expected[tool][method]
            print('\t', method, repro, 'bug candidates - ', 'mismatch' if repro != results_expected[tool][method] else 'match')

if __name__ == '__main__':
    sys.exit(main())
