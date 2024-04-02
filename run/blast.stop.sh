#!/bin/env bash

cd "$(dirname "$(readlink -f "$0")")"/..

PURGE=$2

DOCKER_ARGS=""
if [[ "${PURGE}" == "--purge" ]]; then
  DOCKER_ARGS="--remove-orphans --volumes"
  echo "Purging Docker data volumes..."
  set -x
  rm -f docker/initialized/.initialized
  set +x
fi

docker compose --profile $1 \
  -f docker/docker-compose.yml \
  --project-name blast \
  --env-file env/.env.dev \
  down ${DOCKER_ARGS}
