import os
import sys

from bs4 import BeautifulSoup

TAG_CREATION_FUNCS = ['create_property_tag', 'create_taskdef_tag',
                      'create_with_clover_tag', 'create_clover_xml_tag',
                      'create_test_check_tag', 'create_test_method_tag']

def create_property_tag():
    return create_tag('property', {'name': 'clover.jar', 'location': '/home/dtomassi/clover-ant/clover-ant-4.2.1/lib/clover.jar'})


def create_taskdef_tag():
    return create_tag('taskdef', {'resource': 'cloverlib.xml', 'classpath': '${clover.jar}'})


def create_with_clover_tag():
    with_clover_target_tag = create_tag('target', {'name': 'with.clover'})
    with_clover_target_tag.append(create_tag('clover-setup'))
    return with_clover_target_tag


def create_clover_xml_tag():
    with_clover_target_tag = create_tag('target', {'name': 'clover.xml'})
    clover_report_tag = create_tag('clover-report')
    current_tag = create_tag('current', {'outfile': 'coverage.xml', 'includeFailedTestCoverage': 'true'})
    current_tag.append(create_tag('format', {'type': 'xml'}))
    clover_report_tag.append(current_tag)
    with_clover_target_tag.append(clover_report_tag)
    return with_clover_target_tag


def create_pathelement_tag():
    return create_tag('pathelement', {'path': '${clover.jar}'})


def add_tags(s):
    for tag_func in [globals()[func] for func in TAG_CREATION_FUNCS]:
        s.project.append(tag_func())


# def add_pathelement_tag(s):
#     junit = soup.project.find('junit')
#     junit.classpath.append(create_pathelement_tag())


def create_tag(name: str, attrs={}):
    tmp_soup = BeautifulSoup('', 'lxml-xml')
    tag = tmp_soup.new_tag(name)
    for attr in attrs:
        tag[attr] = attrs[attr]
    return tag

 # <target name="-test.method" if="testaction.method"> 
 #        <echo>Run JUnit using 'test name=$${testclass} method=$${testmethod}'</echo> 
 #    </target> 

def create_test_method_tag():
    target_tag = create_tag('target', {'name': '-test.method', 'if': 'testaction.method'})
    echo_tag = create_tag('echo')
    echo_tag.append("Run JUnit using 'test name=$${testclass} method=$${testmethod}'")
    target_tag.append(echo_tag)
    return target_tag

def create_condition_tag():
    condition_tag = create_tag('condition', {'property': 'testaction.method'})
    and_tag = create_tag('and')
    and_tag.append(create_tag('isset', {'property': 'testclass'}))
    and_tag.append(create_tag('isset', {'property': 'testmethod'}))
    condition_tag.append(and_tag)
    return condition_tag


def create_test_check_tag():
    test_check_target_tag = create_tag('target', {'name': '-test.check'})
    test_check_target_tag.append(create_condition_tag())
    return test_check_target_tag


def modify_test_target(s):
    target_tags = s.project.find_all('target')
    for target in target_tags:
        if target['name'] == 'test':
            if target['depends'] != '':
                target['depends'] = target['depends'] + ',' + '-test.check,-test.method'
            else:
                target['depends'] = '-test.check,-test.method'


def modify_junit(s):
    junit_tag = s.project.find('junit')
    junit_tag.classpath.append(create_pathelement_tag())
    if junit_tag.batchtest is not None:
        junit_tag.batchtest.decompose()
    junit_tag.append(create_tag('test', {'name': '${testclass}', 'methods': '${testmethod}'}))


def _validate_input(argv):
    if len(argv) != 2:
        print('Not enough arguments.')
        sys.exit(1)       
    build_xml_fp = argv[1]
    if not os.path.isfile(build_xml_fp):
        print('build_xml_fp DNE')
        sys.exit(1)
    return build_xml_fp


def modify_build_xml(build_xml_fp):
    soup = BeautifulSoup(open(build_xml_fp), 'lxml-xml')
    
    # Modify build.xml file.
    add_tags(soup)
    modify_test_target(soup)
    modify_junit(soup)

    # Overwrite the existing build.xml with the updated build.xml.
    with open(build_xml_fp, 'w') as f:
      # f.write(soup.prettify().encode('utf-8'))
      f.write(soup.prettify())


def main(argv=None):
    if argv is None:
        argv = sys.argv
    
    # Read in the build.xml file and open it with BS.
    build_xml_fp = _validate_input(argv)
    
    # Modify build.xml and write updated back.
    modify_build_xml(build_xml_fp) 

    ## ADD CLOVER JAR TO UNIT PATH

if __name__ == '__main__':
    sys.exit(main())


