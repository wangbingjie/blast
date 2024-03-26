#!/usr/bin/env bash

rm -r data/ghost_output/*
rm -r data/database/*
rm -r data/test_database/*
rm -r data/tns_staging/*
rm -r app/static/*
rm -r app/rabbitmq_data/*

mv data/cutout_cdn/2010ag/ data/
mv data/cutout_cdn/2010ai/ data/
mv data/cutout_cdn/2010H/ data/
rm -r data/cutout_cdn/*
mv data/2010ag/ data/cutout_cdn/
mv data/2010ai/ data/cutout_cdn/
mv data/2010H/ data/cutout_cdn/

mv data/sed_output/2010H/ data/
rm -r data/sed_output/*
mv data/2010H data/sed_output/
