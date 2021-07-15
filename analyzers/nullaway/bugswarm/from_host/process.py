"""
This script performs the following steps when run inside an artifact container:
  1. Modify a Maven project's POM to include the Error-Prone plugin.
  2. Generate Error-Prone reports by invoking the Maven build for the project.
  3. Copy the reports to the container-side sandbox to make them available from the host.

Requirements:
  1. This script if run with Python 2.x.
  2. This script is run inside an artifact container.
  3. This script is run from inside either the failed or passed repositories in the artifact container.
  4. The Python script that modifies the POM is in the same directory as this script.

"""

import os
import shutil
import subprocess
import sys


def main(argv=None):
    argv = argv or sys.argv

    image_tag, container_sandbox, modify_pom_script, f_or_p = _validate_input(argv)
    OUTPUT_FILENAME = 'error-prone-out.txt'
    JAVA_FILES_FILENAME = 'java.files'

    # Update pip
    _update_pip()

    # Install dependencies for modifying the POM.
    _pip_install('bs4')
    _pip_install('lxml')

    # Modify the POM.
    modify_command = 'python {} pom.xml'.format(modify_pom_script)
    _, stdout, stderr, ok = _run_command(modify_command)
    if not ok:
        _print_error('Failed to modify the POM. Exiting.', stdout, stderr)
        sys.exit(1)
    else:
        print('Modified the POM.')

    # Generate Error-Prone reports.
    mvn_command = '{} clean compile -fn -DskipTests >> {} 2>&1'.format(_get_maven_binary_path(), OUTPUT_FILENAME)
    _, stdout, stderr, _ = _run_command(mvn_command)
    # We cannot use the return code to determine success since the Maven command should always fail for failed jobs and
    # always pass for passed jobs. Instead, we check stderr as a proxy.
    print('Attempted to generate Error-Prone reports.')
    print('stdout:\n{}'.format(stdout))
    print('stderr:\n{}'.format(stderr))

    reports_destination = os.path.join(container_sandbox, image_tag, f_or_p)
    _copy_reports_to_sandbox(reports_destination)


def _get_java_files(java_files):
    _, stdout, stderr, ok = _run_command('find . -name *.java')
    if not ok:
        _print_error('Error getting java files', stdout, stderr)
    with open(java_files, 'w+') as file:
        file.write(stdout)
    return ok, stdout, stderr


def _update_pip():
    # Install pip with apt-get
    command = 'sudo apt-get -y update'
    _, stdout, stderr, ok = _run_command(command)

    # Update pip with apt-get
    command = 'sudo apt-get -y upgrade python-pip'
    _, stdout, stderr, ok = _run_command(command)


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


def _copy_reports_to_sandbox(partial_destination):
    """
    Copy Error-Prone reports to the container-side sandbox. If needed, the destination directory is created in the
    container in the following format:
    <host-side sandbox>/<image_tag>/<'failed' or 'passed'>/<path to the original report, relative to repo_dir>

    Starts the recursive search for reports from the current directory.
    :param partial_destination: The destination without the path to the original report,
                                relative to the repository directory.
    """

    topdir = '.'
    for currentdir, subdirs, files in os.walk(topdir):
        for f in files:
            if f == 'error-prone-out.txt':
                src = os.path.join(currentdir, f)
                relative_path_to_file = os.path.relpath(os.path.join(currentdir, f), topdir)
                dst = os.path.join(partial_destination, relative_path_to_file)
                # Make any needed directories.
                _py2_makedirs(dst)
                print('Copying {} to {}.'.format(src, dst))
                shutil.copy(src, dst)


def _py2_makedirs(path):
    """
    Python 2 os.makedirs workaround that behaves similar to Python 3's os.makedirs with exist_ok=True.
    Removes the leaf part of the path before creating directories.
    """
    path, _ = os.path.split(path)
    command = 'mkdir -p {}'.format(path)
    _run_command(command)


def _get_maven_binary_path():
    """
    :return: The path to the Maven binary in the container.
    """
    command = 'find / -name mvn 2> /dev/null | sed -n 1p'
    _, stdout, stderr, ok = _run_command(command)
    first_line = stdout.splitlines()[0]
    if not ok:
        _print_error('Failed to get path to Maven binary. Exiting.', stdout, stderr)
        sys.exit(1)
    else:
        print('Got path to Maven binary: {}'.format(first_line))
    return first_line


def _pip_install(package):
    command = 'sudo pip install {}'.format(package)
    _, stdout, stderr, ok = _run_command(command)
    if not ok:
        _print_error('Failed to install {} with pip. Exiting.'.format(package), stdout, stderr)
        sys.exit(1)
    else:
        print('Installed {}.'.format(package))
    return ok


def _print_usage():
    print('Usage: python process.py <image_tag> <container_sandbox> <repo_dir> <modify_pom_script>')
    print('repo_dir: The directory containing the actual failed or passed repository.')


def _validate_input(argv):
    if len(argv) != 5:
        _print_usage()
        sys.exit(1)
    image_tag = argv[1]
    container_sandbox = argv[2]
    modify_pom_script = argv[3]
    f_or_p = argv[4]
    # Test the container sandbox, but not the host sandbox, argument since this script is run inside a container and
    # therefore cannot verify the host sandbox argument.
    if not os.path.isdir(container_sandbox):
        print('The container_sandbox argument ({}) is not a directory or does not exist. Exiting.'
              .format(container_sandbox))
        _print_usage()
        sys.exit(1)
    if f_or_p not in ['failed', 'passed']:
        print('The f_or_p argument must be either "failed" or "passed". Exiting.')
        _print_usage()
        sys.exit(1)
    return image_tag, container_sandbox, modify_pom_script, f_or_p


if __name__ == '__main__':
    sys.exit(main())
