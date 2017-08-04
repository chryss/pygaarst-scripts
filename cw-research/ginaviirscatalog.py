#!/usr/bin/env python
"""
Make a JSON catalog of VIIRS SDS granules

Chris Waigl, 2016-06-01
"""

import os
import sys
import glob
import json
import argparse
sys.path.append("/Users/chris/Dropbox/Research/satelliteremotesensing/firedetection")
import viirstools as vt

#basedir = u'/Volumes/cwdata1/VIIRS/GINA/dds.gina.alaska.edu/NPP/viirs/'
basedir = u'/Volumes/cwdata1/VIIRS/GINA/mirror_script'
outdir = basedir 
outname = u'viirsgranulecatalog.json'

def parse_arguments():
    """Parse arguments"""
    parser = argparse.ArgumentParser(description='generate scene catalog')
    parser.add_argument('-o', dest='outdir', 
        help='set outdir',
        default=outdir)
    parser.add_argument('-d', dest='datadir',
        help='set data dir',
        default=basedir)
    parser.add_argument('--patt', dest='globpattern',
        help='pattern to select files',)
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    outpath = os.path.join(args.outdir, outname)
    data = {}
    if os.path.exists(outpath):
        with open('outpath') as data_file:    
            data = json.load(data_file)
    scenelist = None
    os.chdir(args.datadir)
    if args.globpattern is not None:
        scenelist = glob.glob(args.globpattern)
        scenelist = filter(os.path.isdir, scenelist)
    cata = vt.getgranulecatalog(args.datadir, scenelist=scenelist)
    data.update(cata)
    with open(outpath, 'w') as dest:
        dest.write(json.dumps(data, indent=2))