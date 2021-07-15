import os
import subprocess
import sys
import time

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from typing import Callable
from typing import List

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
import utils

def _print_usage():
    print('Usage: python3 main.py <image-tags-file> <annotation>')
    print('image_tags_file: Path to a file containing a newline-separated list of image tags to process.')
    print('annotation: Which annotation will be added. Either checkfornull or nullable')


def _validate_input(argv):
    if len(argv) != 3:
      _print_usage()
      sys.exit(1)
    image_tags_file = argv[1]
    annotation = argv[2]
    if not os.path.isfile(image_tags_file):
        print('The image_tags_file argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)
    if annotation not in ['checkfornull', 'nullable']:
        print('The annotation arguement is not recognized. Exiting.')
        _print_usage()
        sys.exit(1)
    return image_tags_file, annotation


def main(argv=None):
    argv = argv or sys.argv

    image_tags_file, annotation = _validate_input(argv)
    image_tags = list()
    with open(image_tags_file) as f:
        image_tags = list([x.strip() for x in f.readlines()])
    t_start = time.time()
    for image_tag in image_tags:
        print(utils.run_command('python3 main.py False {} {}'.format(image_tag, annotation)))
    t_end = time.time()
    print('Running AnnotationRunner took {}s'.format(t_end-t_start))


if __name__ == '__main__':
    sys.exit(main())
