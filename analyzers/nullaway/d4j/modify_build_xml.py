import inspect
import os
import sys

from bs4 import BeautifulSoup

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
JAR_DIR = os.path.join(current_dir, 'nullaway_jars')
print(JAR_DIR)

def create_tag(name: str, attrs={}):
    tmp_soup = BeautifulSoup('', 'lxml-xml')
    tag = tmp_soup.new_tag(name)
    for attr in attrs:
        tag[attr] = attrs[attr]
    return tag


def _validate_input(argv):
    if len(argv) != 3:
        print('Not enough arguments.')
        sys.exit(1)       
    build_xml_fp = argv[1]
    if not os.path.isfile(build_xml_fp):
        print('build_xml_fp DNE')
        sys.exit(1)
    group_id = argv[2]
    return build_xml_fp, group_id


def _make_populate_path_tag():
    path_tag = create_tag('path', attrs={'id':'processorpath.ref'})
    paths = ["{}/error_prone_core-2.4.1-20200810.223009-23-with-dependencies.jar".format(JAR_DIR),
             "{}/jFormatString-3.0.0.jar".format(JAR_DIR),
             "{}/dataflow-2.5.7.jar".format(JAR_DIR),
             "{}/dataflow-shaded-3.1.2.jar".format(JAR_DIR),
             "{}/javacutil-2.5.7.jar".format(JAR_DIR),
             "{}/threeten-extra-1.5.0.jar".format(JAR_DIR),
             "{}/nullaway-0.3.0.jar".format(JAR_DIR)]
    for path in paths:
        path_tag.insert(0, create_tag('pathelement', attrs={'location' : path}))
    return path_tag
 

def modify_build_xml(build_xml_fp, group_id):
    soup = BeautifulSoup(open(build_xml_fp), 'lxml-xml')

    compile_target_tag = soup.find_all(attrs={"name" : "compile"})[0]
    compile_target_tag.insert(0, create_tag('property', attrs={'name': 'javac.jar', 'location': '{}/javac-9+181-r4173-1.jar'.format(JAR_DIR)}))
    compile_target_tag.insert(1, _make_populate_path_tag())
    if hasattr(compile_target_tag.javac, 'source'):
        del compile_target_tag.javac['source']
    if hasattr(compile_target_tag.javac, 'target'):
        del compile_target_tag.javac['target']
    if hasattr(compile_target_tag.javac, 'fork'):
        compile_target_tag.javac['fork'] = "yes"
    if hasattr(compile_target_tag.javac, 'includeantruntime'):
        compile_target_tag.javac['includeantruntime'] = "no"
    if hasattr(compile_target_tag.javac, 'encoding'):
        compile_target_tag.javac['encoding'] = 'iso-8859-1'
    else:
        compile_target_tag.javac['encoding'] = 'iso-8859-1'
    compile_target_tag.javac.insert(0,create_tag('compilerarg', attrs={'value':"-J-Xbootclasspath/p:${javac.jar}"}))
    compile_target_tag.javac.insert(1,create_tag('compilerarg', attrs={'line':"-XDcompilePolicy=simple"}))
    compile_target_tag.javac.insert(2,create_tag('compilerarg', attrs={'value':"-processorpath"}))
    compile_target_tag.javac.insert(3,create_tag('compilerarg', attrs={'pathref':"processorpath.ref"}))
    compile_target_tag.javac.insert(4,create_tag('compilerarg', attrs={'value':"-Xplugin:ErrorProne -XepOpt:NullAway:AnnotatedPackages={} -XepAllErrorsAsWarnings -Xmaxwarns 10000".format(group_id)}))
    with open('{}'.format(build_xml_fp), 'wb') as f:
        f.write(soup.prettify().encode('utf-8'))


def main(argv=None):
    if argv is None:
        argv = sys.argv
    
    # Read in the build.xml file and open it with BS.
    build_xml_fp, group_id = _validate_input(argv)
    
    # Modify build.xml and write updated back.
    modify_build_xml(build_xml_fp, group_id) 


if __name__ == '__main__':
    sys.exit(main())


