import codecs
import os
import sys

from bs4 import BeautifulSoup


def main(argv=None):
    argv = argv or sys.argv

    pom_path, testname = _validate_input(argv)

    # Parse the POM.
    soup = BeautifulSoup(codecs.open(pom_path, "r", "utf-8"), 'lxml-xml')

    # # Change https to http
    # repos = soup.project.find('repositories')
    # if repos is not None:
    #     repo_list = repos.find_all('repository')
    #     for repo in repo_list:
    #         repo_url = repo.url.string.strip().replace('https', 'http')
    #         repo.url.string = repo_url
    if soup.find('project') is None:
        soup.insert(0, soup.new_tag('project'))

    added_build = False
    if soup.project.find("build") is None:
        soup.project.append(soup.new_tag("build"))
        added_build = True

    # Add Clover plugin
    if added_build:
        soup.build.insert(0, _make_clover_plugin(added_build))

    list_builds = soup.project.find_all('build')
    for build in list_builds:
        has_pm = build.find('pluginManagement') is not None
        if has_pm:
            list_plugins = build.pluginManagement.plugins.find_all('plugin')
        else:
            if build.plugins is None:
                build.insert(0, soup.new_tag('plugins'))
            list_plugins = build.plugins.find_all('plugin')
        modified_surefire = False
        for plugin in list_plugins:
            if plugin.artifactId is None:
                continue
            if 'maven-surefire-plugin' == plugin.artifactId.string.strip():
                if plugin.find('configuration') is None:
                    plugin.append(_generate_configuration_xml(testname))
                else:
                    plugin.configuration.replace_with(_generate_configuration_xml(testname))
                    # plugin.append(_generate_configuration_xml(testname))
                modified_surefire = True
        if not modified_surefire:
            if has_pm:
                build.pluginManagement.plugins.insert(0, _make_surefire_plugin(testname))
            else:
                build.plugins.insert(0, _make_surefire_plugin(testname))
        if not added_build:
            if has_pm:
                build.pluginManagement.plugins.insert(0, _make_clover_plugin(added_build))
            else:
                build.plugins.insert(0, _make_clover_plugin(added_build))

    # Overwrite the existing POM with the updated POM.
    with open(pom_path, 'w+') as f:
        if isinstance(soup.prettify(), str):
            f.write(soup.prettify())
        else:
            f.write(soup.prettify().encode('utf-8'))


def _make_clover_plugin(added_build):
    if added_build:
        clover_xml = """
            <plugins>
                <plugin>
                    <groupId>org.openclover</groupId>
                    <artifactId>clover-maven-plugin</artifactId>
                    <configuration>
                        <reportDescriptor>clover-report.xml</reportDescriptor>
                    </configuration>
                </plugin>
            </plugins>
        """
        clover_element = BeautifulSoup(clover_xml, 'lxml-xml').find('plugins')
    else:
        clover_xml = """
            <plugin>
                <groupId>org.openclover</groupId>
                <artifactId>clover-maven-plugin</artifactId>
                <configuration>
                    <reportDescriptor>clover-report.xml</reportDescriptor>
                </configuration>
            </plugin>
        """
        clover_element = BeautifulSoup(clover_xml, 'lxml-xml').find('plugin')
    return clover_element


def _make_surefire_plugin(testname):
    surefire_xml = """
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-surefire-plugin</artifactId>
            <version>2.20.1</version>
            <configuration>
                <test>{}</test>
            </configuration>
        </plugin>
    """.format(testname)
    return BeautifulSoup(surefire_xml, 'lxml-xml').find('plugin')


def _generate_configuration_xml(testname):
    config_xml = """
                <configuration>
                    <test>{}</test>
                </configuration>
                """.format(testname)
    return BeautifulSoup(config_xml, 'lxml-xml').find('configuration')


def _generate_test_xml(testname):
    test_xml = """
                    <test>{}</test>
                """.format(testname)
    return BeautifulSoup(test_xml, 'lxml-xml').find('test')


def _get_tag_index(element, tag):
    for i, child in enumerate(element):
        if child.tag.endswith(tag):
            return i
    return None


def _print_usage():
    print('Usage: python3 modify_pom.py <pom_path>')
    print('pom_path: Path to the pom.xml file to modify.')


def _validate_input(argv):
    if len(argv) != 3:
        _print_usage()
        sys.exit(1)
    pom_path, testname = argv[1], argv[2]
    if not os.path.isfile(pom_path) and os.path.exists(pom_path):
        print('The pom_path argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)
    return pom_path, testname


if __name__ == '__main__':
    sys.exit(main())
