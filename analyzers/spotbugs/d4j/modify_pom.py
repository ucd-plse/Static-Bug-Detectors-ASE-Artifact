import os
import sys

from bs4 import BeautifulSoup


def main(argv=None):
    argv = argv or sys.argv

    pom_path, l_or_h = _validate_input(argv)

    # Parse the POM.
    soup = BeautifulSoup(open(pom_path), 'lxml-xml')
    added_build = False

    if soup.project.find("build") is None:
        soup.project.append(soup.new_tag("build"))
        added_build = True

    # Add SpotBugs plugin
    if added_build:
        soup.build.insert(0, _make_spotbugs_plugin(added_build, l_or_h))
    else:
        list_builds = soup.project.find_all('build')
        for build in list_builds:
            list_plugins = build.plugins.find_all('plugin')
            for plugin in list_plugins:
                if 'spotbugs-maven-plugin' == plugin.artifactId.string.strip():
                    plugin.decompose()
            build.plugins.insert(0, _make_spotbugs_plugin(added_build, l_or_h))

    # Overwrite the existing POM with the updated POM.
    with open(pom_path, 'wb') as f:
        f.write(soup.prettify().encode('utf-8'))


def _make_spotbugs_plugin(added_build, l_or_h):
    # Adapted from https://github.com/find-sec-bugs/find-sec-bugs/wiki/Maven-configuration.
    if added_build is True:
        spotbugs_xml = """
            <plugins>
                <plugin>
                    <groupId>com.github.spotbugs</groupId>
                    <artifactId>spotbugs-maven-plugin</artifactId>
                    <version>3.1.6</version>
                    <configuration>
                        <effort>Max</effort>
                        <threshold>{}</threshold>
                    </configuration>
                </plugin>
            </plugins>
        """.format(l_or_h)
        spotbugs_element = BeautifulSoup(spotbugs_xml, 'lxml-xml').find('plugins')
    else:
        spotbugs_xml = """
        <plugin>
            <groupId>com.github.spotbugs</groupId>
            <artifactId>spotbugs-maven-plugin</artifactId>
            <version>3.1.6</version>
            <configuration>
                <effort>Max</effort>
                <threshold>{}</threshold>
            </configuration>
        </plugin>
        """.format(l_or_h)
        spotbugs_element = BeautifulSoup(spotbugs_xml, 'lxml-xml').find('plugin')
    return spotbugs_element


def _get_tag_index(element, tag):
    for i, child in enumerate(element):
        if child.tag.endswith(tag):
            return i
    return None


def _print_usage():
    print('Usage: python3 modify_pom.py <pom_path> <low-or-high>')
    print('pom_path: Path to the pom.xml file to modify.')
    print('low-or-high: low or high threshold for SpotBugs')


def _validate_input(argv):
    if len(argv) != 3:
        _print_usage()
        sys.exit(1)
    pom_path = argv[1]
    if not os.path.isfile(pom_path) and os.path.exists(pom_path):
        print('The pom_path argument is not a file or does not exist. Exiting.')
        _print_usage()
        sys.exit(1)
    l_or_h = argv[2]
    if l_or_h not in ['low', 'high']:
        _print_usage()
        sys.exit(1)
    return pom_path, l_or_h


if __name__ == '__main__':
    sys.exit(main())
