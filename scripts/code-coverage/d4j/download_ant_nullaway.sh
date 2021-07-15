#!/bin/bash
HOME_DIR=/home/dtomassi
MAVEN_DIR=${HOME_DIR}/.m2/repository
JAVAC_DIR=${MAVEN_DIR}/com/google/errorprone/javac/9+181-r4173-1
ERRORPRONE_DIR=${MAVEN_DIR}/com/google/errorprone/error_prone_core/2.4.0
JFORMATSTRING_DIR=${MAVEN_DIR}/com/google/code/findbugs/jFormatString/3.0.0
DATAFLOW_DIR=${MAVEN_DIR}/org/checkerframework/dataflow/2.5.7
JAVACUTIL_DIR=${MAVEN_DIR}/org/checkerframework/javacutil/2.5.7

echo Downloading Javac
mkdir -p ${JAVAC_DIR}
cd ${JAVAC_DIR}
wget https://repo1.maven.org/maven2/com/google/errorprone/javac/9+181-r4173-1/javac-9+181-r4173-1.jar
echo Downloading Error Prone
mkdir -p ${ERRORPRONE_DIR}
cd ${ERRORPRONE_DIR}
wget https://repo1.maven.org/maven2/com/google/errorprone/error_prone_core/2.4.0/error_prone_core-2.4.0-with-dependencies.jar 
echo Downloading JFormatString
mkdir -p ${JFORMATSTRING_DIR}
cd ${JFORMATSTRING_DIR}
wget https://repo1.maven.org/maven2/com/google/code/findbugs/jFormatString/3.0.0/jFormatString-3.0.0.jar 
echo Downloading Dataflow
mkdir -p ${DATAFLOW_DIR}
cd ${DATAFLOW_DIR}
wget https://repo1.maven.org/maven2/org/checkerframework/dataflow/2.5.7/dataflow-2.5.7.jar 
echo Downloading JavacUtil
mkdir -p ${JAVACUTIL_DIR}
cd ${JAVACUTIL_DIR}
wget https://repo1.maven.org/maven2/org/checkerframework/javacutil/2.5.7/javacutil-2.5.7.jar


