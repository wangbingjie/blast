#!/bin/env bash

cd "$(dirname "$(readlink -f "$0")")"/..

# When bind mounting the app/ folder, for example
# in profiles slim_dev and full_dev, containers can
# fail if the file permissions are not globally readable.
chmod -R a+rX app/ 2>/dev/null

case "$1" in
  test) DOCKER_ARGS="--exit-code-from app_test" ;;
    ci) DOCKER_ARGS="--exit-code-from app_ci"   ;;
     *) DOCKER_ARGS="--abort-on-container-exit" ;;
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
  up --build ${DOCKER_ARGS}
