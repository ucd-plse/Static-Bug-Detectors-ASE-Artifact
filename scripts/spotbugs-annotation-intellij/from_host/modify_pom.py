import os
import sys

from bs4 import BeautifulSoup

argv = sys.argv

pom_fp = argv[1]

soup = BeautifulSoup(open(pom), 'lxml-xml')
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
