#!/usr/local/env python

# 2015-05-01 -- cwaigl@alaska.edu (Chris Waigl)
# Fire detection: GINA download and sync script

from __future__ import print_function, unicode_literals, division
import os, sys
import argparse
import datetime as dt
import glob
import numpy as np
import seaborn as sns
from pygaarst import raster
from pygaarst import basemaputils as bu
from matplotlib import pyplot as plt
import fiona
from shapely.geometry import Polygon
from shapely.geos import TopologicalError
from descartes import PolygonPatch
from pprint import pprint

sys.path.append("/Users/chris/Dropbox/Research/satelliteremotesensing/firedetection")
import viirstools as vt

NASPATH = "/Volumes/cwdata1/VIIRS/GINA/dds.gina.alaska.edu/NPP/viirs"
VIZDIR = "visual"
TESTDIR = "testviz"
SCENELIST = "GINA_list.txt"
FILEPAT = 'SVM12_npp_*.h5'
VF = 'BorealAKForUAFSmoke.json'
VECTOROVERLAY = None        #ugly
if VF:
    VECTOROVERLAY = os.path.join(
        os.path.split(
            os.path.realpath(__file__))[0], VF)
MINFRAC = 0.01   # minimum fractional area for keeping a sub-scene

def printOpenFiles(openfiles):
    print("### %d OPEN FILES:" % (len(openfiles), ))
    pprint([f.x for f in openfiles])

def parse_arguments():
    """Parse arguments"""
    parser = argparse.ArgumentParser(description='Produce visualizations of extent of scenes')
    parser.add_argument('-o', dest='overwrt', 
        help='overwrite existing images',
        action='store_true')
    parser.add_argument('--testdir',
        help='use a single directory to test')
    parser.add_argument('--ov', dest='overlayvector',
        help="overlay vector file",
        default=VECTOROVERLAY)
    parser.add_argument('--dir', dest='archivedir',
        help="directory containing file archive",
        default=NASPATH)
    parser.add_argument('--num', action='store_true',
        help="print numbers on plot")
    parser.add_argument('--debug', action='store_true',
        help="debug mode")
    return parser.parse_args()

def read_items(filepath):
    """Turns a plain text file file with one item/line into an iterator"""
    with open(filepath, "rU") as src:
        for line in src:
            yield line.strip()

def generate_viz(scene, outdir, 
        fig, mm, 
        numbers=False,
        debug=False,
        datadir=None,
        overwrite=False):

    if debug:
        import __builtin__
        openfiles = set()
        oldfile = __builtin__.file
        class newfile(oldfile):
            def __init__(self, *args):
                self.x = args[0]
                print("### OPENING %s ###" % str(self.x) )
                oldfile.__init__(self, *args)
                openfiles.add(self)

            def close(self):
                print("### CLOSING %s ###" % str(self.x))
                oldfile.close(self)
                openfiles.remove(self)
        oldopen = __builtin__.open
        def newopen(*args):
            return newfile(*args)
        __builtin__.file = newfile
        __builtin__.open = newopen

    figname = os.path.split('{}_plot.png'.format(scene))[-1]
    if os.path.exists(os.path.join(outdir, figname)): 
        if overwrite:
            print("{} exists, overwriting.".format(figname))
        else:
            print("{} exists, skipping.".format(figname))
            return
    ax = fig.gca()
    if not datadir:
        datadir = os.path.join(NASPATH, scene, 'sdr')
    elif os.path.exists(os.path.join(datadir, scene, 'sdr')):
        datadir = os.path.join(datadir, scene, 'sdr')
    else:
        datadir = os.path.join(datadir, scene)
    print("Working on data in {}.".format(datadir))
    if not os.path.isdir(datadir):
        print("{} is not a directory, skipping.".format(datadir))
        return
    os.chdir(datadir)
    testfiles = glob.glob(FILEPAT)
    print("Working with {} data files.".format(len(testfiles)))
    testfiles.sort()
    current_palette = sns.husl_palette(n_colors=len(testfiles), h=.2, l=.4, s=.9)
    totalfrac = 0.0
    plotobj = []
    plottexts = []
    for idx, tf in enumerate(testfiles):
        print('{}: {}'.format(idx, tf))
        try:
            tsto = raster.VIIRSHDF5(tf)
        except IOError as err:
            print("Error opening file {}: {}.".format(tf, err))
            print("Aborting plot for scene {}.".format(datadir))
            return
        edgelons, edgelats = vt.getedge(tsto)
        x, y = mm(edgelons, edgelats)
        contour = Polygon(zip(x, y))
        try:
            intersect = contour.intersection(poly)
            fraction = intersect.area/poly.area
        except TopologicalError:
            fraction = 0
        totalfrac += fraction*100
        print("Intersection as fraction of AOI: {}".format(fraction))
        if fraction > MINFRAC:
            size = 10
            alpha = 1.000
            color = current_palette[idx]
            plotobj.append(ax.plot(x, y, zorder=15, 
                linewidth=3, color=color, alpha=alpha))
        else:
            size = 5
            alpha = .4
            color = current_palette[idx]
            plotobj.append(ax.scatter(x, y, size, zorder=25, 
                marker='o', color=color, alpha=alpha))
        if numbers:
            midx = 0.5 * (min(x) + max(x))
            midx = max(min(midx, mm.xmax), mm.xmin)
            midy = 0.5 * (min(y) + max(y))
            midy = max(min(midy, mm.ymax), mm.ymin)
            plottexts.append(
                ax.text(midx, midy, str(idx), 
                color=current_palette[idx],
                weight='bold',
                fontsize=20
                ))
        tsto.close()
    if debug:
        printOpenFiles(openfiles)
    ax.set_title("{}: {:.2f}% of AOI".format(scene, totalfrac))
    print("Outdir variable: {}".format(outdir))
    print("Figname variable: {}".format(figname))
    imgpath = os.path.join(outdir, figname)
    print("Saving figure to {}.".format(imgpath))
    fig.savefig(imgpath)
    # clean up base plot
    for item in plotobj:
        try:
            for subobj in item:
                try:
                    ax.lines.remove(subobj)
                except ValueError:
                    pass
        except TypeError:   # not a sequence    
            try: 
                ax.collections.remove(item)
            except ValueError:
                pass
    for item in plottexts:
        ax.texts.remove(item)

def render_poly(mmap, fig, record, transform=True):
    """Given matplotlib axes, a map and a record, adds the record as a patch
    and returns the axes so that reduce() can accumulate more
    patches."""
    if transform:
        record = bu.maptransform(mmap, record)
    fig.gca().add_patch(
        PolygonPatch(record['geometry'], 
            fc='orange', ec='orange', alpha=0.5, zorder=11))
    return fig

if __name__ == '__main__':
    args = parse_arguments()
    # generate base map 
    print("Generating base map")
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111)
    mm = bu.map_interiorAK(width=5000000, height=5000000, resolution='l')
    # add polygon overly
    print("Overlaying polygon")
    if args.overlayvector:
        print("Overlaying vector data.")
        with fiona.open(args.overlayvector, 'r') as source:
            for record in source:
                record = bu.maptransform(mm, record)
                poly = Polygon(record['geometry']['coordinates'][0])
                fig = render_poly(mm, fig, record, transform=False)
    if args.testdir:
        outdir = os.path.join(args.archivedir, TESTDIR)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        slug = dt.datetime.utcnow().strftime('%Y%m%d%H%M%S')
        if os.path.isdir(args.testdir):
            datadir = os.path.join(args.testdir, 'sdr')
        else: 
            datadir = os.path.join(args.archivedir, args.testdir, 'sdr')
        generate_viz(
            'test_{}'.format(slug), 
            outdir, fig, mm, 
            datadir=datadir,
            numbers=args.num,
            debug=args.debug)
    else:
        if os.path.exists(os.path.join(args.archivedir, SCENELIST)):
            dirlist = read_items(os.path.join(args.archivedir, SCENELIST))
        else:
            dirlist = glob.glob(os.path.join(args.archivedir, "201[0-9]_*"))
            dirlist = filter(os.path.isdir, dirlist)
            dirlist.sort()
        for scene in dirlist:
            outdir = os.path.join(args.archivedir, VIZDIR)
            print("scene variable: {}".format(scene))
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            print("Writing to {}.".format(outdir))
            generate_viz(
                scene, outdir, fig, mm, 
                datadir=args.archivedir,
                overwrite=args.overwrt,
                numbers=args.num,
                debug=args.debug)
