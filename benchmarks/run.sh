#!/bin/bash

#########################################################################################################
# This script assumes to be run from the asp_interactive_configuration directory as ./benchmarks/run.sh #
# Before running the script make sure the poetry shell virtual environment is activated.                #
#########################################################################################################

id=$(date --iso-8601)
file=bench_outputs_$id.txt
mkdir -p benchmarks/outputs
echo -e "\e[36mOutputs will be saved to: benchmarks/outputs/$file\e[39m"
echo -e "\e[35mStarting\e0\e[5m...\e[25m\e[39m"
for i in {1..20}
do
    echo Running for $i
    echo ----------$i---------- >> benchmarks/outputs/$file
    python ooasp/run.py --elementA $i --elementB $i --elementC $i --elementD $i >> benchmarks/outputs/$file
    echo --------------------- >> benchmarks/outputs/$file
done
echo -e "\e[96mFinished!\e[39m"