#!/bin/env bash
rm -r data/test_database
docker compose -f docker-compose.test.yml up