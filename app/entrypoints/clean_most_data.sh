#!/usr/bin/env bash

rm -r data/ghost_output/*
rm -r data/database/*
rm -r data/test_database/*
rm -r data/tns_staging/*
rm -r app/static/*
rm -r app/rabbitmq_data/*

mv data/sed_output/2010H/ data/
rm -r data/sed_output/*
mv data/2010H data/sed_output/
