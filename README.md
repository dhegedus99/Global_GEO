# GLOBAL GEO COMPOSITE CREATOR ####

These scripts produce global geostationary composite imagery from
Himawari-8, GOES-16, GOES-18, Meteosat-9 and Meteosat-10.

## Setup

The global geo composite creator requires a python virtual environment, 
which holds all necessary libraries. It also requires the xRITDecompress 
binary from EUMETSAT to read in the SEVIRI dataset. These are done, when 
running:
```bash config.sh```

Then navigate into the EUMETSAT repo, e.g.:
```cd /home/users/$USER/bin/PublicDecompWT/xRITDecompress```

Edit the Makefile:
line 6: ```DEST_DIR=/home/users/$(USER)```
line 20-21: comment out

Run to compile the xRITDecompress binary (we will need this path in the 
./run_geo script):
```make```

## Running the proccesing

Note:
- Make sure the name of the virtual python environment is the same in
  both the config and run_geo script (but can be named anything)
- Make sure the path given for the xRITCompress binary in run_geo is
  the same as in the Makefile (line 24)

To run the global_geo processing, run: 
```./run_geo```

By default, the script will process the most recent suitable timeslot
(hourly, due to SEVIRI license restrictions imposed on the RSG
group). To process older data, instead specify the desired timeslot by 
editing the ```dtstr``` variable in run_geo, where the timeslot is in 
YYYYmmddHHMM format.