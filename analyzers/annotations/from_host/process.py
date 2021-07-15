"""
This script performs the following steps when run inside an artifact container:
  1. Modify a Maven project's POM to include the SpotBugs plugin.
  2. Generate SpotBugs reports by invoking the Maven build for the project.
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

    modify_pom_script, annotation = _validate_input(argv)

    # Install dependencies for modifying the POM.
    _pip_install('beautifulsoup4')
    _pip_install('lxml')

    # Modify the POM.
    modify_command = 'python {}'.format(modify_pom_script)
    _, stdout, stderr, ok = _run_command(modify_command)
    if not ok:
        _print_error('Failed to modify the POMs. Exiting.', stdout, stderr)
        sys.exit(1)
    else:
        print('Modified the POMs.')


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
    print('Usage: python process.py <modify_pom_script>')


def _validate_input(argv):
    if len(argv) != 2:
        _print_usage()
        sys.exit(1)
    modify_pom_script = argv[1]
    return modify_pom_script


if __name__ == '__main__':
    sys.exit(main())
