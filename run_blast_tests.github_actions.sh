#!/bin/env bash
rm -r data/test_database
docker compose -f docker/docker-compose.github_actions.yml up
