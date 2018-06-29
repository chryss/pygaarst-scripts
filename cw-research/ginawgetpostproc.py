#!/usr/bin/env python
#
# 2016-08-17 -- cwaigl@alaska.edu (Chris Waigl)
# postprocess after getting VIIRS updates from GINA via mirror script

from __future__ import print_function, unicode_literals, division
import os
import argparse
import datetime as dt
import glob

NASDIR = '/Volumes/cwdata1/VIIRS/GINA/mirror_script'


def parse_arguments():
    """Parse arguments"""
    parser = argparse.ArgumentParser(description='generate scene catalog')
    parser.add_argument(
        '-d', dest='datadir',
        help='set data dir',
        default=NASDIR)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    os.chdir(args.datadir)
    dirnames = glob.glob('npp*')
    dirnames = filter(os.path.isdir, dirnames)
    for dirname in dirnames:
        dummy = dirname.split('.')
        b = dummy[1]
        c = dummy[2][:4]
        newname = dt.datetime.strftime(
            dt.datetime.strptime(b + c, '%y%j%H%M'), '%Y_%m_%d_%j_%H%M'
        )
        if os.path.islink(newname):
            continue
        try:
            os.symlink(dirname, newname)
        except OSError as e:
            print("Could not link {} to {}: {}".format(newname, dirname, e))
