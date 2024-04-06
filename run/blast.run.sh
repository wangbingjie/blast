#!/bin/env bash

cd "$(dirname "$(readlink -f "$0")")"/..

# When bind mounting the app/ folder, for example
# in profiles slim_dev and full_dev, containers can
# fail if the file permissions are not globally readable.
chmod -R a+rX app/ 2>/dev/null

ENV_FILE="env/.env.dev"
case "$1" in
  test)
    DOCKER_ARGS="--exit-code-from app_test"
    ;;
  ci)
    DOCKER_ARGS="--exit-code-from app_ci"
    ENV_FILE="env/.env.ci"
    ;;
  slim_dev)
    DOCKER_ARGS="--abort-on-container-exit"
    ;;
  *)
    DOCKER_ARGS=""
    ;;
esac

# Clear any initialization check files
docker run --rm -it -v blast_blast-data:/mnt/data blast:dev rm -f /mnt/data/.initializing_db /mnt/data/.initializing_data

if [[ ! -f "env/.env.dev" ]]; then
  touch env/.env.dev
fi

set -x
docker compose \
  --profile $1 \
  --project-name blast \
  -f docker/docker-compose.yml \
  --env-file env/.env.default --env-file "${ENV_FILE}" \
  up --build ${DOCKER_ARGS}
