#!/bin/env bash
bash wait-for-it.sh 0.0.0.0:${WEB_APP_PORT} --timeout=0 &&
python3 run_batch.py /input.csv