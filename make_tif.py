#!/usr/bin/env python
import sys
sys.path.append('/home/users/dhegedus/Global_GEO/')
import utils
from getopt import getopt
from osgeo import gdal, gdalconst
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import pickle 
import warnings  # noqa: E402
import fcntl
import time
warnings.filterwarnings('ignore')


options, operands = getopt(sys.argv[1:], "", ["outf_name=", "tmpdir=", "proc_dt=", 
                                              "vza_thresh_max=", "min_refl=", "max_refl="])
print(options)
for o,v in options:
    if o == "--outf_name":
        outf_name = v
    if o == "--proc_dt":
        proc_dt = datetime.strptime(v, "%Y%m%d%H%M")
    if o == "--tmpdir":
        tmpdir = v
    if o == "--vza_thresh_max":
        print(float(v))
        vza_thresh_max = float(v)
    if o == "--min_refl":
        min_refl = float(v)
    if o == "--max_refl":
        max_refl = float(v)

my_objects = [] 
try:                
    with open(tmpdir+'return_dict'+proc_dt.strftime("%Y%m%d%H%M")+'.pkl', 'rb') as f:
        while True:
            my_objects.append(pickle.load(f))
except EOFError:
            pass
            
return_dict = dict((key,d[key]) for d in my_objects for key in d)

for key in return_dict:
    gt = return_dict[key][2]
    sr = return_dict[key][3]

print(return_dict.keys())      
vza_frac_all = [x[1] for x in return_dict.values()]
final_vza_frac = utils.create_vza_frac(tuple(vza_frac_all), vza_thresh_max)
proj_str, extent, targ_srs = utils.setup_global_area(res=0.03)
# Compute the final output RGB
out_rgb_arr = np.zeros((targ_srs.height, targ_srs.width,3))
print(out_rgb_arr.shape)
i = 0
for key in return_dict:
    out_rgb_arr = out_rgb_arr + final_vza_frac[:, :, i].reshape(return_dict[key][0].shape[0], return_dict[key][0].shape[1], 1) * return_dict[key][0]
    i = i+1
#plt.figure()
#plt.imshow(out_rgb_arr)
#plt.show()
out_rgb_arr[np.where((out_rgb_arr==[0,0,0]).all(axis=2))] = [255,255,255]                    
out_rgb = utils.norm_output(out_rgb_arr, max_refl, min_refl)           
utils.save_img_tiff(out_rgb, outf_name, gt, sr, gdal.GDT_Byte)
utils.rem_old_files(tmpdir, proc_dt)


if len(return_dict) ==5:
    with open(tmpdir+'return_dict'+proc_dt.strftime("%Y%m%d%H%M")+'.pkl', 'wb+') as f:
        print(time.ctime())
        fcntl.lockf(f, fcntl.LOCK_EX)
        pickle.dump(list(return_dict.keys()), f)
        fcntl.lockf(f, fcntl.F_UNLCK)
        print(time.ctime())