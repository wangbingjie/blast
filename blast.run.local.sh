#!/bin/env bash

rm -r data/database
rm -r cutout_cdn/
docker compose -f docker/docker-compose.yml up --build
