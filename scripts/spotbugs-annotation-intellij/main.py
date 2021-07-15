import os
import subprocess
import sys
import time

from distutils.dir_util import copy_tree

from bugswarm.common import log
from bugswarm.common.shell_wrapper import ShellWrapper
from bugswarm.common.artifact_processing import utils as procutils
from bugswarm.common.artifact_processing.runners import ParallelArtifactRunner

DOCKERHUB_REPO = 'datomassi/bugswarm-intellij-annotated'
DOCKERHUB_REPO_SB = 'datomassi/bugswarm-intellij-annotated-sb'
_MODIFY_POM_SCRIPT = 'modify_pom.py'
_COPY_DIR = 'from_host'


class SpotBugsAnnotationRunner(ParallelArtifactRunner):
    def __init__(self, image_tags_file, workers):
        with open(image_tags_file) as f:
            image_tags = list(map(str.strip, f.readlines()))
        super().__init__(image_tags, workers)

    @staticmethod
    def _get_command(image_tag):
        return """cp -f {container_sandbox}/{copy_dir}/* {failed_repo_dir}
            cp -f {container_sandbox}/{copy_dir}/* {passed_repo_dir}
            sudo pip install bs4
            cd {failed_repo_dir} && echo 'In failed repository.'
            grep -rli '@Nullable' * | xargs sed -i 's/@Nullable/@CheckForNull/g'
            grep -rli 'org.jetbrains.annotations.Nullable' * | xargs sed -i 's/org.jetbrains.annotations.Nullable/javax.annotation.CheckForNull/g'
            grep -rli 'org.jetbrains.annotations.NotNull' * | xargs sed -i 's/org.jetbrains.annotations.NotNull/javax.annotation.NotNull/g'
            python modify_pom.py pom.xml
            rm modify_pom.py
            cd {passed_repo_dir} && echo 'In passed repository.'
            grep -rli '@Nullable' * | xargs sed -i 's/@Nullable/@CheckForNull/g'
            grep -rli 'org.jetbrains.annotations.Nullable' * | xargs sed -i 's/org.jetbrains.annotations.Nullable/javax.annotation.CheckForNull/g'
            grep -rli 'org.jetbrains.annotations.NotNull' * | xargs sed -i 's/org.jetbrains.annotations.NotNull/javax.annotation.NotNull/g'
            python modify_pom.py pom.xml
            rm modify_pom.py""".format(**{
            'image_tag': image_tag,

            'container_sandbox': procutils.CONTAINER_SANDBOX,
            'host_sandbox': procutils.HOST_SANDBOX,

            'copy_dir': _COPY_DIR,
            'failed_repo_dir': '/home/travis/build/failed/*/*/',
            'passed_repo_dir': '/home/travis/build/passed/*/*/',

            'modify_pom_py': _MODIFY_POM_SCRIPT,
        })

    def process_artifact(self, image_tag: str):
        return run(image_tag, self._get_command(image_tag))

    def pre_run(self):
        copy_tree(_COPY_DIR, os.path.join(procutils.HOST_SANDBOX, _COPY_DIR))



def run(image_tag, command):
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
    command_final = 'docker run -v {}:{} --name {} -i {}:{} /bin/bash -lc "{}"'.format(procutils.HOST_SANDBOX, procutils.CONTAINER_SANDBOX, image_tag, DOCKERHUB_REPO, image_tag, cmd)
    process, stdout, stderr, ok = _run_command(command_final)
    print(stdout)
    print(stderr)
    dckr_cmt_cmd = 'docker commit {}'.format(image_tag)
    process, sha, stderr, ok = _run_command(dckr_cmt_cmd)
    print(stdout)
    print(stderr)
    dckr_tag_cmd = 'docker tag {} {}:{}'.format(sha, DOCKERHUB_REPO_SB, image_tag)
    process, stdout, stderr, ok = _run_command(dckr_tag_cmd)
    print(stdout)
    print(stderr)
    dckr_push_cmd = 'docker push {}:{}'.format(DOCKERHUB_REPO_SB, image_tag)
    process, stdout, stderr, ok = _run_command(dckr_push_cmd)
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
    SpotBugsAnnotationRunner(image_tags_file, workers=1).run()
    t_end = time.time()
    print('Running Spotbugs Annotations took {}s'.format(t_end-t_start))


if __name__ == '__main__':
    sys.exit(main())

