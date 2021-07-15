#!/bin/bash
export PATH=$PATH:/home/dtomassi/github/defects4j/framework/bin
# Chart 4b chart_4b
while IFS="	" read -r repo id
do
  bash checkout.sh ${repo} ${id}
done < $1

