import json
import sys

from db_utils import DatabaseConnection

# Configure DB.
DB = DatabaseConnection('root', 'password')
db_name = sys.argv[1]
DB.select_database(db_name)

# Tool and mapping method constants.
TOOLS = ['sblt', 'sbht', 'eradicate', 'infer', 'nullaway', 'cfnullness']
mapping_methods_dict = {'code_diff': DB.code_diff,
                        'report_diff': DB.report_diff,
                        'stack_trace': DB.stack_trace,
                        'covered_lines': DB.covered_lines}

def main():
    results_dict = {'sblt': {'code_diff': {}, 'report_diff':{}, 'stack_trace':{}, 'covered_lines':{}}, 
                    'sbht': {'code_diff': {}, 'report_diff':{}, 'stack_trace':{}, 'covered_lines':{}}, 
                    'eradicate': {'code_diff': {}, 'report_diff':{}, 'stack_trace':{}, 'covered_lines':{}},
                    'infer':{'code_diff': {}, 'report_diff':{}, 'stack_trace':{}, 'covered_lines':{}},
                    'nullaway': {'code_diff': {}, 'report_diff':{}, 'stack_trace':{}, 'covered_lines':{}},
                    'cfnullness': {'code_diff': {}, 'report_diff':{}, 'stack_trace':{}, 'covered_lines':{}}
                   }

    for tool in TOOLS:
        for mapping_method in mapping_methods_dict:
            print('Running {} on {}'.format(mapping_method, tool))
            if mapping_method == 'code_diff':
                result = mapping_methods_dict[mapping_method]('diff', tool)
            elif mapping_method == 'report_diff':
                result = mapping_methods_dict[mapping_method](tool)
            elif mapping_method == 'stack_trace':
                result = mapping_methods_dict[mapping_method]('trace', tool)
            else: # covered_lines
                result = mapping_methods_dict[mapping_method]('covered_lines', tool)
            results_dict[tool][mapping_method] = result

    with open('bug_candidates.json', 'w+') as output_file:
        json.dump(results_dict, output_file, indent=4)
    print('Successfully wrote bug candidates to bug_candidates.json')

if __name__ == '__main__':
    sys.exit(main())

