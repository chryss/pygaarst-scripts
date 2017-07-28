#! /bin/bash

DAYS=3
TARGETDIR=/Volumes/cwdata1/VIIRS/GINA/mirror_script/
SCRIPTDIR=/Users/chris/Dropbox/Research/pygaarst-scripts/cw-research/

source activate snakes

while [[ $# -gt 1 ]]
do
key="$1"
case $key in
    -d|--days)
        DAYS="$2"
        shift
        ;;
    -t|--target)
        TARGETDIR="$2"
        shift
        ;;
    *)
        break    # unknown option
    ;;
esac
shift # past argument or value
done

cd $SCRIPTDIR
#python ginasync.py --reb
#python ginasync.py
bash mirror_products.sh -f uafgina -s snpp -i viirs -p level1 -n -d $DAYS -o $TARGETDIR
python ginawgetpostproc.py
python ginaviz.py --num --dir $TARGETDIR

source deactivate
