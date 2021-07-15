import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def _validate_input(argv):
    if len(argv) != 2:
        print('Incorrect number of arguments provided.')
        sys.exit(1)
    bug_cand_fp = argv[1]
    if not os.path.isfile(bug_cand_fp):
        print('The bug_cand_fp argument is not a file or does not exist. Exiting.')
        sys.exit(1)
    return bug_cand_fp 

def compare_warning(tb, bc):
    return tb['image_tag'] == bc['image_tag'] and \
           bc['file'] in tb['file']

def compare_warning_rd(tb, bc):
    return tb == bc['image_tag']

def main(argv=None):
    argv = argv or sys.argv

    with open(os.path.join(SCRIPT_DIR, 'true_bugs.json')) as tb_f:
        results_expected = json.load(tb_f)

    bug_cand_fp = _validate_input(argv)
    with open(bug_cand_fp) as f:
        bug_can_json = json.load(f)

    for tool in sorted(bug_can_json.keys()):
        print(tool)
        for method in ['code_diff', 'report_diff', 'stack_trace', 'covered_lines']:
            num_match = 0
            for tb_warning in results_expected[tool][method]:
                for bc_warning in bug_can_json[tool][method]:
                    if method == 'report_diff':
                        if compare_warning_rd(tb_warning, bc_warning):
                            num_match += 1
                            break
                    else:
                        if compare_warning(tb_warning, bc_warning):
                            num_match += 1
                            break
            print('\t', method, num_match, 'true bugs - ', 'mismatch' if num_match != len(results_expected[tool][method]) else 'match')

if __name__ == '__main__':
    sys.exit(main())
