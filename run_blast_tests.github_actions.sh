#!/bin/env bash
docker compose -f docker/docker-compose.github_actions.yml up --exit-code-from app
