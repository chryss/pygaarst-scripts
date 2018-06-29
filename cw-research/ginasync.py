#!/usr/local/env python

# 2015-05-01 -- cwaigl@alaska.edu (Chris Waigl)
# Fire detection: GINA download and sync script

from __future__ import print_function, unicode_literals, division
import os
import sys
import re
import argparse
import datetime as dt
import shutil
import ftputil

NASPATH = "/Volumes/cwdata1/VIIRS/GINA/dds.gina.alaska.edu/NPP/viirs"
FTPDOMAIN = "dds.gina.alaska.edu"
FTPU = 'anonymous'
FTPP = 'ftppass'
GINAPATH = 'NPP/viirs'
SCENEPAT = r'\d{4}_\d{2}_\d{2}_\d+_\d{4}'
SCREGEX = re.compile(SCENEPAT)
GENERICFILES = set(['.listing', '.DS_Store'])
GINALISTFN = 'GINA_list.txt'

LOCALWORK = True
REMOTEWORK = True
CLEANUP = False
WRITEDIRS = True


def parse_arguments():
    """Parse arguments"""
    parser = argparse.ArgumentParser(
        description='Sync VIIRS GINA with NAS storage')
    parser.add_argument(
        '--lc', dest='cleanup',
        help='Perform local clean-up and rewrite index',
        action='store_true')
    parser.add_argument(
        '--nd', dest='nodownload',
        help='Don\'t download new files',
        action='store_true')
    parser.add_argument(
        '-o', dest='overwrt',
        help='overwrite existing directories',
        action='store_true')
    parser.add_argument(
        '--reb', dest='rebuild',
        help='check and rebuild index of existing scenes, then exit',
        action='store_true')
    parser.add_argument('--retrievedir', help='retrieve one single directory')
    return parser.parse_args()


def is_valid_scenedir(dirstring):
    """Check is a directory name is a valid scene directory"""
    if not os.path.isdir(os.path.join(NASPATH, dirstring)):
        return False
    elif not SCREGEX.match(dirstring):
        return False
    return True


def localcleanup():
    cleanup = []
    scenedirnames = filter(is_valid_scenedir, os.listdir(NASPATH))
    for subdir in scenedirnames:
        subsubdirs = os.listdir(os.path.join(NASPATH, subdir))
        if 'sdr' not in subsubdirs:
            print("{}: no sdr dir, removing".format(os.path.join(NASPATH, subdir)))
            cleanup.append(os.path.join(NASPATH, subdir))
            continue
        elif 'edr' in subsubdirs:
            print("{} will be removed".format(os.path.join(NASPATH, subdir, 'edr')))
            cleanup.append(os.path.join(NASPATH, subdir, 'edr'))
        else:
            sdrdirs = os.listdir(os.path.join(NASPATH, subdir, 'sdr'))
            if set(sdrdirs).issubset(GENERICFILES):
                print("{}: sdr dir is empty, removing".format(
                    os.path.join(NASPATH, subdir)))
                cleanup.append(os.path.join(NASPATH, subdir))
    if CLEANUP:
        for dirname in cleanup:
            shutil.rmtree(dirname)


def _dirname_is_valid(testname, includenames, excludenames):
    """includenames and excludenames are sequence types. If either is empty,
    nothing is excluded and/or all is included"""
    if (
        (not includenames or testname in includenames) and
        testname not in excludenames
    ):
        return True
    else:
        return False


def remotedownload(excludedirs, includedirs=[], overwrite=False):
    os.chdir(NASPATH)
    if overwrite:    # we exclude the excludedirs list
        excludedirs = []
    with ftputil.FTPHost(FTPDOMAIN, FTPU, FTPP) as host:
        host.chdir(GINAPATH)
        names = host.listdir(host.curdir)
        for name in names:
            if _dirname_is_valid(name, includedirs, excludedirs):
                host.chdir(name)
                if 'sdr' in host.listdir(host.curdir):
                    host.chdir('sdr')
                    if len(host.listdir(host.curdir)) > 0:
                        if not os.path.exists(name + '/sdr'):
                            os.makedirs(name + '/sdr')
                        os.chdir(name + '/sdr')
                        excludefiles = []
                        if not overwrite:
                            excludefiles = os.listdir('.')
                        for fn in host.listdir(host.curdir):
                            if host.path.isfile(fn) and not fn in excludefiles:
                                print("Downloading {}".format(os.path.join(os.getcwd(), fn)))
                                host.download(fn, fn)
                        os.chdir(NASPATH)
                    host.chdir('..')
                host.chdir('..')


def rebuildscenelist():
    scenedirnames = filter(is_valid_scenedir, os.listdir(NASPATH))
    scenedirnames.sort()
    filelistpath = os.path.join(NASPATH, GINALISTFN)
    writenew = False
    if os.path.isfile(filelistpath):
        with open(filelistpath, 'rU') as src:
            filelist = [dirname.strip() for dirname in src]
            filelist.sort()
        missing = [dn for dn in scenedirnames if dn not in filelist]
        extras = [dn for dn in filelist if dn not in scenedirnames]
        if missing or extras:
            if missing:
                print("There are scene directories that are not registered. Adding:")
                print('\n'.join(missing))
            if extras:
                print("There are registered directories that are not present. Removing:")
                print('\n'.join(extras))
            infix = dt.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            prefix, suffix = os.path.splitext(GINALISTFN)
            newname = prefix + infix + suffix
            print("Moving {} to {}".format(
                GINALISTFN, newname
            ))
            shutil.move(filelistpath, os.path.join(NASPATH, newname))
            writenew = True
    else:
        print("{} does not exist. Generating it.".format(GINALISTFN))
        writenew = True
    if writenew:
        with open(filelistpath, 'w') as dst:
            dst.write('\n'.join(scenedirnames))
    else:
        print("Index up to date -- nothing to do.")


if __name__ == '__main__':
    args = parse_arguments()
    if args.rebuild:
        print("Checking and rebuilding index.")
        rebuildscenelist()
        sys.exit()
    if args.cleanup:
        print("Performing cleanup before any other options.")
        localcleanup()
        rebuildscenelist()
    if args.retrievedir:
        remotedownload(
            [], includedirs=[args.retrievedir], overwrite=args.overwrt)
        sys.exit()
    if not args.nodownload:
        try:
            localdirs = [
                fn.strip() for fn in open(
                    os.path.join(NASPATH, GINALISTFN), 'rU').readlines()]
        except IOError:
            localdirs = []
        remotedownload(localdirs, overwrite=args.overwrt)
        localcleanup()
        rebuildscenelist()
