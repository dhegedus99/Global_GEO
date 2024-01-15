# GLOBAL GEO COMPOSITE CREATOR ####

These scripts produce global geostationary composite imagery from
Himawari-8, GOES-16, GOES-18, Meteosat-9 and Meteosat-10.

## Setup

The global geo composite creator requires a python virtual environment, 
which holds all necessary libraries. It also requires the xRITDecompress 
binary from EUMETSAT to read in the SEVIRI dataset.

To set up the virtual environment and get the binary, run:
```
bash config.sh
```

Then navigate into the EUMETSAT repo, e.g.:
```
cd /home/users/$USER/bin/PublicDecompWT/xRITDecompress
```

Edit the Makefile:
line 6: ```DEST_DIR=/home/users/$(USER)```
line 20-21: comment out

Run to compile the xRITDecompress binary (we will need this path in the ./run_geo script):
make


To run, simply execute:
 python Global_GEO.py

And the script will process the most recent suitable timeslot
(hourly, due to SEVIRI license restrictions imposed on the RSG
group). To process older data, instead run the script with a
command line argument specifying the desired timeslot:
 python Global_GEO.py 202210051200
Where the timeslot is in YYYYmmddHHMM format.

This script requires numerous libraries, most notably:
 - satpy and dependencies
 - s3fs
 - gdal

Also note that for performance reasons, an internal satpy function
( _get_sensor_angles) is used. This is not a supported function so
the utility may break at any point in the future.
