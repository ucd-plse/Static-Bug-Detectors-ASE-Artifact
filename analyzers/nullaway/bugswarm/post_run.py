import os
import sys


def main(argv=None):
    argv = argv or sys.argv

    host_sandbox, repo_base_dir = _validate_input(argv)

    # If the repository base directory is '/home/travis/build', then the unwanted prefix is 'home-travis-build-'.
    unwanted_prefix = repo_base_dir.strip('/').replace('/', '-') + '-'

    # First, clean up the XML filenames in the sandbox on the host side.
    for filename in os.listdir(host_sandbox):
        if _should_ignore_filename(host_sandbox, filename) or not filename.startswith(unwanted_prefix):
            continue
        fixed_filename = filename[len(unwanted_prefix):]
        if filename.startswith(unwanted_prefix):
            full_src = os.path.join(host_sandbox, filename)
            full_dst = os.path.join(host_sandbox, fixed_filename)
            print('Renaming {} to {}'.format(filename, fixed_filename))
            os.rename(full_src, full_dst)

    # Now, group the XML files into directories based on status.
    for filename in os.listdir(host_sandbox):
        if _should_ignore_filename(host_sandbox, filename):
            continue
        status, tail_filename = filename.split('-', 1)
        full_src = os.path.join(host_sandbox, filename)
        full_dst = os.path.join(host_sandbox, status, tail_filename)
        print('Moving {} to {} directory'.format(filename, status))
        # Intentionally use renames() for its directory creation functionality.
        os.renames(full_src, full_dst)


def _should_ignore_filename(host_sandbox, filename):
    return not (os.path.isfile(os.path.join(host_sandbox, filename)) and filename.endswith('.xml'))


def _print_usage():
    print('Usage: python3 post_run.py <host_sandbox> <repo_base_dir>')
    print('host_sandbox: The path to the sandbox on the host side.')
    print('repo_base_dir: The absolute path to the directory containing repositories in the artifact.')


def _validate_input(argv):
    if len(argv) != 3:
        _print_usage()
        sys.exit(1)
    host_sandbox = argv[1]
    repo_base_dir = argv[2]
    if not os.path.isdir(host_sandbox):
        print(host_sandbox)
        print('The host_sandbox argument is not a directory or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)
    return host_sandbox, repo_base_dir


if __name__ == '__main__':
    sys.exit(main())
