#! /usr/bin/env sh
# stop execution instantly on non-zero status. This is to know location of error
set -e

RANDOM_STRING="random_string_was_not_generated!!"
STRING_LENGTH=32

# Function to generate a STRING_LENGTH string of characters
rando_string() {
    RANDOM_STRING=$(tr -dc 'A-Za-z0-9!#$%&'\''()*+,-./:;<=>?@[\]^_`{|}~' </dev/urandom | head -c $STRING_LENGTH)
}

# Function to generate viable postgres username which must start with a letter, @, _, or #
# For simplicity, simply make the whole username STRING_LENGTH valid starting characters
rando_user() {
  RANDOM_STRING=$(tr -dc 'A-Za-z@_#' </dev/urandom | head -c $STRING_LENGTH)
}

# Output filenames
ENV_FILE="./.env"
TEST_ENV_FILE="./backend/.test.env"

# Used to modify pytest and logging behavior within the FastAPI and SQLAlchemy services
DEBUG="false"

# Used by FastAPI and Pydantic BaseSettings ingest
API_PORT="8883"
PROJECT_NAME="demo_project"
PROJECT_VERSION="0.1.0"
BACKEND_CORS_ORIGINS="[\"http://localhost:8000\",\"https://localhost:8000\",\"http://localhost\",\"https://localhost\"]"
HASH_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES="30"
DEFAULT_EMAIL="brent-stone@github.com"

POSTGRES_USER="demo_pg"
POSTGRES_DB="demo_pg"
# These following settings are used by FastAPI API layer under core > config.py
######## WARNING ########
# Ensure \backend\.test.env used by pytest uses POSTGRES_SERVER value of localhost or IP
# of running postgres container instead of using a docker service alias like db.
POSTGRES_SERVER="db"
POSTGRES_PORT="5432"

# .test.env specific settings for pytest and local development
TEST_DEBUG="true"
TEST_POSTFIX="_test"
TEST_POSTGRES_SERVER="localhost"

# Redis Settings
REDIS_PORT="6379"
REDIS_HOST="redis"
REDIS_DB=${POSTGRES_SERVER}
TEST_REDIS_HOST="localhost"

# Generate viable random values for the user/pass & encryption environment variables
rando_user;
RANDOM_USER=${RANDOM_STRING}
rando_string
RANDOM_SECRET_STR=${RANDOM_STRING}
rando_string
RANDOM_POSTGRES_PW=${RANDOM_STRING}
rando_string
RANDOM_REDIS_PW=${RANDOM_STRING}


# Check if 'prod' .env file already exists
if [ -f $ENV_FILE ]; then
  echo "$ENV_FILE file already exists. To reset, remove it then re-run this script."
# If not, initialize it with new key:value pairs
else
  # Create the .env file
  touch $ENV_FILE

  # Write to the file
  {
    echo "# FastAPI Settings";
    echo "DEBUG=${DEBUG}";

    echo "API_PORT=${API_PORT:-$API_PORT}";
    echo "PROJECT_NAME=${PROJECT_NAME}";
    echo "PROJECT_VERSION=${PROJECT_VERSION}";
    echo "DEFAULT_EMAIL=${DEFAULT_EMAIL}";
    echo "HASH_ALGORITHM=${HASH_ALGORITHM}";
    echo "ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}";
    echo "BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}";
    echo "SECRET_KEY=${SECRET_KEY:-$RANDOM_SECRET_STR}";

    echo "# Postgres Settings (also used by FastAPI)";
    echo "POSTGRES_USER=${POSTGRES_USER:-$RANDOM_USER}";
    echo "POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-$RANDOM_POSTGRES_PW}";
    echo "POSTGRES_DB=${POSTGRES_DB:-$POSTGRES_DB}";
    echo "POSTGRES_SERVER=${POSTGRES_SERVER:-$POSTGRES_SERVER}";
    echo "POSTGRES_PORT=${POSTGRES_PORT:-$POSTGRES_PORT}";

    echo "# Redis (Celery) Settings";
    echo "REDIS_HOST=${REDIS_HOST:-$REDIS_HOST}";
    echo "REDIS_PASSWORD=${REDIS_PASSWORD:-$RANDOM_REDIS_PW}";
    echo "REDIS_PORT=${REDIS_PORT:-$REDIS_PORT}";
    echo "REDIS_DB=${REDIS_DB:-$REDIS_DB}";
    echo "CELERY_BROKER_URL=redis://${REDIS_HOST:-$REDIS_HOST}:${REDIS_PORT:-$REDIS_PORT}/0";
    echo "CELERY_RESULT_BACKEND=redis://${REDIS_HOST:-$REDIS_HOST}:${REDIS_PORT:-$REDIS_PORT}/0";
  } >> $ENV_FILE
fi

# Check if 'test' .test.env file already exists
if [ -f $TEST_ENV_FILE ]; then
  echo "$TEST_ENV_FILE file already exists. To reset, remove it then re-run this script."
# If not, initialize it with new key:value pairs
else
  # Create the .env file
  touch $TEST_ENV_FILE

  # Write to the file
  {
    echo "# FastAPI Settings";
    echo "DEBUG=${TEST_DEBUG}";

    echo "API_PORT=${API_PORT:-$API_PORT}";
    echo "PROJECT_NAME=${PROJECT_NAME}";
    echo "PROJECT_VERSION=${PROJECT_VERSION}";
    echo "DEFAULT_EMAIL=${DEFAULT_EMAIL}";
    echo "HASH_ALGORITHM=${HASH_ALGORITHM}";
    echo "ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}";
    echo "BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}";
    echo "SECRET_KEY=${SECRET_KEY:-$RANDOM_SECRET_STR}";

    echo "# Postgres Settings (also used by FastAPI)";
    echo "POSTGRES_USER=${POSTGRES_USER:-$RANDOM_USER}";
    echo "POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-$RANDOM_POSTGRES_PW}";
    echo "POSTGRES_DB=${POSTGRES_DB:-$POSTGRES_DB}${TEST_POSTFIX}";
    echo "POSTGRES_SERVER=${TEST_POSTGRES_SERVER}";
    echo "POSTGRES_PORT=${POSTGRES_PORT:-$POSTGRES_PORT}";

    echo "# Redis (Celery) Settings";
    echo "REDIS_HOST=${REDIS_HOST:-$REDIS_HOST}";
    echo "REDIS_PASSWORD=${REDIS_PASSWORD:-$RANDOM_REDIS_PW}";
    echo "REDIS_PORT=${REDIS_PORT:-$REDIS_PORT}";
    echo "REDIS_DB=${REDIS_DB:-$REDIS_DB}";
    echo "CELERY_BROKER_URL=redis://${TEST_REDIS_HOST:-$TEST_REDIS_HOST}:${REDIS_PORT:-$REDIS_PORT}/0";
    echo "CELERY_RESULT_BACKEND=redis://${TEST_REDIS_HOST:-$TEST_REDIS_HOST}:${REDIS_PORT:-$REDIS_PORT}/0";
  } >> $TEST_ENV_FILE
fi