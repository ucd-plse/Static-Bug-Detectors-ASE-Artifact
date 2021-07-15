#!/bin/bash
# /tmp/chart_4b chart-4 b
while IFS="	" read -r folder class method bug version
do
  bash run_clover.sh ${folder} ${class} ${method} ${bug} ${version}
done < $1

