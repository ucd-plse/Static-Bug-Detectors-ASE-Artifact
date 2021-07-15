import inspect
import os
import shutil
import subprocess
import sys
import time
import concurrent.futures

from os.path import abspath

from bugswarm.common.artifact_processing import utils as procutils
from bugswarm.common.artifact_processing.runners import ParallelArtifactRunner

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir) 
import utils

_SANDBOX_DIR = abspath('/'.join(current_dir.split('/')[:-2]) + '/results/eradicate-proj-reports')
BUG_DIR = abspath('/'.join(current_dir.split('/')[:-2]) + '/results/eradicate-proj-files')
SCRIPT_FP = os.path.dirname(os.path.realpath(__file__))
_SOURCE_DIR = '/home/travis/build'


class EradicateRunner(ParallelArtifactRunner):
    def __init__(self, b_or_f, bug_ids_file, build_script, workers = 1):
        """
        :param bug_ids_file: Path to a file containing a newline-separated list of image tags.
        :param copy_dir: A directory to copy into the host-side sandbox before any artifacts are processed.
        :param command: A callable used to determine what command(s) to execute in each artifact container. `command` is
                        called once for each processed artifact. The only parameter is the image tag of the artifact
                        about to be processed.
        :param workers: The same as for the superclass initializer.
        """
        self.bug_ids = bug_ids_file
        self.b_or_f = b_or_f
        self.build_script = build_script
        super().__init__(self.bug_ids, workers)


    def process_artifact(self, bug_id):
        return self.run_infer(bug_id, self._get_command(bug_id, self.b_or_f, self.build_script))

    @staticmethod
    def _get_command(bug_id, b_or_f, build_script):
        if build_script == 'build.xml':
            command = """export JAVA_HOME=/usr/lib/jvm/jdk1.8.0_221/jre
                export JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF8
                cd {source_dir}/{bug_id}{b_or_f}
                /infer/infer/bin/infer --keep-going --eradicate -- ant clean compile""".format(**{
                    'source_dir': _SOURCE_DIR,
                    'bug_id': bug_id,
                    'container_sandbox': _SANDBOX_DIR,
                    'b_or_f': b_or_f,
                })
        else: #pom.xml
            command = """export JAVA_HOME=/usr/lib/jvm/jdk1.8.0_221/jre
                export JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF8
                cd {source_dir}/{bug_id}{b_or_f}
                /infer/infer/bin/infer --keep-going --eradicate -- mvn clean compile""".format(**{
                    'source_dir': _SOURCE_DIR,
                    'bug_id': bug_id,
                    'container_sandbox': _SANDBOX_DIR,
                    'b_or_f': b_or_f,
                })
            
        return '/bin/bash -lc "{}"'.format(command)

    @staticmethod
    def run_infer(container_name, cmds):
        c = cmds.split('\n')
        x = [x.strip() for x in c]
        cmd = ' && '.join(x)
        command = 'docker run --rm -v {}:{} ' \
        'datomassi/images:infer-jdk8 {}'.format(BUG_DIR,
                                            _SOURCE_DIR, cmd)
        print(command)
        process, stdout, stderr, ok = utils.run_command(command)
        print(stdout, stderr)
        return process, stdout, stderr, ok


def _print_usage():
    print('Usage: python3 run_eradicate.py <bug_ids_file>')
    print('bug_ids_file: Path to a file containing a csv-separated list of bug ids,build script to process.')


def _validate_input(argv):
    bug_ids_file = argv[1]
    if not os.path.isfile(bug_ids_file):
        print('The bug_ids_file argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)
    return bug_ids_file


def main(argv=None):
    argv = argv or sys.argv

    bug_ids_file = _validate_input(argv)

    t_start = time.time()
    with open(bug_ids_file) as file:
        for line in file:
            line, build_script = line.strip().split(',')

            with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
                ti_start = time.time()
                for b_or_f in ['b','f']:
                    inf = EradicateRunner(b_or_f, [line], build_script, workers=1)
                    f1 = executor.submit(inf.run)
                    time.sleep(10)
                    while f1.running():
                        pass
                    cp_cmd = """mkdir -p {source_dir}/{bug_id}/{b_or_f} && cp {bug_dir}/{bug_id}{b_or_f}/infer-out/report.json {source_dir}/{bug_id}/{b_or_f}/""".format(**{
                            'source_dir': _SANDBOX_DIR,
                            'bug_id': line,
                            'bug_dir': BUG_DIR,
                            'b_or_f': b_or_f,
                    })
                    _, stdout, stderr, _ = utils.run_command(cp_cmd)
                ti_end = time.time()
                print('Done. {}'.format(ti_end-ti_start))
                continue

    t_end = time.time()
    print('Running Eradicate took {}s'.format(t_end-t_start))


if __name__ == '__main__':
    sys.exit(main())
