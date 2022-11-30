#! /usr/bin/env sh
set -e

DEFAULT_MODULE_NAME=demo.main

MODULE_NAME=${MODULE_NAME:-$DEFAULT_MODULE_NAME}
VARIABLE_NAME=${VARIABLE_NAME:-app}
export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8883}
LOG_LEVEL=${LOG_LEVEL:-info}

# Run the pre-start script to trigger Alembic migration and other pre-start actions
/bin/bash prestart.sh

# Start Uvicorn with live reload
exec uvicorn --reload --host $HOST --port $PORT --log-level $LOG_LEVEL "$APP_MODULE"
