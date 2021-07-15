import lxml
import os
import re
import subprocess
import sys

from os.path import abspath

from bugswarm.common.rest_api.database_api import DatabaseAPI
from bugswarm.common.credentials import DATABASE_PIPELINE_TOKEN

OUTPUT_DIR = abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../auxiliary-data'))
print(OUTPUT_DIR)
API = DatabaseAPI(token=DATABASE_PIPELINE_TOKEN)

def main(argv=None):
    if argv is None:
        argv = sys.argv

    image_tags_fp = _validate_input(argv)
    LOG_DIR = '{}/log_tmp'.format(os.getcwd())
    _make_tmp_dir()

    image_tags = []
    with open(image_tags_fp) as file:
        for line in file:
            line = line.strip()
            image_tags.append(line)

    trace_funcs_dict = {}
    for image_tag in image_tags:
        image_tag_split = image_tag.split('-')
        log_fp = '{}/{}.log'.format(LOG_DIR, image_tag)
        try:
            log_contents = API.get_build_log(str(image_tag_split[len(image_tag_split)-1]))
        except BaseException:
            continue
        if not log_contents:
            continue
        with open(log_fp, 'w+') as f:
            f.write(log_contents)
        trace_funcs = []
        with open(log_fp) as file:
            npe_started = False
            for line in file:
                line = line.strip()
                m = re.search(r'java.lang.NullPointerException', line)
                if m:
                    npe_started = True
                    continue
                if line != '' and npe_started:
                    m = re.match(r'^at [\w\.$]+\(([\w\.]+):([0-9]+)\)', line)
                    if m:
                        trace_funcs.append((m.group(1), m.group(2)))
                        continue
                if npe_started and line == '':
                    npe_started = False
        trace_funcs_dict[image_tag] = trace_funcs

    with open(os.path.join(OUTPUT_DIR, 'stack-trace.csv'), 'w+') as file:
        for key in trace_funcs_dict:
            for func in trace_funcs_dict[key]:
                file.write('{},{},{}\n'.format(key, func[0], func[1]))


def _make_tmp_dir():
    cmd = 'mkdir {}/log_tmp'.format(os.getcwd())
    _, stdout, stderr, ok = _run_command(cmd)
    if not ok and ' File exists' not in stderr:
        _print_error('Error creating log directory', stdout, stderr)
        sys.exit(1)


def _run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    stdout = stdout.decode('utf-8').strip()
    stderr = stderr.decode('utf-8').strip()
    ok = process.returncode == 0
    return process, stdout, stderr, ok


def _print_error(msg, stdout=None, stderr=None):
    print('Error: ' + msg)
    if stdout is not None:
        print('stdout:\n{}'.format(stdout))
    if stderr is not None:
        print('stderr:\n{}'.format(stderr))


def _print_usage():
    print('Usage: python3 changes.py <image_tags_filepath>')


def _validate_input(argv):
    image_tags_filepath = argv[1]

    if not os.path.isfile(image_tags_filepath):
        log.error('The image_tags_filepath argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)

    return image_tags_filepath

if __name__ == '__main__':
    sys.exit(main())
