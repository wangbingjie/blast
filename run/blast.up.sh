#!/bin/env bash
set -e

cd "$(dirname "$(readlink -f "$0")")"/..

# When bind mounting the app/ folder, for example
# in profiles slim_dev and full_dev, containers can
# fail if the file permissions are not globally readable.
# chmod -R a+rX app/ 2>/dev/null

if [[ ! -f "env/.env.dev" ]]; then
  touch env/.env.dev
fi

PROFILE=$1
source run/get_compose_args.sh $PROFILE

set -x
docker compose ${COMPOSE_CONFIG} up ${COMPOSE_ARGS}
