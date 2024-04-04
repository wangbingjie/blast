#!/bin/env bash
set -e

cd "$(dirname "$(readlink -f "$0")")"/..

PURGE_OPTION=$2

DOCKER_ARGS=""
case "${PURGE_OPTION}" in
  "--purge-all")
    DOCKER_ARGS="--volumes"
    echo "Purging all data volumes..."
  ;;
  "--purge-db")
    VOLUMES="blast_blast-db blast_django-static"
    echo "Purging Django database and static file volumes..."
  ;;
  "--purge-data")
    VOLUMES="blast_blast-data"
    echo "Purging astro data volume..."
  ;;
esac

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

docker volume rm ${VOLUMES}
