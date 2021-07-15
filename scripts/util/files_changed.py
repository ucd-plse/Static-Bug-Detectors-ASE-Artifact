"""
This script will check to see if all the files that were changed in the diff are analyzed by SpotBugs.
"""

import lxml
import os
import subprocess
import sys

from bs4 import BeautifulSoup

from bugswarm.common import github_wrapper
from bugswarm.common import log
from bugswarm.common.rest_api.database_api import DatabaseAPI
from bugswarm.private.credentials import DATABASE_PIPELINE_TOKEN
from bugswarm.private.credentials import GITHUB_TOKENS


def main(argv=None):
    if argv is None:
        argv = sys.argv

    image_tags_file = _validate_input(argv)

    gh_wrapper = github_wrapper.GitHubWrapper(GITHUB_TOKENS)

    # For each image_tag run _process_image_tag()
    with open(image_tags_file) as file:
        content = file.readlines()
        for l in content:
            image_tag, reports_directory = [x.strip() for x in l.split(',')]
            print('Processing {}'.format(image_tag))
            r_val = _process_image_tag(image_tag, gh_wrapper, reports_directory)
            if r_val:
                print('Files that were changed were not analyzed.')
            print('Done processing {}'.format(image_tag))

    print('Done processing all image-tags')
    

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
    print('Usage: python3 changes.py <image-tags-and-report-dir-file>')
    print('Example format: <image-tag>,<filepath-to-report-dir>')



def _validate_input(argv):
    image_tags_file = argv[1]

    if not os.path.isfile(image_tags_file):
        log.error('The image_tags_file argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)

    return image_tags_file


def _get_files_changed(repo_owner, repo, sha_fail, sha_pass, gh_wrapper):
    """
    repo_owner: Name of repo owner on GitHub
    repo: Name of repo on GitHub
    sha_fail: SHA of failing commit from the artifact
    sha_pass: SHA of passing commit from the artifact
    gh_wrapper: GitHub wrapper object

    Gets the files that were changed in the GitHub diff of the failing and passing commit

    :return: List of files that were changed in the GitHub diff
    """

    url = 'https://api.github.com/repos/{}/{}/compare/{}...{}'.format(repo_owner, repo, sha_fail, sha_pass)

    # Try to make github api request
    response, response_json = gh_wrapper.get(url)

    if response is None or response_json is None:
        return None

    # Create list of files that were changed
    files_changed = [f['filename'] for f in response_json['files']]
    pruned_files_changed = []
    
    # Prune files that are not Java files
    for file in files_changed:
        ext = file.split('.')[len(file.split('.'))-1].strip()
        if ext != 'java':
            continue
        pruned_files_changed.append(file)

    return pruned_files_changed


def _get_files_analyzed(reports_directory):
    """
    reports_directory: Filepath to the directory containing the failing reports

    Parses the spotbugsXml.xml file and gets the files that were analyzed

    :return: List of files that were analyzed
    """

    cmd = 'find {} -name "spotbugsXml.xml"'.format(reports_directory)
    _, stdout, stderr, ok = _run_command(cmd)
    if not ok:
        _print_error('Attempting to get list of spotbugs reports', stdout, stderr)
        return None
    reports = [x.strip() for x in stdout.split('\n')]
    files_analyzed = []
    for report in reports:
        soup = BeautifulSoup(open(report), 'lxml-xml')
        file_stats = soup.find_all('FileStats')
        for file in file_stats:
            files_analyzed.append((file.get('path')))

    return files_analyzed


def _process_image_tag(image_tag, gh_wrapper, reports_directory):
    """
    image_tag: The image tag of the artifact being processed
    gh_wrapper: GitHub wrapper object
    reports_directory: Filepath to the directory containing the failing reports

    Wrapper for _get_files_changed and _get_files_analyzed.
    Checks to if any files that are returned from _get_files_analyzed are not
    in the files returned in _get_files_analyzed.

    :return: True if files that were changed were not analyzed. False otherwise.
    """

    sha = {}

    # Get artifact from DB
    bugswarmapi = DatabaseAPI(token=DATABASE_PIPELINE_TOKEN)
    artifact = bugswarmapi.find_artifact(image_tag).json()

    # Get SHAs
    sha['failed'] = artifact['failed_job']['trigger_sha']
    sha['passed'] = artifact['passed_job']['trigger_sha']

    # Get repo_owner and rep
    repo_owner = artifact['repo'].split('/')[0]
    repo = artifact['repo'].split('/')[1]

    # Getting number of additions,etc to push into db
    files_changed = _get_files_changed(repo_owner, repo, sha['failed'], sha['passed'], gh_wrapper)
    if files_changed is None:
        print('files_changed is None')
        return None

    files_analyzed = _get_files_analyzed(reports_directory)
    if files_analyzed is None:
        print('files_analyzed is None')
        return None

    # Initalize dict with False
    files_changed_dict = {}
    for file in files_changed:
        files_changed_dict[str(file)] = False

    # Check to see if files that were changed, were indeed analyzed
    for file_changed in files_changed:
        for file_analyzed in files_analyzed:
            if file_analyzed in file_changed:
                files_changed_dict[str(file_changed)] = True
                break

    # See if any files were not analyzed
    file_not_analyzed = False
    for file in files_changed:
        if files_changed_dict[str(file)] == False:
            print('{} was not analyzed.'.format(file))
            file_not_analyzed = True

    return file_not_analyzed


if __name__ == '__main__':
    sys.exit(main())
