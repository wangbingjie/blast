#!/bin/env bash
bash app/entrypoints/clean_data.sh
docker compose -f docker/docker-compose.test.yml up --exit-code-from app
