#!/bin/bash
export PATH=$PATH:/home/dtomassi/github/defects4j/framework/bin
# defects4j checkout -p Closure -v 171b -w /tmp/Closure_171b
defects4j checkout -p $1 -v $2 -w /tmp/$1-$2
cd /tmp/$3
defects4j compile
