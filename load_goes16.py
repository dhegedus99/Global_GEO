#!/usr/bin/env python
import sys
sys.path.append('/home/users/dhegedus/Global_GEO/')
import utils
from getopt import getopt
from osgeo import gdal, gdalconst
from datetime import datetime
import pickle 
import fcntl
import time
import satpy
import warnings  # noqa: E402
warnings.filterwarnings('ignore')

options, operands = getopt(sys.argv[1:], "", ["idir_tmp=", "proc_dt=", "return_dict=", "comp=", 
                                              "vza_thresh_max=", "resampler=" ,"cache_dir="])
for o,v in options:
    if o == "--idir_tmp":
        idir_tmp = v
    if o == "--proc_dt":
        proc_dt = datetime.strptime(v, "%Y%m%d%H%M")
    if o == "--comp":
        comp = v
    if o == "--return_dict":
        return_dict = v
    if o == "--vza_thresh_max":
        vza_thresh_max = float(v)
    if o == "--resampler":
        resampler = v
    if o == "--cache_dir":
        cache_dir = v

satpy.config.set(cache_dir=cache_dir)
satpy.config.set(tmp_dir=idir_tmp)
        
proj_str, extent, targ_srs = utils.setup_global_area(res=0.03)

worp_opts = gdal.WarpOptions(width=targ_srs.width,
                                height=targ_srs.height,
                                outputType=gdal.GDT_Float32,
                                dstSRS=proj_str,
                                dstNodata=-999.,
                                outputBounds=extent,
                                format="vrt",
                                resampleAlg=gdalconst.GRA_Bilinear,
                                multithread=True)
return_dict= {}     
utils.load_goes(idir_tmp, proc_dt, return_dict, comp, vza_thresh_max, resampler, 'goes16', worp_opts)

#utils.rem_old_files(idir_tmp, proc_dt)

with open(idir_tmp+'return_dict'+proc_dt.strftime("%Y%m%d%H%M")+'.pkl', 'ab+') as f:
    print(time.ctime())
    fcntl.lockf(f, fcntl.LOCK_EX)
    pickle.dump(return_dict, f)
    fcntl.lockf(f, fcntl.F_UNLCK)
    print(time.ctime())
        
#with open(scratch_dir+'seviri_dict.pkl', 'rb') as f:
#    loaded_dict = pickle.load(f)