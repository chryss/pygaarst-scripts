#!/usr/bin/env python
"""
Make a JSON catalog of VIIRS SDS granules

Chris Waigl, 2016-06-01
"""

import os
import sys
import json
sys.path.append("/Users/chris/Dropbox/Research/satelliteremotesensing/firedetection")
import viirstools as vt

basedir = u'/Volumes/cwdata1/VIIRS/GINA/dds.gina.alaska.edu/NPP/viirs/'
outdir = basedir 
outname = u'viirsgranulecatalog.json'

cata = vt.getgranulecatalog(basedir)
with open(os.path.join(outdir, outname), 'w') as dest:
    dest.write(json.dumps(cata, indent=2))