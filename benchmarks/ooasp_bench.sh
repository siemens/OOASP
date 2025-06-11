#!/bin/bash

FILE_PATH=benchmarks/script/smart-options.txt
RS_PATH=~/runsolver/src/runsolver
PYTHON_SCRIPT=ooasp/app.py
TIME_LIMIT=1
ITERATIONS=10

KV_PATH=benchmarks/script/results/key_value
OUT_PATH=benchmarks/script/results/out
THREAD_PATH=benchmarks/script/results/thread

#----------FUNCTIONS----------

make_top_directories () {
    mkdir -p $KV_PATH
    mkdir -p $OUT_PATH
    mkdir -p $THREAD_PATH
}

make_suite_directories () {
    mkdir -p $KV_PATH/$1
    mkdir -p $OUT_PATH/$1
    mkdir -p $THREAD_PATH/$1
}

#----------SETUP------------

make_top_directories

#----------ELEMENT BENCHMARKS----------

echo -e "$(date) \e[94mStarting \e[1;4mElement\e[0;94m Benchmarks\e[39m"

cat $FILE_PATH | while read OPT
do
    for i in $(seq 1 $ITERATIONS);
    do
        DIR_OUTNAME=${OPT//,/-}
        OUTNAME="${OPT//,/-}__E${i}"

        make_suite_directories $DIR_OUTNAME

        echo -e "\e[90m$(date)\e[36m:>\e[39m Starting benchmark: \e[1;92mI=$i\e[0;39m with options: \e[1;32m$OPT\e[0;39m"
        $RS_PATH -o $OUT_PATH/$DIR_OUTNAME/$OUTNAME.log -v $KV_PATH/$DIR_OUTNAME/$OUTNAME.log -w $THREAD_PATH/$DIR_OUTNAME/$OUTNAME.log -W $TIME_LIMIT python $PYTHON_SCRIPT --elementA $i --elementB $i --elementC $i --elementD $i --smart-functions "$OPT"
        echo -e "\e[90m$(date)\e[36m:>\e[39m \e[35mFinished for \e[1;92mI=$i\e[0;39m"
    done
done

#----------FRAME BENCHMARKS----------

echo -e "$(date) \e[94mStarting \e[1;4mFrame\e[0;94m Benchmarks\e[39m"

cat $FILE_PATH | while read OPT
do
    for i in {5,7,9,13,16};
    do
        DIR_OUTNAME=${OPT//,/-}
        OUTNAME="${OPT//,/-}__F${i}"

        make_suite_directories $DIR_OUTNAME

        echo -e "\e[90m$(date)\e[36m:>\e[39m Starting benchmark: \e[1;92mI=$i\e[0;39m with options: \e[1;32m$OPT\e[0;39m"
        $RS_PATH -o $OUT_PATH/$DIR_OUTNAME/$OUTNAME.log -v $KV_PATH/$DIR_OUTNAME/$OUTNAME.log -w $THREAD_PATH/$DIR_OUTNAME/$OUTNAME.log -W $TIME_LIMIT python $PYTHON_SCRIPT --frame $i --smart-functions "$OPT"
        echo -e "\e[90m$(date)\e[36m:>\e[39m \e[35mFinished for \e[1;92mI=$i\e[0;39m"
    done
done

echo -e "\e[1;4;95mFINISHED"\!"\e[0;39m"
