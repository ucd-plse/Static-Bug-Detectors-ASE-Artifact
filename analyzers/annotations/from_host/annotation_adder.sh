#!/bin/bash
export JAVA_HOME=/usr/lib/jvm/java-8-oracle/jre
export PATH=$JAVA_HOME/bin:$PATH
find /home/travis/build/failed -name "*.java" | while read x; do java -jar /from_host/annotation-adder-$1.jar $x $x; done
find /home/travis/build/passed -name "*.java" | while read x; do java -jar /from_host/annotation-adder-$1.jar $x $x; done
