#!/bin/bash

export HOME=/home/pcy/pichayon
export LOG=$HOME/logs

if [ ! -d $LOG ]
then
    echo "create dir $LOG"
    mkdir -p $LOG
fi

cd $HOME
. venv/bin/activate
./scripts/run-door-controller > $LOG/console.log 2>&1
