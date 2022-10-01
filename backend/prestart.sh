#! /usr/bin/env sh
set -e
# Do anything like wait for DB to migrate/startup here
# uvicorn will execute after this script runs
(cd /app && exec alembic upgrade head)
sleep 0.1
echo "prestart complete"