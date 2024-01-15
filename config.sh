#!/bin/bash

#Setup python virtual environment based on jaspy
module load jaspy
python -m venv --system-site-packages /home/users/$USER/glob_geo_env
source /home/users/$USER/glob_geo_env/bin/activate
pip install s3fs
pip install gdal2tiles
deactivate


#Clone XRITDecompress library from EUMETSAT
cd /home/users/$USER/bin/

git clone https://gitlab.eumetsat.int/open-source/PublicDecompWT.git

#if you get an error about the Peer's certificate, comment out line 11 and uncomment line 14-16
#git config --global http.sslVerify false
#git clone https://gitlab.eumetsat.int/open-source/PublicDecompWT.git
#git config --global http.sslVerify true
