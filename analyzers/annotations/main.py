import os
import subprocess
import sys
import time

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from distutils.dir_util import copy_tree
from typing import Callable
from typing import List

from bugswarm.common import log
from bugswarm.common.shell_wrapper import ShellWrapper
from bugswarm.common.artifact_processing import utils as procutils

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
import utils

_COPY_DIR = 'from_host'
_PROCESS_SCRIPT = 'process.py'
_MODIFY_POM_SCRIPT = 'modify_pom.py'
_POST_RUN_SCRIPT = 'post_run.py'


class AnnotationRunner():
    def __init__(self, is_file, image_tags_file, annotation, workers = 1):
        if is_file:
            with open(image_tags_file) as f:
                image_tags = list(map(str.strip, f.readlines()))
        else:
            image_tags = [image_tags_file]
        if not image_tags:
            raise ValueError
        if not annotation:
            raise ValueError
        if workers <= 0:
            raise ValueError
        self._image_tags = list(image_tags)
        self._annotation = annotation
        self._num_workers = min(workers, len(self._image_tags))

    def run(self):
        with ThreadPoolExecutor(max_workers=self._num_workers) as executor:
            future_to_image_tag = {executor.submit(self._thread_main, image_tag): image_tag for image_tag in self._image_tags}

        attempted = 0
        succeeded = 0
        errored = 0
        for future in as_completed(future_to_image_tag):
            attempted += 1
            try:
                data = future.result()
                if data:
                    cmd = 'docker commit {} datomassi/bugswarm-annotated:{} && docker push datomassi/bugswarm-annotated:{}'.format(future_to_image_tag[future], future_to_image_tag[future], future_to_image_tag[future])
                    _, stdout, stderr, ok = utils.run_command(cmd)
                    succeeded += 1
                    if not ok:
                        print(stdout)
                        print(stderr)
                else:
                    errored += 1
            except Exception as e:
                log.error(e)
                errored += 1


    def process_artifact(self, image_tag):
        return self._run_artifact(image_tag, self._get_command(image_tag, self._annotation))

    def _thread_main(self, image_tag: str):
        return self.process_artifact(image_tag)

    @staticmethod
    def _get_command(image_tag, annoation):
        return """export JAVA_HOME=/usr/lib/jvm/java-8-oracle/jre
            export PATH=$JAVA_HOME/bin:$PATH
            python /from_host/{process_py} /from_host/{modify_pom_py}
            bash /from_host/annotation_adder.sh {annoation}""".format(**{
            'image_tag': image_tag,

            'container_sandbox': procutils.CONTAINER_SANDBOX,
            'host_sandbox': procutils.HOST_SANDBOX,

            'process_py': _PROCESS_SCRIPT,
            'modify_pom_py': _MODIFY_POM_SCRIPT,
            'annoation': annoation
        })

    @staticmethod
    def run_artifact(image_tag, cmd):
        if not image_tag:
            raise ValueError
        c = cmd.split('\n')
        x = [x.strip() for x in c]
        cmd = ' && '.join(x)
        command = 'docker run --name {} -v $PWD/from_host:/from_host bugswarm/images:{} /bin/bash -lc "{}"'.format(image_tag, image_tag, cmd)
        print(command)
        process, stdout, stderr, ok = utils.run_command(command)
        print(process, stdout, stderr, ok)
        return process, stdout, stderr, ok


def _print_usage():
    log.info('Usage: python3 main.py <image_tags_file>')
    log.info('image_tags_file: Path to a file containing a newline-separated list of image tags to process.')


def _validate_input(argv):
    if len(argv) != 3:
      _print_usage()
      sys.exit(1)
    is_file = argv[1] == 'True'
    image_tags_file = argv[2]
    if is_file and not os.path.isfile(image_tags_file):
        log.error('The image_tags_file argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)
    return is_file, image_tags_file


def main(argv=None):
    argv = argv or sys.argv

    is_file, image_tags_file = _validate_input(argv)

    t_start = time.time()
    AnnotationRunner(is_file, image_tags_file, workers=1).run()
    t_end = time.time()
    print('Running AnnotationRunner took {}s'.format(t_end-t_start))


if __name__ == '__main__':
    sys.exit(main())
