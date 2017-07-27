pygaarst-scripts
================

This is a collection of useful scripts carrying out operations on geospatial and remote sensing data, some using the pygaarst library, some stand-alone.

Types of scripts
----------------

Scripts in scripts/ depend on pygaarst, those in standalone-scripts/ do not, but will depend on other Python libraries, such as gdal, pyproj, fiona...

Scripts in cw-researc/ are personal research scripts. They are not expected to 
be of direct use to anyone else, but represent things I've done with the 
libraries. Feel free to use as examples, but don't expect any particular
quality standards or compatibility.

Requirements
------------

pygaarst-scripts is written to run under Python 2.7 on a *nix environment. Linux, OS X or BSD should work equally well. Not tested under Windows. 

Python 3 support is planned but requires pygaarst to be ported to Python 3 first.

The following Python packages are required in scripts:

* pytz (for time zone arithmetic)

