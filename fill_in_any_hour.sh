#!/bin/bash
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


dtstr=${1} #datetime in format "%Y%m%d%H%M"

if [ ! -z "$dtstr" -a "$dtstr" != " " ]; then
        Year="${dtstr:0:4}"
        Month="${dtstr:4:2}"
        Day="${dtstr:6:2}"
        Hour="${dtstr:8:2}"
        
else
        dtstr="$(date +%Y%m%d%H00)"

        Year="$(date +%Y)"
        Month="$(date +%m)"
        Day="$(date +%d)"
        Hour="$(date +%H)"

fi

logdir=/work/scratch-nopw2/$USER/global_geo/Year/Month/Day

python Global_GEO.py --outdir_top=$outdir_top --idir_top=$idir_top --tmpdir=$tmpdir --cachedir=$cachedir --logdir=$logdir --pydir=$pydir --XRIT_Decompress_path=$XRIT_Decompress_path $dtstr

