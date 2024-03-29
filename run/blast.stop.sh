#!/bin/env bash

cd "$(dirname "$(readlink -f "$0")")"/..

docker compose --profile $1 --project-name blast -f docker/docker-compose.yml --env-file env/.env.dev down
