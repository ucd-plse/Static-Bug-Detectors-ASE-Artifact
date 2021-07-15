import os
import sys

def _validate_input(argv):
    if len(argv) != 3:
        print('Incorrect number of arguments provided.')
        sys.exit(1)
    replicated_fp = argv[1]
    study_fp = argv[2]
    if not os.path.isfile(replicated_fp):
        print('The replicated_fp argument is not a file or does not exist. Exiting.')
        sys.exit(1)
    if not os.path.isfile(study_fp):
        print('The study_fp argument is not a file or does not exist. Exiting.')
        sys.exit(1)
    return replicated_fp, study_fp 

def main(argv=None):
    argv = argv or sys.argv

    replicated_fp, study_fp = _validate_input(argv)
    
    with open(replicated_fp) as rep_f:
        replicated_warnings = [warning.strip() for warning in rep_f.readlines()]

    with open(study_fp) as study_f:
        study_warnings = [warning.strip() for warning in study_f.readlines()]

    replicated_warnings.sort()
    study_warnings.sort()
    
    for i in range(len(replicated_warnings)):
        if replicated_warnings[i] not in study_warnings:
            print('Mismatch in warnings.')
            sys.exit(1)
    print('Warnings match.')

if __name__ == '__main__':
    sys.exit(main())
