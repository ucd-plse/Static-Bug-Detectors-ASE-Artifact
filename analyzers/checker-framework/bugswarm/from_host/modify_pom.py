import os
import sys

from bs4 import BeautifulSoup


def main(argv=None):
    argv = argv or sys.argv
    pom_path = _validate_input(argv)
    # Parse the POM.

    soup = BeautifulSoup(open(pom_path), 'lxml-xml')

    # Add <properties> tag
    properties = soup.project.find('properties', recursive=False)
    if properties is None:
      soup.project.insert(0, BeautifulSoup('<properties></properties>', 'lxml-xml').find('properties'))
    errorprone_xml = '<errorProneJavac>${com.google.errorprone:javac:jar}</errorProneJavac>'
    soup.properties.insert(0, BeautifulSoup(errorprone_xml, 'lxml-xml').find('errorProneJavac'))
    checker_xml = '<checkerFrameworkVersion>3.10.0</checkerFrameworkVersion>'
    soup.properties.insert(0, BeautifulSoup(checker_xml, 'lxml-xml').find('checkerFrameworkVersion'))
    
    # Add <dependencies> tag
    dependencies = soup.project.find('dependencies')
    if dependencies is None:
      soup.project.insert(1, _make_dependencies_tags())
    else:
      checker_xml = """<dependency>
  <groupId>org.checkerframework</groupId>
  <artifactId>checker-qual</artifactId>
  <version>${checkerFrameworkVersion}</version>
  </dependency>"""
      soup.project.dependencies.insert(1, BeautifulSoup(checker_xml, 'lxml-xml').find('dependency'))
      errorprone_xml = """<dependency>
      <groupId>com.google.errorprone</groupId>
      <artifactId>javac</artifactId>
      <version>9+181-r4173-1</version>
    </dependency>"""
      soup.project.dependencies.insert(1, BeautifulSoup(errorprone_xml, 'lxml-xml').find('dependency'))
    
    # Add <build> tag
    added_build = False
    builds = soup.project.find_all('build')
    if len(builds) == 0:
      soup.project.append(soup.new_tag('build'))
      added_build = True
    for b in builds:
      if added_build:
        b.insert(0, _make_maven_dep_plugin(added_build))
      else:
        added_mvn_dep = False
        plugin_list = b.find_all('plugin')
        for plugin in plugin_list:
          if plugin.artifactId == None:
            continue
          artifact_id = plugin.artifactId.string.strip()
          if 'maven-dependency-plugin' == artifact_id:
            plugin.decompose()
            b.plugins.insert(len(b.plugins), _make_maven_dep_plugin(added_build))
            added_mvn_dep = True
        if not added_mvn_dep:
          b.plugins.insert(len(b.plugins), _make_maven_dep_plugin(added_build))

    # Add <profiles> tag
    profiles = soup.project.find('profiles')
    if profiles is None:
      soup.project.insert(len(soup.project), _make_profile_tags())
    else:
      prof_1_xml = """<profile>
    <id>checkerframework</id>
    <activation>
      <jdk>[1.8,13)</jdk>
    </activation>
    <build>
      <plugins>
        <plugin>
          <artifactId>maven-compiler-plugin</artifactId>
          <version>3.8.1</version>
          <configuration>
            <fork>true</fork>
            <compilerArguments>
              <Xmaxerrs>10000</Xmaxerrs>
              <Xmaxwarns>10000</Xmaxwarns>
            </compilerArguments>
            <annotationProcessorPaths>
              <path>
                <groupId>org.checkerframework</groupId>
                <artifactId>checker</artifactId>
                <version>3.7.0</version>
              </path>
            </annotationProcessorPaths>
            <annotationProcessors>
              <!-- Add all the checkers you want to enable here -->
              <annotationProcessor>org.checkerframework.checker.nullness.NullnessChecker</annotationProcessor>
            </annotationProcessors>
            <compilerArgs>
              <arg>-Awarns</arg> <!-- -Awarns turns type-checking errors into warnings. -->
            </compilerArgs>
          </configuration>
        </plugin>
      </plugins>
    </build>
    <dependencies>
      <dependency>
        <groupId>org.checkerframework</groupId>
        <artifactId>checker</artifactId>
        <version>${checkerFrameworkVersion}</version>
      </dependency>
    </dependencies>
  </profile>"""
      profiles.insert(0, BeautifulSoup(prof_1_xml, 'lxml-xml').find('profile'))
      prof_2_xml = """<profile>
    <id>checkerframework-jdk8</id>
    <activation>
      <jdk>1.8</jdk>
    </activation>
    <!-- using github.com/google/error-prone-javac is required when running on JDK 8 -->
    <properties>
      <javac.version>9+181-r4173-1</javac.version>
    </properties>
    <dependencies>
      <dependency>
        <groupId>org.checkerframework</groupId>
        <artifactId>checker-qual</artifactId>
        <version>${checkerFrameworkVersion}</version>
      </dependency>
      <dependency>
        <groupId>com.google.errorprone</groupId>
        <artifactId>javac</artifactId>
        <version>9+181-r4173-1</version>
      </dependency>
    </dependencies>
    <build>
      <plugins>
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-compiler-plugin</artifactId>
          <configuration>
            <fork>true</fork> <!-- Must fork or else JVM arguments are ignored. -->
            <source>1.8</source>
            <target>1.8</target>
            <compilerArgs combine.children="append">
              <arg>-J-Xbootclasspath/p:${settings.localRepository}/com/google/errorprone/javac/${javac.version}/javac-${javac.version}.jar</arg>
            </compilerArgs>
          </configuration>
        </plugin>
      </plugins>
    </build>
  </profile>"""
      profiles.insert(0, BeautifulSoup(prof_2_xml, 'lxml-xml').find('profile'))
    # Overwrite the existing POM with the updated POM.
    with open('{}'.format(pom_path), 'wb') as f:
      f.write(soup.prettify().encode('utf-8'))


def _make_dependencies_tags():
  dependencies_xml = """
  <dependencies>
    <dependency>
      <groupId>org.checkerframework</groupId>
      <artifactId>checker-qual</artifactId>
      <version>${checkerFrameworkVersion}</version>
    </dependency>
    <dependency>
      <groupId>com.google.errorprone</groupId>
      <artifactId>javac</artifactId>
      <version>9+181-r4173-1</version>
    </dependency>
  </dependencies>
  """
  dependencies_el = BeautifulSoup(dependencies_xml, 'lxml-xml').find('dependencies')
  return dependencies_el


def _make_maven_dep_plugin(added_build):
  maven_dep_xml = None
  maven_dep_el = None
  if added_build:
    maven_dep_xml = """
<plugins>
  <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-dependency-plugin</artifactId>
      <executions>
          <execution>
              <goals>
                  <goal>properties</goal>
              </goals>
          </execution>
      </executions>
  </plugin>
</plugins>
    """
    maven_dep_el = BeautifulSoup(maven_dep_xml, 'lxml-xml').find('plugins')
  else:
    maven_dep_xml = """
  <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-dependency-plugin</artifactId>
      <executions>
          <execution>
              <goals>
                  <goal>properties</goal>
              </goals>
          </execution>
      </executions>
  </plugin>
    """
    maven_dep_el = BeautifulSoup(maven_dep_xml, 'lxml-xml').find('plugin')
  return maven_dep_el


def _make_profile_tags():
  profile_xml = """
    <profiles>
  <profile>
    <id>checkerframework</id>
    <activation>
      <jdk>[1.8,13)</jdk>
    </activation>
    <build>
      <plugins>
        <plugin>
          <artifactId>maven-compiler-plugin</artifactId>
          <version>3.8.1</version>
          <configuration>
            <fork>true</fork>
            <compilerArguments>
              <Xmaxerrs>10000</Xmaxerrs>
              <Xmaxwarns>10000</Xmaxwarns>
            </compilerArguments>
            <annotationProcessorPaths>
              <path>
                <groupId>org.checkerframework</groupId>
                <artifactId>checker</artifactId>
                <version>3.7.0</version>
              </path>
            </annotationProcessorPaths>
            <annotationProcessors>
              <!-- Add all the checkers you want to enable here -->
              <annotationProcessor>org.checkerframework.checker.nullness.NullnessChecker</annotationProcessor>
            </annotationProcessors>
            <compilerArgs>
              <arg>-Awarns</arg> <!-- -Awarns turns type-checking errors into warnings. -->
            </compilerArgs>
          </configuration>
        </plugin>
      </plugins>
    </build>
    <dependencies>
      <dependency>
        <groupId>org.checkerframework</groupId>
        <artifactId>checker</artifactId>
        <version>${checkerFrameworkVersion}</version>
      </dependency>
    </dependencies>
  </profile>
  <profile>
    <id>checkerframework-jdk8</id>
    <activation>
      <jdk>1.8</jdk>
    </activation>
    <!-- using github.com/google/error-prone-javac is required when running on JDK 8 -->
    <properties>
      <javac.version>9+181-r4173-1</javac.version>
    </properties>
    <dependencies>
      <dependency>
       <groupId>org.checkerframework</groupId>
       <artifactId>checker-qual</artifactId>
       <version>${checkerFrameworkVersion}</version>
      </dependency>
      <dependency>
        <groupId>com.google.errorprone</groupId>
        <artifactId>javac</artifactId>
        <version>9+181-r4173-1</version>
      </dependency>
    </dependencies>
    <build>
      <plugins>
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-compiler-plugin</artifactId>
          <configuration>
            <fork>true</fork> <!-- Must fork or else JVM arguments are ignored. -->
            <source>1.8</source>
            <target>1.8</target>
            <compilerArgs combine.children="append">
              <arg>-J-Xbootclasspath/p:${settings.localRepository}/com/google/errorprone/javac/${javac.version}/javac-${javac.version}.jar</arg>
            </compilerArgs>
          </configuration>
        </plugin>
      </plugins>
    </build>
  </profile>
</profiles>
  """
  profile_el = BeautifulSoup(profile_xml, 'lxml-xml').find('profiles')

  return profile_el


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
