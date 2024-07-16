#!/bin/env bash
set -e

cd "$(dirname "$(readlink -f "$0")")"/..

PROFILE=$1
PURGE_OPTION=$2

source run/get_compose_args.sh $PROFILE $PURGE_OPTION

if [[ ! -f "env/.env.dev" ]]; then
  touch env/.env.dev
fi

set -x
docker compose ${COMPOSE_CONFIG} down ${COMPOSE_ARGS}
set +x

if [[ "${PURGE_VOLUMES}x" != "x" ]]; then
  set -x
  docker volume rm ${PURGE_VOLUMES}
  set +x
fi
