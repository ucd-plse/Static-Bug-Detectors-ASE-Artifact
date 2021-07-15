import os
import subprocess
import sys

_DOCKER_REPO = 'bugswarm/images'
_DIRECTORIES = ['failed', 'passed']


def main(argv=None):
    argv = argv or sys.argv
    image_tag, working_dir = _validate_input(argv)

    docker_repo_image = '{}:{}'.format(_DOCKER_REPO, image_tag)

    # Check to see if failed/ or passed/ exist in working directory.
    # Remove if they do.
    ls_cmd = 'ls {}'.format(working_dir)
    _, stdout, _, _ = _run_command(ls_cmd)
    dir_contents = stdout.split('\n')
    for f_or_p in _DIRECTORIES:
        rm_cmd = 'rm -rf {}/{}'.format(working_dir, f_or_p)
        if f_or_p in dir_contents:
            print('Removing {}/{}.'.format(working_dir, f_or_p))
            _, stdout, stderr, ok = _run_command(rm_cmd)
            if not ok:
                _print_error('Error removing {}/{}.'.format(working_dir, f_or_p), stdout=stdout, stderr=stderr)
                sys.exit(1)

    # Pulling Docker image.
    print('Pulling {}.'.format(docker_repo_image))
    docker_pull_cmd = 'docker pull {}'.format(docker_repo_image)
    _, stdout, stderr, ok = _run_command(docker_pull_cmd)
    if not ok:
        _print_error('Error pulling {}'.format(docker_repo_image), stdout=stdout, stderr=stderr)
        sys.exit(1)

    # Copying 'failed' and 'passed' directories from container.
    print('Copying directories.')
    docker_create_cmd = 'docker create -it --name {} {} /bin/bash'.format(image_tag, docker_repo_image)
    _, stdout, stderr, ok = _run_command(docker_create_cmd)
    if not ok:
        _print_error('Error creating docker container.', stdout=stdout, stderr=stderr)
        sys.exit(1)
    for f_or_p in _DIRECTORIES:
        docker_cp_cmd = 'docker cp {}:/home/travis/build/{} {}'.format(image_tag, f_or_p, working_dir)
        _, stdout, stderr, ok = _run_command(docker_cp_cmd)
        if not ok:
            _print_error('Error copying files from container.', stdout=stdout, stderr=stderr)
            sys.exit(1)

    # Remove container
    docker_rm_cmd = 'docker rm -f {}'.format(image_tag)
    _, _, _, _ = _run_command(docker_rm_cmd)


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
    print('Usage: python3 copy_project_repos.py <image_tag> <working_directory>')
    print('image_tag: Image tag of artifact.')
    print('working_directory: Directory where files will be copied.')


def _validate_input(argv):
    if len(argv) != 3:
        _print_usage()
        sys.exit(1)
    image_tag = argv[1]
    working_dir = argv[2]

    if not os.path.isdir(working_dir) and os.path.exists(working_dir):
        print('The working_dir argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)

    return image_tag, working_dir


if __name__ == '__main__':
    sys.exit(main())
