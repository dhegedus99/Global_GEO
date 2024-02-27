#!/usr/bin/env python
import gdal2tiles  # noqa: E402
from getopt import getopt
import sys
import os

options, operands = getopt(sys.argv[1:], "", ["outf_name=", "output_dir_rsg=", 
                                              "zoomlevs=", "tilesize="])
print(options)
for o,v in options:
    if o == "--outf_name":
        outf_name = v
    if o == "--output_dir_rsg":
        output_dir_rsg = v
    if o == "--zoomlevs":
        zoomlevs = v
    if o == "--tilesize":
        tilesize = int(v)

os.makedirs(output_dir_rsg, exist_ok=True)
try: 
    gdal2tiles.generate_tiles(outf_name, output_dir_rsg, zoom=zoomlevs, nb_processes=30, tile_size=tilesize,
                                  resume=False, webviewer='none')
                                  
except Exception as e:
        print("Error making tiles")
        print(e)
                                  
# This method uses the external gdal function
        #gdal_proc = ['/gws/smf/j04/nceo_generic/Software/miniconda3/bin/python',
        #            '-u', '/gws/smf/j04/nceo_generic/Software/miniconda3/bin/gdal2tiles.py', 
        #            '--resampling=bilinear',
        #            '--zoom=0-7',
        #            '--resume',
        #            '--tilesize=256',
        #            '--webviewer=none',
        #            outf_name,
        #            output_dir_rsg,
        #            '--processes=20']
        #subprocess.call(gdal_proc)