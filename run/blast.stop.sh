#!/bin/env bash

cd "$(dirname "$(readlink -f "$0")")"/..

PURGE=$2

DOCKER_ARGS=""
if [[ "${PURGE}" == "--purge" ]]; then
  DOCKER_ARGS="--remove-orphans --volumes"
  echo "Purging Docker data volumes..."
  set -x
  # rm -f docker/initialized/.initialized
  # rm -f /mnt/data/.initializing_data
  # rm -f /mnt/data/.initializing_db
  set +x
fi

EXTRA_ENV=""
if [[ -f "env/.env.dev" ]]; then
  EXTRA_ENV="--env-file env/.env.dev"
fi

set -x
docker compose \
  --profile $1 \
  --project-name blast \
  -f docker/docker-compose.yml \
  --env-file env/.env.default ${EXTRA_ENV} \
  down ${DOCKER_ARGS}
