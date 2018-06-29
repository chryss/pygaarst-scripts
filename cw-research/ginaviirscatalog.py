#!/usr/bin/env python
"""
Make a JSON catalog of VIIRS SDS granules

Chris Waigl, 2016-06-01
"""

from __future__ import print_function
import os
import sys
import glob
import json
import argparse
sys.path.append(os.path.join(
    os.path.expanduser('~'),
    "Dropbox/Research/satelliteremotesensing/firedetection"))
import viirstools as vt


# basedir = u'/Volumes/cwdata1/VIIRS/GINA/dds.gina.alaska.edu/NPP/viirs/'
basedir = u'/Volumes/cwdata1/VIIRS/GINA/mirror_script'
outdir = basedir
outname = u'viirsgranulecatalog.json'


def parse_arguments():
    """Parse arguments"""
    parser = argparse.ArgumentParser(description='generate scene catalog')
    parser.add_argument('-o', '--out', dest='outdir',
                        help='set outdir',
                        default=outdir)
    parser.add_argument('-d', '--dir', dest='datadir',
                        help='set data dir',
                        default=basedir)
    parser.add_argument('--patt', dest='globpattern',
                        help='pattern to select files',)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    if (args.datadir != basedir and
            args.outdir == basedir):
        args.outdir = args.datadir
    outpath = os.path.join(args.outdir, outname)
    try:
        with open(outpath) as data_file:
            data = json.load(data_file)
    except IOError:
        print("Datafile {} doesn't exist: creating new one.".format(outname))
        data = {}
    scenelist = None
    os.chdir(args.datadir)
    if args.globpattern is not None:
        scenelist = glob.glob(args.globpattern)
        scenelist = filter(os.path.isdir, scenelist)
    cata = vt.getgranulecatalog(args.datadir, scenelist=scenelist)
    data.update(cata)
    with open(outpath, 'w') as dest:
        try:
            dest.write(json.dumps(data, indent=2))
        except IOError as err:
            print(err)
            print("Dumping {} in working directory".format(outname))
            rescue = open(outname, 'w')
            rescue.write(json.dumps(data, indent=2))
