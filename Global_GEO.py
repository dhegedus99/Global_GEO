"""DESCRIPTION ####

This is the main script for producing Global Geo-composites from 5 geostationary 
satellites: Goes East, Goes West, Himawari, MSG IODC (Indian Ocean Data Coverage)
and MSG FDS (Full Disk Service).

The script creates some temporary files:
- tif file of the processed data: once tiling is complete this is deleted
- return_dict_YYYYMMDDHH00.pkl file: dictionary containing all the processed data, 
so we can make sure we have processed all 5 datasets
WARNING: once processing is complete, the data from return_dict_YYYYMMDDHH00.pkl is
deleted and it will only contain a list of all datasets used. This would throw 
an error when trying to read in the pickle file as the script assumes a dictionary 
format. This error means no more processing is needed 

"""

from datetime import datetime # noqa: E402
import os, stat  # noqa: E402
import utils  # noqa: E402
import sys  # noqa: E402
from getopt import getopt
import matplotlib.pyplot as plt
import numpy as np
import subprocess
from osgeo import gdal, gdalconst
from glob import glob
import pickle
import re
import satpy
import shutil  # noqa: E402
import warnings  # noqa: E402
warnings.filterwarnings('ignore')
#os.environ["XRIT_DECOMPRESS_PATH"]='/home/users/'+os.environ['USER']+'/bin/xRITDecompress'


### Batch Specifications ###
batch=True
queue='short-serial'


### Path Specifications ###
options, operands = getopt(sys.argv[1:], "", ["outdir_top=", "idir_top=", "tmpdir=", "cachedir=", "pydir=", "logdir=", "XRIT_Decompress_path="])
for o,v in options:
    if o == "--outdir_top":
        topdir_remote = v
    if o == "--idir_top":
        idir_top = v
    if o == "--tmpdir":
        tmpdir = v
    if o == "--cachedir":
        cachedir = v
    if o == "--pydir":
        pydir = v
    if o == "--logdir":
        logdir = v
    if o == "--XRIT_Decompress_path":
        os.environ["XRIT_DECOMPRESS_PATH"] = v

        
### Datetime to be processed ###
if len(sys.argv) < 9:
    proc_dt = datetime.utcnow().replace(microsecond=0, second=0, minute=0)
else:
    dtstr = sys.argv[-1]
    try:
        proc_dt = datetime.strptime(dtstr, "%Y%m%d%H%M")
    except ValueError:
        raise ValueError("You must enter a processing date/time in format YYYYMMDDHHMM.")

print("Processing:", proc_dt)


### False Colour Composite specifications ###
# view zenith angle limits
vza_thresh_max = 80.
# name of composite in satpy
comp = 'natural_color_raw_with_night_ir'
# Limits on reflectance, sometimes these are exceeded due to calibration
# or high solar angle issues. Setting these prevents edge cases from 
# producing odd-looking output.
min_refl = 0
max_refl = 1


### Tiling Specifications ###
# Expected number of files in tile directory
expected_fnum = 2734
zoomlevs = '0-6'
tilesize = 512


### Directory structure ###
dirs = utils.DirStruct(tmpdir=tmpdir, cachedir=cachedir, idir_top=idir_top, logdir=logdir, pydir=pydir)


### Output file ###
output_dir_rsg = f'{topdir_remote}/{proc_dt.strftime("%Y/%m/%d")}/GLOBAL_GEO_{proc_dt.strftime("%Y%m%d%H%M")}_V1_00_FC/'
outf_name = f'{dirs.odir}/GLOBAL_GEO_{proc_dt.strftime("%Y%m%d%H%M")}_V1_00_FC.tif'


### Configure Satpy ###
satpy.config.set(cache_dir=dirs.cache_dir)
satpy.config.set(tmp_dir=dirs.idir_tmp)
satpy.config.set(cache_lonlats=True)
satpy.config.set(cache_sensor_angles=True)


### START OF PROCESSING ###


# Check if any data has been processed already
if os.path.exists(tmpdir+"return_dict"+proc_dt.strftime("%Y%m%d%H%M")+".pkl"):
    # If pickle file exists, some processing has been done already
    # Read in pickle file to check which data is already processed
    my_objects = [] 
    try:
        with open(tmpdir+'return_dict'+proc_dt.strftime("%Y%m%d%H%M")+'.pkl', 'rb') as f:
            while True:
                my_objects.append(pickle.load(f))
    except EOFError:
        pass
    except Exception as e: 
        print(e)
        print('File is corrupted/cannot be opened/pickling is throwing an error, restarting processing')
        os.remove(tmpdir+"return_dict"+proc_dt.strftime("%Y%m%d%H%M")+".pkl")
            
        with open(tmpdir+'return_dict'+proc_dt.strftime("%Y%m%d%H%M")+'.pkl','wb+') as f:
            pass
        return_dict={}
    try:
        return_dict = dict((key,d[key]) for d in my_objects for key in d)
    except TypeError:
        print('Processing is already done, temporary files already deleted.')
        print('Nothing to do, exiting script.')
        quit()
    print(return_dict.keys())
    if len(return_dict) <5:
        # Fill in gaps in processing for any missing data
        print("Not all data was used, restarting image generation.")
        ids=[]
        if not "fds" in return_dict.keys():
            job_name='gg_sev_fds'
            fds_id = utils.submit_fds(batch, job_name, proc_dt, queue, dirs, comp, vza_thresh_max)
            ids.append(fds_id)
        if not "ioc" in return_dict.keys():
            job_name='gg_sev_ioc'
            ioc_id = utils.submit_ioc(batch, job_name, proc_dt, queue, dirs, comp, vza_thresh_max)
            ids.append(ioc_id)
        if not "hi8" in return_dict.keys():
            job_name='gg_hi8'
            hi8_id = utils.submit_hi8(batch, job_name, proc_dt, queue, dirs, comp, vza_thresh_max)
            ids.append(hi8_id)
        if not "goes16" in return_dict.keys():
            job_name='gg_goes16'
            g16_id = utils.submit_g16(batch, job_name, proc_dt, queue, dirs, comp, vza_thresh_max)
            ids.append(g16_id)
        if not "goes18" in return_dict.keys():
            job_name='gg_goes18'
            g18_id = utils.submit_g18(batch, job_name, proc_dt, queue, dirs, comp, vza_thresh_max)
            ids.append(g18_id)
        job_name='gg_tif'
        tif_id = utils.submit_tif(batch, job_name, outf_name, proc_dt, queue, dirs, vza_thresh_max, min_refl, max_refl, ids)     
    else:
        # All the data has been processed and is in the pickle file
        if os.path.exists(output_dir_rsg):
            # If final output tiles all exist, no need to do any reprocessing
            print("Output files already exist on RSGNCEO.")
            my_objects = [] 
            try:
                with open(tmpdir+'return_dict'+proc_dt.strftime("%Y%m%d%H%M")+'.pkl', 'rb') as f:
                        while True:
                            my_objects.append(pickle.load(f))
            except EOFError:
                pass
            except Exception as e: 
                print(e)
                os.remove(tmpdir+"return_dict"+proc_dt.strftime("%Y%m%d%H%M")+".pkl")
            return_dict = dict((key,d[key]) for d in my_objects for key in d)
            # Delete temporary/cached files and only keep the list of processed data in the 
            # pickle file (to save storage space, but know not to reprocess)
            if (utils.totfiles(output_dir_rsg) >= expected_fnum) & (len(return_dict) ==5):
                with open(tmpdir+'return_dict'+proc_dt.strftime("%Y%m%d%H%M")+'.pkl', 'wb+') as f:
                    fcntl.lockf(f, fcntl.LOCK_EX)
                    pickle.dump(list(return_dict.keys()), f)
                    fcntl.lockf(f, fcntl.F_UNLCK)
                os.remove(glob(tmpdir,"*.nc"))
                os.remove(glob(tmpdir,proc_dt.strftime("%Y%m%d_%H%M")+"*.bz2"))
                os.remove(glob(outf_name))
                print('Deleting all temporary files, have everything we need')
                quit()
            else:
                print("Tiling has not finished, restarting now.")
                tif_id=''
                pass
        elif (os.path.exists(outf_name)) & (len(return_dict) ==5):
            # If temporary tif file exists, but tiling is not finished, only do tiling
            print("Output file exists, skipping image generation for", proc_dt)
            tif_id=''
            pass
        else:
            pass
else: 
    # If pickle file doesn't exist, create it
    with open(tmpdir+'return_dict'+proc_dt.strftime("%Y%m%d%H%M")+'.pkl','wb+') as f:
        pass
    # If pickle file doesn't exist, regenerate image just in case it's not complete
    print("Cannot find file specifying which data has been used, so repeating image generation.")
    job_name='gg_sev_fds'
    fds_id = utils.submit_fds(batch, job_name, proc_dt, queue, dirs, comp, vza_thresh_max)
    job_name='gg_sev_ioc'
    ioc_id = utils.submit_ioc(batch, job_name, proc_dt, queue, dirs, comp, vza_thresh_max)
    job_name='gg_hi8'
    hi8_id = utils.submit_hi8(batch, job_name, proc_dt, queue, dirs, comp, vza_thresh_max)
    job_name='gg_goes16'
    g16_id = utils.submit_g16(batch, job_name, proc_dt, queue, dirs, comp, vza_thresh_max)
    job_name='gg_goes18'
    g18_id = utils.submit_g18(batch, job_name, proc_dt, queue, dirs, comp, vza_thresh_max)
    ids = [fds_id, ioc_id, hi8_id, g16_id, g18_id]
    job_name='gg_tif'
    tif_id = utils.submit_tif(batch, job_name, outf_name, proc_dt, queue, dirs, vza_thresh_max, min_refl, max_refl, ids)
     
# Tiling   
if batch:
            job_name='gg_tiling'
            cmdbatch = 'sbatch --job-name='+job_name \
                +' -o '+logdir+'/'+job_name+proc_dt.strftime("%H%M")+'.log' \
                +' -e '+logdir+'/'+job_name+proc_dt.strftime("%H%M")+'.err' \
                +' --mem=10G'+' -p '+queue \
                +' --time=00:30:00'
            if tif_id:
                cmd = cmdbatch+ ' ' +'--dependency=afterany:'+tif_id
            else:
                cmd = cmdbatch
            cmd = cmd+' '+pydir+'tiling.py' \
                  + ' ' + '--outf_name='+ outf_name + ' ' + '--output_dir_rsg=' + output_dir_rsg +' ' \
                  +'--zoomlevs='+zoomlevs + ' ' + '--tilesize=' + str(tilesize)
            out = subprocess.check_output(cmd.split(' '), universal_newlines=True)
            m = re.search('Submitted batch job (?P<ID>\d+)',out)
            tile_id = m.group('ID')
            print('Tiling processing job submitted with ID: ',tile_id) 
        
else:
            cmd = 'python'
            cmd =cmd+' '+pydir+'tiling.py' \
                  + ' ' + '--outf_name='+ outf_name + ' ' + '--output_dir_rsg=' + output_dir_rsg +' ' \
                  +' '+'--zoomlevs='+zoomlevs + ' ' + '--tilesize=' + str(tilesize)
            os.system(cmd)


### END OF PROCESSING ###
