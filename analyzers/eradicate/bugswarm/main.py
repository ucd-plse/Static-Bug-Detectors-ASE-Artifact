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

_SOURCE_DIR = '/home/travis/build'
_SANDBOX_DIR = '/bugswarm-sandbox'

HOST_SANDBOX = abspath('../../results/eradicate-proj-reports')

class EradicateRunner(ParallelArtifactRunner):
    def __init__(self, f_or_p, image_tags_file, workers = 1):
        """
        :param image_tags_file: Path to a file containing a newline-separated list of image tags.
        :param copy_dir: A directory to copy into the host-side sandbox before any artifacts are processed.
        :param command: A callable used to determine what command(s) to execute in each artifact container. `command` is
                        called once for each processed artifact. The only parameter is the image tag of the artifact
                        about to be processed.
        :param workers: The same as for the superclass initializer.
        """
        self.image_tags = image_tags_file
        self.f_or_p = f_or_p
        super().__init__(self.image_tags, workers)


    def process_artifact(self, image_tag):
        return self.run_eradicate(image_tag, self._get_command(image_tag, self.f_or_p))

    @staticmethod
    def _get_command(image_tag, f_or_p):
        command = """export JAVA_HOME=/usr/lib/jvm/jdk1.8.0_221/jre
           export JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF8
           cd {source_dir}/{f_or_p}/*/*/
           mvn clean install -U -DskipTests -Denforcer.skip=true -Dcheckstyle.skip -Dcobertura.skip -Dbaseline.skip=true
           /infer/infer/bin/infer --keep-going --eradicate -- mvn clean test-compile compile -DskipTests -Denforcer.skip=true -Dcobertura.skip -Dcheckstyle.skip -Dbaseline.skip=true
           mkdir -p {container_sandbox}/{image_tag}/{f_or_p}
           cp -R infer-out/report.json {container_sandbox}/{image_tag}/{f_or_p}""".format(**{
           'source_dir': _SOURCE_DIR,
           'image_tag': image_tag,
           'container_sandbox': _SANDBOX_DIR,
           'f_or_p': f_or_p,
        })
        return '/bin/bash -lc "{}"'.format(command)

    @staticmethod
    def run_eradicate(container_name, cmds):
        if not container_name:
            raise ValueError

        c = cmds.split('\n')
        x = [x.strip() for x in c]
        cmd = ' && '.join(x)
        command = 'docker run --rm -v {}:{} ' \
        '--volumes-from {} datomassi/images:infer-jdk8 {}'.format(HOST_SANDBOX,
                                            procutils.CONTAINER_SANDBOX,
                                            container_name, cmd)
        process, stdout, stderr, ok = utils.run_command(command)
        return process, stdout, stderr, ok


class ImageTagRunner(ParallelArtifactRunner):
    def __init__(self, image_tags_file, dockerhub_repo, workers = 1):
        self.image_tags = image_tags_file
        self.dockerhub_repo = dockerhub_repo
        super().__init__(self.image_tags, workers)

    @staticmethod
    def _get_command():
        return '/bin/bash -c "while true; do echo \'Hit CTRL+C\' > /dev/null; sleep 1; done"'

    def process_artifact(self, image_tag):
        return self.run_artifact(image_tag, self._get_command(), self.dockerhub_repo)

    @staticmethod
    def run_artifact(image_tag, cmd, dockerhub_repo):
        if not image_tag:
            raise ValueError

        command = 'docker run --name {} ' \
        '-v /home/travis/build/ {}:{} {}'.format(image_tag, dockerhub_repo, image_tag, cmd)
        process, stdout, stderr, ok = utils.run_command(command)
        return process, stdout, stderr, ok


def _print_usage():
    print('Usage: python3 main.py <image_tags_file> <failed_or_passed>')
    print('image_tags_file: Path to a file containing a newline-separated list of image tags to process.')


def _validate_input(argv):
    image_tags_file = argv[1]
    f_or_p = argv[2]
    dockerhub_repo = argv[3]
    if not os.path.isfile(image_tags_file):
        print('The image_tags_file argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)
    if f_or_p not in ['failed', 'passed']:
        print('f_or_p argument needs to be either "failed" or "passed"')
        _print_usage()
        sys.exit(1)
    return image_tags_file, f_or_p, dockerhub_repo


def main(argv=None):
    argv = argv or sys.argv

    image_tags_file, f_or_p, dockerhub_repo = _validate_input(argv)

    t_start = time.time()
    with open(image_tags_file) as file:
        for line in file:
            line = line.strip()

            with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
                ti_start = time.time()
                im = ImageTagRunner([line], dockerhub_repo, workers=1)
                inf = EradicateRunner(f_or_p, [line], workers=1)
                f = executor.submit(im.run)

                while not f.running():
                    pass

                # Wait until container is running
                print('job for {} is running'.format(line))
                res = False
                while not res:
                    res = utils.container_running(line)
                print('submitting job for {}'.format(line))
                time.sleep(15)
                f1 = executor.submit(inf.run)
                time.sleep(10)
                while f1.running():
                    pass
                # Stop artifact container
                utils.run_command('docker stop {}'.format(line))
                ti_end = time.time()
                print('Done. {}'.format(ti_end-ti_start))
                continue

    t_end = time.time()
    print('Running Eradicate took {}s'.format(t_end-t_start))


if __name__ == '__main__':
    sys.exit(main())
