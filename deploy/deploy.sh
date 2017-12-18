#!/bin/bash

pushd `dirname $0` > /dev/null
SCRIPT_DIR=`pwd -P`
popd > /dev/null

ACTION=deploy
RESTART=1
ENVR=pay-http
HOST=test

usage()
{
    echo "Usage: `basename $0` [-b|f|s] [-p] [-r] [-h HOST]"
    exit 1
}

[ $# -eq 0 ] && usage

while getopts :bfsprh: OPTION
do
    case $OPTION in
        b)
            ENVR=pay-http
            ;;
        p)
            ACTION=envinstall
            ;;
        r)
            RESTART=0
            ;;
        h)
            HOST=$OPTARG
            ;;
        \?)
            usage
            ;;
    esac
done


(
    cd $SCRIPT_DIR
    fab dep:$HOST pro:$ENVR $ACTION:$RESTART
)
