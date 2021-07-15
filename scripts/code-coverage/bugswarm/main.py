import os
import subprocess
import sys
import time

from distutils.dir_util import copy_tree

from os.path import abspath

from bugswarm.common import log
from bugswarm.common.shell_wrapper import ShellWrapper
from bugswarm.common.artifact_processing import utils as procutils
from bugswarm.common.artifact_processing.runners import ParallelArtifactRunner

_COPY_DIR = 'from_host'
_PROCESS_SCRIPT = 'process.py'
_MODIFY_POM_SCRIPT = 'modify_pom.py'
_POST_RUN_SCRIPT = 'post_run.py'

HOST_SANDBOX = abspath('../../auxiliary-data/coverage-proj-reports')

class CodeCoverageRunner(ParallelArtifactRunner):
    def __init__(self, image_tags_file, workers):
        with open(image_tags_file) as f:
            image_tags = list(map(str.strip, f.readlines()))
        super().__init__(image_tags, workers)

    @staticmethod
    def _get_command(image_tag, testname):
        return """export JAVA_HOME=/usr/lib/jvm/java-8-oracle/jre
            cp -f {container_sandbox}/{copy_dir}/* {failed_repo_dir}
            cd {failed_repo_dir} && echo 'Running {process_py} in failed repository.'
            sudo python {process_py} {image_tag} {container_sandbox} {modify_pom_py} 'failed' {testname}
            echo 'Done running {process_py}.'""".format(**{
            'image_tag': image_tag,

            'container_sandbox': procutils.CONTAINER_SANDBOX,
            'host_sandbox': HOST_SANDBOX,

            'copy_dir': _COPY_DIR,
            'failed_repo_dir': '/home/travis/build/failed/*/*/',

            'process_py': _PROCESS_SCRIPT,
            'modify_pom_py': _MODIFY_POM_SCRIPT,
            'testname': testname,
        })

    def process_artifact(self, image_tag: str):
        image_tag, testname = image_tag.split(',')
        return run_clover(image_tag, self._get_command(image_tag, testname))

    def pre_run(self):
        copy_tree(_COPY_DIR, os.path.join(HOST_SANDBOX, _COPY_DIR))

    def post_run(self):
        ShellWrapper.run_commands('python3 {} {} {}'
                                  .format(_POST_RUN_SCRIPT, HOST_SANDBOX, procutils.REPOS_DIR),
                                  shell=True)


def run_clover(image_tag, command):
    """
    Assumes that the caller wants to use the sandbox and stdin piping features of the BugSwarm client since this
    function will likely be called in the context of an artifact processing workflow.
    :param image_tag: The image tag representing the artifact image to run.
    :param command: A string containing command(s) to execute in the artifact container. Will be piped to the container
                    process' standard input stream.
    :return: A 2-tuple of
             - the combined output of stdout and stderr
             - the return code of the subprocess that ran the artifact container.
    """
    if not image_tag:
        raise ValueError
    c = command.split('\n')
    x = [x.strip() for x in c]
    cmd = ' && '.join(x)
    command_final = 'docker run -v {}:{} -i bugswarm/images:{} /bin/bash -lc "{}"'.format(HOST_SANDBOX, procutils.CONTAINER_SANDBOX, image_tag, cmd)
    process, stdout, stderr, ok = _run_command(command_final)
    print(stdout)
    print(stderr)
    return [stdout, stderr], ok


def _run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    stdout = stdout.decode('utf-8').strip()
    stderr = stderr.decode('utf-8').strip()
    ok = process.returncode == 0
    return process, stdout, stderr, ok


def _print_usage():
    log.info('Usage: python3 main.py <image_tags_file>')
    log.info('image_tags_file: Path to a file containing a tsv list of image tags with the testname to process.')


def _validate_input(argv):
    if len(argv) != 2:
      _print_usage()
      sys.exit(1)
    image_tags_file = argv[1]
    if not os.path.isfile(image_tags_file):
        log.error('The image_tags_file argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)
    return image_tags_file


def main(argv=None):
    argv = argv or sys.argv

    image_tags_file = _validate_input(argv)

    t_start = time.time()
    CodeCoverageRunner(image_tags_file, workers=1).run()
    t_end = time.time()
    print('Running Code Coverage took {}s'.format(t_end-t_start))


if __name__ == '__main__':
    sys.exit(main())
