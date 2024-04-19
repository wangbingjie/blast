#!/bin/bash
set -e

cd /mnt/data

mkdir -p cutout_cdn
mkdir -p sed_output
mkdir -p ghost_data
mkdir -p ghost_output
mkdir -p tns_staging
mkdir -p transmission
mkdir -p dustmaps
mkdir -p fsps
mkdir -p sbipp
mkdir -p sbipp_phot

mkdir -p /data/

# The creation of symlinks should error if there is a non-symlink
# file or folder where the symlink should be.
if [[ ! -L "/data/cutout_cdn" ]]; then
    ln -s /mnt/data/cutout_cdn   /data/cutout_cdn
fi
if [[ ! -L "/data/sed_output" ]]; then
    ln -s /mnt/data/sed_output   /data/sed_output
fi
if [[ ! -L "/data/ghost_data" ]]; then
    ln -s /mnt/data/ghost_data   /data/ghost_data
fi
if [[ ! -L "/ghost_output" ]]; then
    ln -s /mnt/data/ghost_output /ghost_output
fi
if [[ ! -L "/tns_staging" ]]; then
    ln -s /mnt/data/tns_staging  /tns_staging
fi
if [[ ! -L "/transmission" ]]; then
    ln -s /mnt/data/transmission /transmission
fi
if [[ ! -L "/dustmaps" ]]; then
    ln -s /mnt/data/dustmaps     /dustmaps
fi
if [[ ! -L "/fsps" ]]; then
    ln -s /mnt/data/fsps         /fsps
fi
if [[ ! -L "/sbipp" ]]; then
    ln -s /mnt/data/sbipp        /sbipp
fi
if [[ ! -L "/sbipp_phot" ]]; then
    ln -s /mnt/data/sbipp_phot   /sbipp_phot
fi
