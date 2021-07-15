import os
import subprocess
import sys

from bs4 import BeautifulSoup

def _run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    stdout = stdout.decode('utf-8').strip()
    stderr = stderr.decode('utf-8').strip()
    ok = process.returncode == 0
    return process, stdout, stderr, ok

_FAILED_DIR = '/home/travis/build/failed/*/*/'
_PASSED_DIR = '/home/travis/build/passed/*/*/'

_, failed_poms_fp_list, _, _ = _run_command('find {} -name pom.xml'.format(_FAILED_DIR))
_, passed_poms_fp_list, _, _ = _run_command('find {} -name pom.xml'.format(_PASSED_DIR))

failed_poms_fp_list_strip = [fp.encode('ascii').strip() for fp in failed_poms_fp_list.split('\n')]
passed_poms_fp_list_strip = [fp.encode('ascii').strip() for fp in passed_poms_fp_list.split('\n')]

for pom_list in [failed_poms_fp_list_strip, passed_poms_fp_list_strip]:
    for pom in pom_list:
        soup = BeautifulSoup(open(pom), 'lxml-xml')
        if soup.project is None:
            continue
        plugins = soup.project.find_all('plugin')
        for plugin in plugins:
            if 'maven-enforcer-plugin' == plugin.artifactId.string.strip():
                plugin.decompose()

        if soup.project.find('dependencies') is None:
            soup.project.append(soup.new_tag('dependencies'))

        dependency_xml = """
        <dependency>
            <groupId>com.google.code.findbugs</groupId>
            <artifactId>jsr305</artifactId>
            <version>3.0.2</version>
        </dependency>
        """
        soup.dependencies.insert(0, BeautifulSoup(dependency_xml, 'lxml-xml'))

        with open(pom, 'w') as f:
            f.write(soup.prettify().encode('utf-8'))
