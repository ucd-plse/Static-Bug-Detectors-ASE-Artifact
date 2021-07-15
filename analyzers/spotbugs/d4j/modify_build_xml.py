import os
import re
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

from bs4 import BeautifulSoup

def _run_command(command: str):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    stdout = stdout.decode('utf-8').strip()
    stderr = stderr.decode('utf-8').strip()
    ok = process.returncode == 0
    return process, stdout, stderr, ok


def create_tag(name: str, attrs={}):
    tmp_soup = BeautifulSoup('', 'lxml-xml')
    tag = tmp_soup.new_tag(name)
    for attr in attrs:
        tag[attr] = attrs[attr]
    return tag


def create_taskdef_tag(jar_path: str):
    return create_tag('taskdef', {'resource': 'edu/umd/cs/findbugs/anttask/tasks.properties',
                                  'classpath': SCRIPT_DIR + '/' + jar_path}
                     )


def create_property_tag(source_path: str):
    return create_tag('property', {'name': 'spotbugs.home',
                                   'value': SCRIPT_DIR + '/' + source_path})


def get_jar_target_tag(soup):
    jar_target_tag = soup.find_all(attrs={'name': 'jar'})[0]
    if jar_target_tag is None:
        jar_target_tag = soup.find_all(attrs={'name': 'all-classes-jar'})[0]
    return jar_target_tag


def get_jar_location(soup):
    jar_target_tag = get_jar_target_tag(soup)
    if jar_target_tag.jar.has_attr('jarfile'):
        jar_name = jar_target_tag.jar['jarfile']
    else:
        jar_name = jar_target_tag.jar['destfile']
    return jar_name


def get_sourcepath_location(working_dir: str):
    D4J = '../../defects4j/framework/bin/defects4j'
    cmd = D4J + ' export -p dir.src.classes -w ' + working_dir
    _, stdout, stderr, _ = _run_command(cmd)
    return stdout.strip()


def create_target_tag(soup, working_dir, report_level):
    # Create sourcePath tag
    sourcepath_tag = create_tag('sourcePath', {'path': get_sourcepath_location(working_dir)})
    # Create class tag
    class_tag = create_tag('class', {'location': get_jar_location(soup)})
    # Create spotbugs tag
    spotbugs_tag = create_tag('spotbugs', {'home': '${spotbugs.home}',
                                           'effort': 'max',
                                           'reportLevel': report_level,
                                           'output':'xml', 
                                           'outputFile': 'spotbugsXml.xml'})
    # Append sourcePath and class tags to spotbugs
    spotbugs_tag.append(sourcepath_tag)
    spotbugs_tag.append(class_tag)
    # Create target tag
    target_tag = create_tag('target', {'name': 'spotbugs',
                                       'depends': 'jar'})
    # Append spotbugs tag to target
    target_tag.append(spotbugs_tag)
    return target_tag

def _validate_input(argv):
    if len(argv) != 3:
        print('Not enough arguments.')
        sys.exit(1)       
    build_xml_fp = argv[1]
    if not os.path.isfile(build_xml_fp):
        print('build_xml_fp DNE')
        sys.exit(1)
    report_level = argv[2]
    return build_xml_fp, report_level


def modify_build_xml(build_xml_fp, report_level):
    soup = BeautifulSoup(open(build_xml_fp), 'lxml-xml')
    jar_target_tag = get_jar_target_tag(soup)
    if 'test' in jar_target_tag['depends']:
        depends_on = re.sub(r',?test,?', '', jar_target_tag['depends'])
        jar_target_tag['depends'] = depends_on
    soup.project.append(create_taskdef_tag('spotbugs-ant-3.1.6.jar'))
    soup.project.append(create_property_tag('spotbugs-3.1.6'))
    working_dir = '/'.join(build_xml_fp.split('/')[:-1])
    soup.project.append(create_target_tag(soup, working_dir, report_level))
    with open('{}'.format(build_xml_fp), 'wb') as f:
        f.write(soup.prettify().encode('utf-8'))


def main(argv=None):
    if argv is None:
        argv = sys.argv
    
    # Read in the build.xml file and open it with BS.
    build_xml_fp, report_level = _validate_input(argv)
    
    # Modify build.xml and write updated back.
    modify_build_xml(build_xml_fp, report_level)


if __name__ == '__main__':
    sys.exit(main())


