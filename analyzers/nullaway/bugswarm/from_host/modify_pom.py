import os
import sys

from bs4 import BeautifulSoup


def main(argv=None):
    argv = argv or sys.argv
    pom_path = _validate_input(argv)

    # Parse the POM.
    soup = BeautifulSoup(open(pom_path), 'lxml-xml')
    added_build = False
    grp_id = soup.project.find('groupId').getText().strip()
    builds = soup.project.find_all('build')
    dependencies = soup.project.find_all('dependencies')

    if len(dependencies) == 0:
      soup.project.append(soup.new_tag('dependencies'))

    if len(builds) == 0:
      soup.project.append(soup.new_tag('build'))
      added_build = True

    builds = soup.project.find_all('build')
    for b in builds:
      # Add error_prone plugin
      if added_build:
        soup.build.insert(0, _make_error_prone_plugin(added_build, grp_id))
      else:
        list_plugins = b.find_all('plugin')
        for plugin in list_plugins:
          artifact_id = plugin.artifactId.string.strip()
          if 'error_prone-maven-plugin' == artifact_id:
            plugin.decompose()
          if 'maven-checkstyle-plugin' == artifact_id:
            plugin.decompose()
        b.plugins.insert(len(b.plugins), _make_error_prone_plugin(added_build, grp_id))

    for d in dependencies:
      d.insert(len(d), _make_nullable_dependency())

    # Overwrite the existing POM with the updated POM.
    with open('{}'.format(pom_path), 'w') as f:
      f.write(soup.prettify().encode('utf-8'))
    

def _make_nullable_dependency():
  findbugs_dependency_xml = """
  <dependency>
    <groupId>com.google.code.findbugs</groupId>
    <artifactId>jsr305</artifactId>
    <version>3.0.2</version>
  </dependency>
  """
  findbugs_dependency_element = BeautifulSoup(findbugs_dependency_xml, 'lxml-xml').find('dependency')
  return findbugs_dependency_element


def _make_error_prone_plugin(added_build, grp_id):
    # Adapted from Use Case 3 at https://www.petrikainulainen.net/programming/maven/error_prone-maven-plugin-tutorial.
    if added_build is True:
        error_prone_xml = """
        <plugins>
          <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.5</version>
            <configuration>
              <compilerId>javac-with-errorprone</compilerId>
              <forceJavacCompilerUse>true</forceJavacCompilerUse>
              <source>1.8</source>
              <target>1.8</target>
              <showWarnings>true</showWarnings>
              <annotationProcessorPaths>
                <path>
                   <groupId>com.uber.nullaway</groupId>
                   <artifactId>nullaway</artifactId>
                   <version>0.3.0</version>
                </path>
              </annotationProcessorPaths>
              <compilerArgs>
                <arg>-XepOpt:NullAway:AnnotatedPackages={}</arg>
                <arg>-XepAllErrorsAsWarnings</arg>
                <arg>-Xmaxwarns</arg>
                <arg>10000</arg>
              </compilerArgs>
            </configuration>
            <dependencies>
              <dependency>
                <groupId>org.codehaus.plexus</groupId>
                <artifactId>plexus-compiler-javac-errorprone</artifactId>
                <version>2.8</version>
              </dependency>
              <!-- override plexus-compiler-javac-errorprone's dependency on
                   Error Prone with the latest version -->
              <dependency>
                <groupId>com.google.errorprone</groupId>
                <artifactId>error_prone_core</artifactId>
                <version>2.1.3</version>
              </dependency>
            </dependencies>
          </plugin>
        </plugins>
        """.format(grp_id)
        error_prone_element = BeautifulSoup(error_prone_xml, 'lxml-xml').find('plugins')
    else:
        error_prone_xml = """
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-compiler-plugin</artifactId>
          <version>3.5</version>
          <configuration>
            <compilerId>javac-with-errorprone</compilerId>
            <forceJavacCompilerUse>true</forceJavacCompilerUse>
            <source>1.8</source>
            <target>1.8</target>
            <showWarnings>true</showWarnings>
            <annotationProcessorPaths>
              <path>
                 <groupId>com.uber.nullaway</groupId>
                 <artifactId>nullaway</artifactId>
                 <version>0.3.0</version>
              </path>
            </annotationProcessorPaths>
            <compilerArgs>
              <arg>-XepOpt:NullAway:AnnotatedPackages={}</arg>
              <arg>-XepAllErrorsAsWarnings</arg>
              <arg>-Xmaxwarns</arg>
              <arg>10000</arg>
            </compilerArgs>
          </configuration>
          <dependencies>
            <dependency>
              <groupId>org.codehaus.plexus</groupId>
              <artifactId>plexus-compiler-javac-errorprone</artifactId>
              <version>2.8</version>
            </dependency>
            <!-- override plexus-compiler-javac-errorprone's dependency on
                 Error Prone with the latest version -->
            <dependency>
              <groupId>com.google.errorprone</groupId>
              <artifactId>error_prone_core</artifactId>
              <version>2.1.3</version>
            </dependency>
          </dependencies>
        </plugin>
        """.format(grp_id)
        error_prone_element = BeautifulSoup(error_prone_xml, 'lxml-xml').find('plugin')
    return error_prone_element


def _get_tag_index(element, tag):
    for i, child in enumerate(element):
        if child.tag.endswith(tag):
            return i
    return None


def _print_usage():
    print('Usage: python3 modify_pom.py <pom_path>')
    print('pom_path: Path to the pom.xml file to modify.')


def _validate_input(argv):
    if len(argv) != 2:
        _print_usage()
        sys.exit(1)
    pom_path = argv[1]
    if not os.path.isfile(pom_path) and os.path.exists(pom_path):
        print('The pom_path argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)
    return pom_path


if __name__ == '__main__':
    sys.exit(main())
