import inspect
import os
import subprocess
import sys
import time

from distutils.dir_util import copy_tree

from os.path import abspath

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

HOST_SANDBOX = abspath('../../results/checkerframework-proj-reports')

class NullnessCheckerRunner(ParallelArtifactRunner):
    def __init__(self, image_tags_file, dockerhub_repo, workers):
        with open(image_tags_file) as f:
            image_tags = list(map(str.strip, f.readlines()))
        self.dockerhub_repo = dockerhub_repo
        super().__init__(image_tags, workers)


    @staticmethod
    def _get_command(image_tag):
        return """source /etc/profile
            export JAVA_HOME=/usr/lib/jvm/java-8-oracle/jre
            sudo pip install bs4
            sudo pip install lxml
            cp -f {container_sandbox}/{copy_dir}/* {failed_repo_dir}
            cp -f {container_sandbox}/{copy_dir}/* {passed_repo_dir}
            cd {failed_repo_dir} && echo 'Running {process_py} in failed repository.'
            python modify_pom.py pom.xml
            mvn clean install -U -fn -DskipTests -Dcheckstyle.skip -Denforcer.skip=true -Danimal.sniffer.skip=true >> nullness.txt 2>&1
            sudo mkdir -p {container_sandbox}/{image_tag}/failed
            sudo cp nullness.txt {container_sandbox}/{image_tag}/failed
            cd {passed_repo_dir} && echo 'Running {process_py} in passed repository.'
            python modify_pom.py pom.xml
            mvn clean install -U -fn -DskipTests -Dcheckstyle.skip -Denforcer.skip=true -Danimal.sniffer.skip=true >> nullness.txt 2>&1
            sudo mkdir -p {container_sandbox}/{image_tag}/passed
            sudo cp nullness.txt {container_sandbox}/{image_tag}/passed""".format(**{
            'image_tag': image_tag,

            'container_sandbox': procutils.CONTAINER_SANDBOX,
            'host_sandbox': HOST_SANDBOX,

            'copy_dir': _COPY_DIR,
            'failed_repo_dir': '/home/travis/build/failed/*/*/',
            'passed_repo_dir': '/home/travis/build/passed/*/*/',

            'process_py': _PROCESS_SCRIPT,
            'modify_pom_py': _MODIFY_POM_SCRIPT,
        })

    def process_artifact(self, image_tag: str):
        return self.run_nullness(image_tag, self._get_command(image_tag), self.dockerhub_repo)

    def pre_run(self):
        copy_tree(_COPY_DIR, os.path.join(HOST_SANDBOX, _COPY_DIR))

    @staticmethod
    def run_nullness(image_tag, command, dockerhub_repo):
        if not image_tag:
            raise ValueError
        c = command.split('\n')
        x = [x.strip() for x in c]
        cmd = ' && '.join(x)
        command_final = 'docker run -v {}:{} -i {}:{} /bin/bash -lc "{}"'.format(HOST_SANDBOX, procutils.CONTAINER_SANDBOX, dockerhub_repo, image_tag, cmd)
        process, stdout, stderr, ok = utils.run_command(command_final)

def _print_usage():
    print('Usage: python3 main.py <image-tags-file> <dockerhub-repo> <number-of-workers>')
    print('image-tags-file: Path to a file containing a newline-separated list of image tags to process.')
    print('dockerhub-repo: DockerHub repo to pull the docker image from.')
    print('number-of-workers: Number of threads.')


def _validate_input(argv):
    if len(argv) != 4:
        _print_usage()
        sys.exit(1)
    image_tags_file = argv[1]
    if not os.path.isfile(image_tags_file):
        log.error('The image_tags_file argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)
    dockerhub_repo = argv[2]
    num_workers = int(argv[3])
    return image_tags_file, dockerhub_repo, num_workers


def main(argv=None):
    argv = argv or sys.argv

    image_tags_file, dockerhub_repo, num_workers = _validate_input(argv)

    t_start = time.time()
    NullnessCheckerRunner(image_tags_file, dockerhub_repo, workers=num_workers).run()
    t_end = time.time()
    print('Running Nullness Checker took {}s'.format(t_end - t_start))


if __name__ == '__main__':
    sys.exit(main())
