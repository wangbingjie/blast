#!/bin/env bash
set -e

PROFILE=$1
PURGE_OPTION=$2

ENV_FILE="env/.env.dev"
COMPOSE_ARGS=""
case "$PROFILE" in
  "")
    echo "ERROR: You must specify a profile (e.g. $0 slim_dev)"
    exit 1
    ;;
  test)
    COMPOSE_ARGS="--exit-code-from app_test"
    ;;
  ci)
    COMPOSE_ARGS="--exit-code-from app_ci"
    ENV_FILE="env/.env.ci"
    ;;
  slim_dev)
    COMPOSE_ARGS="--abort-on-container-exit"
    ;;
  *)
    COMPOSE_ARGS=""
    ;;
esac

COMPOSE_ARGS=""
PURGE_VOLUMES=""
case "${PURGE_OPTION}" in
  "")
    echo "Retaining all data volumes."
    ;;
  "--purge-all")
    COMPOSE_ARGS="--volumes"
    echo "Purging all data volumes..."
  ;;
  "--purge-db")
    PURGE_VOLUMES="blast_blast-db blast_django-static"
    echo "Purging Django database and static file volumes..."
  ;;
  "--purge-data")
    PURGE_VOLUMES="blast_blast-data"
    echo "Purging astro data volume..."
  ;;
  *)
    echo "ERROR: Invalid purge option."
    exit 1
    ;;
esac

COMPOSE_CONFIG=" --profile $PROFILE"
COMPOSE_CONFIG="${COMPOSE_CONFIG} --project-name blast"
COMPOSE_CONFIG="${COMPOSE_CONFIG} -f docker/docker-compose.yml"
COMPOSE_CONFIG="${COMPOSE_CONFIG} --env-file env/.env.default"
COMPOSE_CONFIG="${COMPOSE_CONFIG} --env-file ${ENV_FILE}"

export COMPOSE_CONFIG
export COMPOSE_ARGS
export PURGE_VOLUMES
