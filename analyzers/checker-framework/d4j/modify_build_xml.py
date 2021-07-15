import os
import sys

from bs4 import BeautifulSoup, Tag, NavigableString

TAG_CREATION_FUNCS = ['create_property_env_tag', 'create_property_cf_tag',
                      'create_cond_tag', 'create_presetdef_tag']



def create_property_env_tag():
    return create_tag('property', {'environment': 'env'})

def create_property_cf_tag():
    return create_tag('property', {'name': 'checkerframework', 'value': '${env.CHECKERFRAMEWORK}'})

def create_cond_tag():
    cond_tag = create_tag('condition', {'property': 'cfJavac', 'value': 'javac.bat', 'else': 'javac'})
    cond_tag.append(create_tag('os', {'family': 'windows'}))
    return cond_tag

def create_javac_tag():
    javac_tag = create_tag('javac', {'fork': 'yes', 'executable': '${checkerframework}/checker/bin/${cfJavac}'})
    javac_tag.append(create_tag('compilerarg', {'value': '-version'}))
    javac_tag.append(create_tag('compilerarg', {'value': '-implicit:class'}))
    return javac_tag

def create_presetdef_tag():
    preset_tag = create_tag('presetdef', {'name': 'jsr308.javac'})
    preset_tag.append(create_javac_tag())
    return preset_tag

def clone(el):
    if isinstance(el, NavigableString):
        return type(el)(el)

    copy = Tag(None, el.builder, el.name, el.namespace, el.nsprefix)
    # work around bug where there is no builder set
    # https://bugs.launchpad.net/beautifulsoup/+bug/1307471
    copy.attrs = dict(el.attrs)
    for attr in ('can_be_empty_element', 'hidden'):
        setattr(copy, attr, getattr(el, attr))
    for child in el.contents:
        copy.append(clone(child))
    return copy

# <target name="check-nullness"
#           description="Check for null pointer dereferences"
#           depends="clean,...">
#     <!-- use jsr308.javac instead of javac -->
#     <jsr308.javac ... >
#       <compilerarg line="-processor org.checkerframework.checker.nullness.NullnessChecker"/>
#       <!-- optional, to not check uses of library methods:
#         <compilerarg value="-AskipUses=^(java\.awt\.|javax\.swing\.)"/>
#       -->
#       <compilerarg line="-Xmaxerrs 10000"/>
#       ...
#     </jsr308.javac>
#   </target>

def create_target_tag(s):
    target_tags = s.project.find_all('target')
    compile_tag = None
    # Find <target name="compile" ... /> tag
    for target in target_tags:
        if target['name'] == 'compile':
            compile_tag = clone(target)
            break

    # Modify target tag
    compile_tag['name'] = 'check-nullness'
    #compile_tag['depends'] = 'clean,' + compile_tag['depends']
    compile_tag.javac.append(create_tag('compilerarg', {'line': '-processor org.checkerframework.checker.nullness.NullnessChecker'}))
    compile_tag.javac.append(create_tag('compilerarg', {'line': '-Xmaxerrs 10000'}))
    compile_tag.javac.append(create_tag('compilerarg', {'line': '-Xmaxwarns 10000'}))
    compile_tag.javac.append(create_tag('compilerarg', {'line': '-Awarns'}))
    compile_tag.javac['target'] = '1.8'
    compile_tag.javac['source'] = '1.8'
    compile_tag.javac.name = 'jsr308.javac'

    return compile_tag


def add_tags(s):
    for tag_func in [globals()[func] for func in TAG_CREATION_FUNCS]:
        s.project.append(tag_func())
    s.project.append(create_target_tag(s))


def create_tag(name: str, attrs={}):
    tmp_soup = BeautifulSoup('', 'lxml-xml')
    tag = tmp_soup.new_tag(name)
    for attr in attrs:
        tag[attr] = attrs[attr]
    return tag


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


