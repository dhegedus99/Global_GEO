#!/bin/bash
# Check for the existence of the cesium images
thumbdir=${1} # Directory into which the cesium images are
dtstr=${2} # YYYYMMDD
vals=($(seq -w 0 1 23))
nexpected=2734
sexpected=1

export XRIT_DECOMPRESS_PATH=/home/users/$USER/bin/xRITDecompress

venv_py=virtual_env_globgeo
module load jaspy
source /home/users/$USER/$venv_py/bin/activate

outdir_top=/gws/pw/j07/rsg_share/public/nrt/nrt_imagery_geo_global/quick_look_cesium/
cachedir=/work/scratch-nopw2/$USER/tmp/
tmpdir=/work/scratch-nopw2/$USER/tmp/
idir_top=/work/scratch-nopw2/$USER/global_geo/
pydir=/home/users/$USER/Global_GEO/
XRIT_Decompress_path=/home/users/$USER/bin/xRITDecompress

function run {
    newlist=()
    #echo $newlist
    datetime=$( date -d "${dtstr}" '+%Y/%m/%d' )
    datetimestr="${dtstr}"
    logdir=/work/scratch-nopw2/$USER/global_geo/$datetime
    echo $datetime
    for time in ${vals[@]}
    do newtime="${time}00"
        nact=$( find ${thumbdir}/${datetime}/*${datetimestr}${newtime}*/ -type f | wc -l )
        file=${tmpdir}return_dict${datetimestr}${newtime}.pkl
        if [ -e "$file" ]; then
            sact=$( stat -c%s $file )
            if [[ $sact -ge $sexpected ]] && [[ $nact -ge $nexpected ]]
            then
                newlist+="exists "
            else
                newlist+="${newtime} "
            fi
        else
            echo "file doesn't exist"
            newlist+="${newtime} " 
        fi
    done
    #existing=($(echo -e "${newlist[@]}" | sort -u ))
    #echo ${existing[@]}
    sorted_unique_ids=($(echo "${newlist[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))
    missing=( "${sorted_unique_ids[@]/exists}" )
    for time in ${missing[@]}
    do
    echo $time

    python Global_GEO.py --outdir_top=$outdir_top --idir_top=$idir_top --tmpdir=$tmpdir --cachedir=$cachedir --logdir=$logdir --pydir=$pydir --XRIT_Decompress_path=$XRIT_Decompress_path ${datetimestr}${time}

    done
    if [[ ${#sorted_unique_ids[@]} -eq 1 ]]
    then
        have_run="true"
    else
        have_run="false"
        
    fi
    echo $have_run
    }

# Repeatedly run the function, until it actually detects the
# input quick-look images

while true
do
run
if [[ $have_run == "false" ]]
    then
        stime=`date +%s`
        echo $stime
        sleep 3600
    else
        echo sleeping
        sleep 36000
        ctime=`date +%s`
        echo "          "$((ctime - stime)) s
fi
done