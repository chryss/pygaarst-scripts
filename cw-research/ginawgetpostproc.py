#!/usr/bin/env python
#
# 2016-08-17 -- cwaigl@alaska.edu (Chris Waigl)
# postprocess after getting VIIRS updates from GINA via mirror script

from __future__ import print_function, unicode_literals, division
import os
import shutil
import datetime as dt
import glob

NASDIR = '/Volumes/cwdata1/VIIRS/GINA/mirror_script'

if __name__ == '__main__':
    os.chdir(NASDIR)
    dirnames = glob.glob('npp*')
    dirnames = filter(os.path.isdir, dirnames)
    for dirname in dirnames:
        _, b, c = dirname.split('.')
        newname = dt.datetime.strftime(
            dt.datetime.strptime(b+c, '%y%j%H%M'), '%Y_%m_%d_%j_%H%M')
        if os.path.islink(newname):
            continue
        try:
            os.symlink(dirname, newname)
        except OSError as e:
            print("Could not link {} to {}: {}".format(newname, dirname, e))