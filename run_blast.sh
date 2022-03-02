#!/bin/env bash

rm -r data/database
docker compose -f docker/docker-compose.yml up
