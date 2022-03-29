#!/bin/env bash
rm -r data/
docker compose -f docker/docker-compose.yml up --build
