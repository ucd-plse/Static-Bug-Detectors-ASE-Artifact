import inspect
import os
import re
import subprocess
import sys
import time

from distutils.dir_util import copy_tree

from os.path import abspath

from bugswarm.common.shell_wrapper import ShellWrapper
from bugswarm.common.artifact_processing import utils as procutils
from bugswarm.common.artifact_processing.runners import ParallelArtifactRunner

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir) 
import utils

_COPY_DIR = 'from_host'
_PROCESS_SCRIPT = 'process.py'
_MODIFY_POM_SCRIPT = 'modify_pom.py'
_POST_RUN_SCRIPT = 'post_run.py'

HOST_SANDBOX = abspath('../../results/sblt-proj-reports')

class SpotbugsRunner(ParallelArtifactRunner):
    def __init__(self, image_tags_file, dockerhub_repo, l_or_h, workers):
        with open(image_tags_file) as f:
            image_tags = list(map(str.strip, f.readlines()))
        super().__init__(image_tags, workers)
        self.dockerhub_repo = dockerhub_repo
        self.l_or_h = l_or_h

    @staticmethod
    def _get_command(image_tag, l_or_h):
        return """export JAVA_HOME=/usr/lib/jvm/java-8-oracle/jre
            cp -f {container_sandbox}/{copy_dir}/* {failed_repo_dir}
            cp -f {container_sandbox}/{copy_dir}/* {passed_repo_dir}
            cd {failed_repo_dir} && echo 'Running {process_py} in failed repository.'
            sudo python {process_py} {image_tag} {container_sandbox} {modify_pom_py} 'failed' {l_h}
            echo 'Done running {process_py}.'
            cd {passed_repo_dir} && echo 'Running {process_py} in passed repository.'
            sudo python {process_py} {image_tag} {container_sandbox} {modify_pom_py} 'passed' {l_h}
            echo 'Done running {process_py}.'""".format(**{
            'image_tag': image_tag,

            'container_sandbox': procutils.CONTAINER_SANDBOX,
            'host_sandbox': HOST_SANDBOX,

            'copy_dir': _COPY_DIR,
            'failed_repo_dir': '/home/travis/build/failed/*/*/',
            'passed_repo_dir': '/home/travis/build/passed/*/*/',

            'process_py': _PROCESS_SCRIPT,
            'modify_pom_py': _MODIFY_POM_SCRIPT,
            'l_h': l_or_h,
        })

    def process_artifact(self, image_tag: str):
        return self.run_spotbugs(image_tag, self._get_command(image_tag, self.l_or_h), self.dockerhub_repo)

    def pre_run(self):
        copy_tree(_COPY_DIR, os.path.join(HOST_SANDBOX, _COPY_DIR))

    def post_run(self):
        ShellWrapper.run_commands('python3 {} {} {}'
                                  .format(_POST_RUN_SCRIPT, HOST_SANDBOX, procutils.REPOS_DIR),
                                  shell=True)

    @staticmethod
    def run_spotbugs(image_tag, command, dockerhub_repo):
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
        command_final = 'docker run -v {}:{} -i {}:{} /bin/bash -lc "{}"'.format(HOST_SANDBOX, procutils.CONTAINER_SANDBOX, dockerhub_repo, image_tag, cmd)
        process, stdout, stderr, ok = utils.run_command(command_final)
        print(stdout)
        print(stderr)
        return [stdout, stderr], ok


def _print_usage():
    print('Usage: python3 main.py <image-tags-file> <dockerhub-repo> <low_or_high> <number-of-workers>')
    print('image-tags-file: Path to a file containing a newline-separated list of image tags to process.')
    print('dockerhub-repo: DockerHub repo that will pull the docker images from.')
    print('number-of-workers: Number of threads.')


def _validate_input(argv):
    if len(argv) != 5:
      _print_usage()
      sys.exit(1)
    image_tags_file = argv[1]
    if not os.path.isfile(image_tags_file):
        log.error('The image_tags_file argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)
    dockerhub_repo = argv[2]
    l_or_h = argv[3]
    num_workers = int(argv[4])
    return image_tags_file, dockerhub_repo, l_or_h, num_workers


def main(argv=None):
    argv = argv or sys.argv

    image_tags_file, dockerhub_repo, l_or_h, num_workers = _validate_input(argv)
    global HOST_SANDBOX
    if l_or_h == 'high':
        HOST_SANDBOX = re.sub(r'sblt', 'sbht', HOST_SANDBOX)
    t_start = time.time()
    SpotbugsRunner(image_tags_file, dockerhub_repo, l_or_h, workers=num_workers).run()
    t_end = time.time()
    print('Running Spotbugs took {}s'.format(t_end-t_start))


if __name__ == '__main__':
    sys.exit(main())
