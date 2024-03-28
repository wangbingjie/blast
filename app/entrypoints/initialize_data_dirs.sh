#!/bin/bash
set -e

cd /mnt/data

mkdir -p cutout_cdn
mkdir -p sed_output
mkdir -p ghost_output
mkdir -p tns_staging
mkdir -p transmission
mkdir -p dustmaps
mkdir -p fsps
mkdir -p sbipp
mkdir -p sbipp_phot

mkdir -p /data/
ln -sf /mnt/data/cutout_cdn   /data/
ln -sf /mnt/data/sed_output   /data/
ln -sf /mnt/data/ghost_output /
ln -sf /mnt/data/tns_staging  /
ln -sf /mnt/data/transmission /
ln -sf /mnt/data/dustmaps     /
ln -sf /mnt/data/fsps         /
ln -sf /mnt/data/sbipp        /
ln -sf /mnt/data/sbipp_phot   /

