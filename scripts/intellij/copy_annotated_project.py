import os
import subprocess
import sys

_BUGSWARM_DOCKER_REPO = 'bugswarm/images'
_DOCKER_REPO = 'datomassi/bugswarm-intellij-annotated'
_DIRECTORIES = ['failed', 'passed']


def main(argv=None):
    argv = argv or sys.argv
    image_tag, working_dir = _validate_input(argv)

    bs_docker_repo_image = '{}:{}'.format(_BUGSWARM_DOCKER_REPO, image_tag)
    an_docker_repo_image = '{}:{}'.format(_DOCKER_REPO, image_tag)

    # Docker create.
    print('Creating container.')
    docker_create_cmd = 'docker create -it --name {} {} /bin/bash'.format(image_tag, bs_docker_repo_image)
    _, stdout, stderr, ok = _run_command(docker_create_cmd)
    if not ok:
        _print_error('Error creating docker container.', stdout=stdout, stderr=stderr)
        sys.exit(1)

    # Docker cp.
    print('Copying files into container.')
    for f_or_p in _DIRECTORIES:
        docker_cp_cmd = 'docker cp {}/{} {}:/home/travis/build/ '.format(working_dir, f_or_p, image_tag, f_or_p)
        _, stdout, stderr, ok = _run_command(docker_cp_cmd)
        if not ok:
            _print_error('Error copying files to container.', stdout=stdout, stderr=stderr)
            sys.exit(1)

    # Docker commit.
    print('Commiting container.')
    docker_commit_cmd = 'docker commit {} {}'.format(image_tag, an_docker_repo_image)
    _, stdout, stderr, ok = _run_command(docker_commit_cmd)
    if not ok:
        _print_error('Error commiting container.', stdout=stdout, stderr=stderr)
        sys.exit(1)

    # Docker push.
    print('Pushing image.')
    docker_push_cmd = 'docker push {}'.format(an_docker_repo_image)
    _, stdout, stderr, ok = _run_command(docker_push_cmd)
    if not ok:
        _print_error('Error pushing image.', stdout=stdout, stderr=stderr)
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
