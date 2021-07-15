import os
import sys

def _validate_input(argv):
    if len(argv) != 4:
        print('Incorrect number of arguments provided.')
        sys.exit(1)
    replicated_fp = argv[1]
    study_fp = argv[2]
    tool_name = argv[3]
    if not os.path.isfile(replicated_fp):
        print('The replicated_fp argument is not a file or does not exist. Exiting.')
        sys.exit(1)
    if not os.path.isfile(study_fp):
        print('The study_fp argument is not a file or does not exist. Exiting.')
        sys.exit(1)
    return replicated_fp, study_fp, tool_name

def main(argv=None):
    argv = argv or sys.argv

    replicated_fp, study_fp, tool_name = _validate_input(argv)
    
    with open(replicated_fp) as rep_f:
        replicated_warnings = [warning.strip() for warning in rep_f.readlines()]

    with open(study_fp) as study_f:
        study_warnings = [warning.strip() for warning in study_f.readlines()]

    match_all_txt = 'match' if len(replicated_warnings) == len(study_warnings) else 'mismatch'
    print('Number of warnings: ', len(replicated_warnings), match_all_txt)
    if tool_name in ['nullaway', 'cfnullness', 'eradicate']:
        num_npes_warnings = len(replicated_warnings)
        num_npes_warnings_study = len(replicated_warnings)
    else:
        warning_txt = ''
        if tool_name == 'infer':
            warning_txt = 'NULL'
        else:
            warning_txt = 'NP_'
        num_npes_warnings = 0
        num_npes_warnings_study = 0
        for warning in replicated_warnings:
            if warning_txt in warning:
                num_npes_warnings += 1
        for warning in study_warnings:
            if warning_txt in warning:
                num_npes_warnings_study += 1
    match_npes_txt = 'match' if num_npes_warnings == num_npes_warnings_study else 'mismatch'
    print('Number of NPE warnings: ', num_npes_warnings, match_npes_txt)
    print('Avg. All: ', round(len(study_warnings) / (102 *2)), match_all_txt)
    print('Avg. NPEs: ', round(num_npes_warnings / (102 *2)), match_npes_txt)

if __name__ == '__main__':
    sys.exit(main())
