
    set -eo pipefail

    bash entrypoints/wait-for-it.sh ${DATABASE_HOST}:${DATABASE_PORT} --timeout=0
    bash entrypoints/wait-for-it.sh ${WEB_SERVER_HOST}:${WEB_SERVER_PORT} --timeout=0

    INIT_CHECK_FILE=/app/static/.initialized
    if [[ ! -f "${INIT_CHECK_FILE}" ]]; then
      echo "\"${INIT_CHECK_FILE}\" not found. Running initialization script..."
      python init.py
      touch "${INIT_CHECK_FILE}"
    else
      echo "Application already initialized (\"${INIT_CHECK_FILE}\" exists)."
    fi

    echo "Starting server..."
    gunicorn app.wsgi --timeout 0 --bind 0.0.0.0:${WEB_APP_PORT} --workers=${GUNICORN_WORKERS:=1}
