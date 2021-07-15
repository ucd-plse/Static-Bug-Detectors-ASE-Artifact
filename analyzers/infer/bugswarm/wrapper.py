import inspect
import os
import subprocess
import sys
import time

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from distutils.dir_util import copy_tree
from multiprocessing import Pool
from multiprocessing import Queue
from multiprocessing import Process
from typing import Callable
from typing import List

from bugswarm.common.artifact_processing import utils as procutils

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
import utils


def _print_usage():
    print('Usage: python3 main.py <image_tags_file> <dockerhub-repo> <number-of-processes>')
    print('image_tags_file: Path to a file containing a newline-separated list of image tags to process.')
    print('dockerhub-repo: Dockerhub repo slug, e.g. bugswarm/images')
    print('number-of-processes: Number of processes')


def _validate_input(argv):
    if len(argv) != 4:
        _print_usage()
        sys.exit()
    image_tags_file = argv[1]
    dockerhub_repo = argv[2]
    num_processes = int(argv[3])
    if not os.path.isfile(image_tags_file):
        print('The image_tags_file argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)
    if num_processes <= 0:
        print('The number of processes needs to be greater than 0. Exiting.')
        _print_usage()
        sys.exit(1)
    return image_tags_file, dockerhub_repo, num_processes


def _thread_main(image_tag: str, f_or_p: str, dockerhub_repo: str):
    return utils.run_command('python3 main.py tmp/{}-{}.txt {} {}'.format(image_tag, f_or_p, f_or_p, dockerhub_repo))


def main(argv=None):
    argv = argv or sys.argv
    image_tags_file, dockerhub_repo, num_processes = _validate_input(argv)

    t_start = time.time()
    utils.run_command('mkdir tmp')

    with open(image_tags_file) as f:
        image_tags = list([x.strip() for x in f.readlines()])
    for image_tag in image_tags:
        for f_or_p in ['failed', 'passed']:
            with open('tmp/{}-{}.txt'.format(image_tag, f_or_p), 'w+') as tmp_f:
                tmp_f.write('{}\n'.format(image_tag))

    with Pool(min(len(image_tags) * 2, num_processes)) as pool:
        q = Queue()
        for image_tag in image_tags:
            for f_or_p in ['failed', 'passed']:
                q.put((image_tag, f_or_p, dockerhub_repo))
        multiple_results = [pool.apply_async(_thread_main, (k[0], k[1], k[2],)) for k in [q.get() for i in range(q.qsize())]]
        print([res.get(timeout=360) for res in multiple_results])

    # with ThreadPoolExecutor(max_workers=4) as executor:
    #     for f_or_p in ['failed', 'passed']:
    #         future_to_image_tag = {executor.submit(_thread_main, '{}-{}'.format(image_tag, f_or_p), f_or_p, dockerhub_repo): image_tag
    #                                for image_tag in image_tags}
    # attempted = 0
    # succeeded = 0
    # errored = 0
    # for future in as_completed(future_to_image_tag):
    #     attempted += 1
    #     try:
    #         data = future.result()
    #         if data:
    #             succeeded += 1
    #         else:
    #             errored += 1
    #     except Exception as e:
    #         print(e)
    #         errored += 1
    # Clean up
    utils.run_command('rm -rf tmp')
    utils.run_command('docker rm $(docker ps -aq)')

    t_end = time.time()
    # print('attempted: {}, succeeded: {}, errored: {}'.format(attempted, succeeded, errored))
    print('Running InferWrapper took {}s'.format(t_end-t_start))


if __name__ == '__main__':
    sys.exit(main())
