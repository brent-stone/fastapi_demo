#! /bin/bash
# stop execution instantly on non-zero status. This is to know location of error
set -e

########## SELF-SIGNED CERT GENERATION TO ENABLE HTTPS ##########
# First, generate a self-signed certificate. These typically only work on localhost
# during development. Use Let's Encrypt or something similar when deploying as a public
# facing production service.
SELF_CERT_NAME="localhost"
SELF_CERT="${SELF_CERT_NAME}.crt"
SELF_KEY="${SELF_CERT_NAME}.key"
# Check if certificate and key exist
if [[ -f ${SELF_CERT} || -f ${SELF_KEY} ]]; then
  echo "$SELF_CERT or $SELF_KEY already exists. To reset, remove both then re-run \
this script."
# If not, generate them
else
  # Create the self signed cert
  openssl req -x509 -out ${SELF_CERT} -keyout ${SELF_KEY} \
  -newkey rsa:4096 -nodes -sha256 \
  -subj '/CN=localhost' -extensions EXT -config <(printf \
  "[dn]\nCN=localhost\n[req]\ndistinguished_name=dn\n[EXT]\nsubjectAltName=DNS:localhost\nkeyUsage=digitalSignature\nextendedKeyUsage=serverAuth")
fi

########## .env & /backend/.test.env SETUP ##########
RANDOM_STRING="random_string_was_not_generated!!"
STRING_LENGTH=32

RANDOM_STRING_CORPUS='A-Za-z0-9!#$%&'\''()*+,-./:;<=>?@[\]^_`{|}~'
RANDOM_USER_CORPUS='A-Za-z@_#'
# Function to generate a STRING_LENGTH string of characters
rando_string() {
    RANDOM_STRING=$(env LC_ALL=C tr -dc "$RANDOM_STRING_CORPUS" </dev/urandom |
    head -c $STRING_LENGTH)
}

# Function to generate viable postgres username which must start with a letter, @, _, or
# # For simplicity, simply make the whole username STRING_LENGTH valid starting
# characters
rando_user() {
  RANDOM_STRING=$(env LC_ALL=C tr -dc "$RANDOM_USER_CORPUS" </dev/urandom |
  head -c $STRING_LENGTH)
}

# Output filenames
ENV_FILE="./.env"
TEST_ENV_FILE="./backend/.test.env"

# Used to modify pytest and logging behavior within the FastAPI and SQLAlchemy services
DEBUG="false"

# Used to modify Uvicorn and FastAPI layer logging
LOG_LEVEL="info"
LOG_LEVEL_DEBUG="debug"

# Used by React frontend
HTTP_PORT="57080"
HTTPS_PORT="57443"

# Used by FastAPI and Pydantic BaseSettings ingest
API_PORT="57073"
PROJECT_NAME="FastAPI Demo"
PROJECT_VERSION="0.1.0"
BACKEND_CORS_ORIGINS="[\
\"http://localhost\",\
\"http://localhost:80\",\
\"http://localhost:3000\",\
\"http://localhost:$HTTP_PORT\",\
\"https://localhost:443\",\
\"https://localhost:$HTTPS_PORT\",\
\"https://localhost\"\
]"
HASH_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES="10080"  # 60 minutes * 24 hours * 7 days
DEFAULT_USERNAME="brentstone"
rando_string
DEFAULT_USER_PASS=${RANDOM_STRING}
DEFAULT_EMAIL="brent-stone@github.com"

POSTGRES_USER="demo"
POSTGRES_DB="demo"
# These following settings are used by FastAPI API layer under core > config.py
######## DEVELOPER INFO ########
# Ensure \backend\.test.env used by pytest uses POSTGRES_SERVER value of localhost or IP
# of running postgres container instead of using a docker service alias like db.
POSTGRES_SERVER="db"
POSTGRES_PORT="57074"

# .test.env specific settings for pytest and local development
TEST_DEBUG="true"
TEST_POSTFIX="_test"
TEST_POSTGRES_SERVER="localhost"
ADMINER_PORT="57075"

# Redis Settings
REDIS_PORT="57076"
REDIS_HOST="redis"
REDIS_DB=${POSTGRES_SERVER}
TEST_REDIS_HOST="localhost"

# Flower (Celery) Redis Dashboard Settings
FLOWER_PORT="57077"

# KeyCloak Settings
KEYCLOAK_PORT=8080
DB_VENDOR=POSTGRES
DB_ADDR=db
DB_DATABASE=autoai_keycloak_db
DB_USER=keycloak
DB_SCHEMA=public
rando_string
DB_PASSWORD="${RANDOM_STRING}"
KEYCLOAK_ADMIN=autoai_admin
rando_string
KEYCLOAK_ADMIN_PASSWORD="${RANDOM_STRING}"
KEYCLOAK_USER=autoai_keycloak
rando_string
KEYCLOAK_PASSWORD="${RANDOM_STRING}"

# Generate viable random values for the user/pass & encryption environment variables
rando_user
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
    echo "# General Settings";
    echo "DEBUG=${DEBUG}";

    echo "# Uvicorn gateway and API logging settings";
    echo "# Uvicorn log level values: 'critical', 'error', 'warning', 'info', 'debug'";
    echo "LOG_LEVEL=${LOG_LEVEL}";

    echo "# React Frontend Settings";
    echo "HTTP_PORT=${HTTP_PORT:-$HTTP_PORT}";
    echo "HTTPS_PORT=${HTTPS_PORT:-$HTTPS_PORT}";

    echo "# FastAPI Settings";
    echo "API_PORT=${API_PORT:-$API_PORT}";
    echo "PROJECT_NAME=${PROJECT_NAME}";
    echo "PROJECT_VERSION=${PROJECT_VERSION}";
    echo "DEFAULT_USERNAME=${DEFAULT_USERNAME}";
    echo "DEFAULT_USER_PASS=${DEFAULT_USER_PASS}";
    echo "DEFAULT_EMAIL=${DEFAULT_EMAIL}";
    echo "HASH_ALGORITHM=${HASH_ALGORITHM}";
    echo "ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}";
    echo "BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}";
    echo "SECRET_KEY=${SECRET_KEY:-$RANDOM_SECRET_STR}";
    echo "# FastAPI SQLAlchemy 2.0 migration specific warning flag";
    echo "# remove once SQLAlchemy is officially updated to 2.0"
    echo "SQLALCHEMY_WARN_20=1";

    echo "# Postgres Settings (also used by FastAPI)";
    echo "POSTGRES_USER=${POSTGRES_USER:-$RANDOM_USER}";
    echo "POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-$RANDOM_POSTGRES_PW}";
    echo "POSTGRES_DB=${POSTGRES_DB:-$POSTGRES_DB}";
    echo "POSTGRES_SERVER=${POSTGRES_SERVER:-$POSTGRES_SERVER}";
    echo "POSTGRES_PORT=${POSTGRES_PORT:-$POSTGRES_PORT}";

    echo "# Postgres Adminer dashboard settings (dev only)"
    echo "ADMINER_PORT=${ADMINER_PORT:-$ADMINER_PORT}"

    echo "# Redis (Celery) Settings";
    echo "REDIS_HOST=${REDIS_HOST:-$REDIS_HOST}";
    echo "REDIS_PASSWORD=${REDIS_PASSWORD:-$RANDOM_REDIS_PW}";
    echo "REDIS_PORT=${REDIS_PORT:-$REDIS_PORT}";
    echo "REDIS_DB=${REDIS_DB:-$REDIS_DB}";
    echo "CELERY_BROKER_URL=redis://${REDIS_HOST:-$REDIS_HOST}/0";
    echo "CELERY_RESULT_BACKEND=redis://${REDIS_HOST:-$REDIS_HOST}/0";

    echo "# Redis (Celery) Flower dashboard settings (dev only)";
    echo "FLOWER_PORT=${FLOWER_PORT:-$FLOWER_PORT}";

    echo "# Keycloak Environment Variables";
    echo "KEYCLOAK_PORT=${KEYCLOAK_PORT:-$KEYCLOAK_PORT}";
    echo "DB_VENDOR=${DB_VENDOR:-$DB_VENDOR}";
    echo "DB_ADDR=${DB_ADDR:-$DB_ADDR}";
    echo "DB_DATABASE=${DB_DATABASE:-$DB_DATABASE}";
    echo "DB_USER=${DB_USER:-$DB_USER}";
    echo "DB_SCHEMA=${DB_SCHEMA:-$DB_SCHEMA}";
    echo "DB_PASSWORD=${DB_PASSWORD:-$DB_PASSWORD}";
    echo "KEYCLOAK_ADMIN=${KEYCLOAK_ADMIN:-$KEYCLOAK_ADMIN}";
    echo "KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD:-$KEYCLOAK_ADMIN_PASSWORD}";
    echo "KEYCLOAK_USER=${KEYCLOAK_USER:-$KEYCLOAK_USER}";
    echo "KEYCLOAK_PASSWORD=${KEYCLOAK_PASSWORD:-$KEYCLOAK_PASSWORD}";
  } >> $ENV_FILE
fi

# Check if 'test' .test.env file already exists
if [ -f $TEST_ENV_FILE ]; then
  echo "$TEST_ENV_FILE file already exists. To reset, remove it then re-run this \
script."
# If not, initialize it with new key:value pairs
else
  # Create the .env file
  touch $TEST_ENV_FILE

  # Write to the file
  {
    echo "# General Settings";
    echo "DEBUG=${TEST_DEBUG}";

    echo "# Uvicorn gateway and API logging settings";
    echo "# Uvicorn log level values: 'critical', 'error', 'warning', 'info', 'debug'";
    echo "LOG_LEVEL=${LOG_LEVEL_DEBUG}";

    echo "# React Frontend Settings";
    echo "HTTP_PORT=${HTTP_PORT:-$HTTP_PORT}";
    echo "HTTPS_PORT=${HTTPS_PORT:-$HTTPS_PORT}";

    echo "# FastAPI Settings";
    echo "API_PORT=${API_PORT:-$API_PORT}";
    echo "PROJECT_NAME=${PROJECT_NAME}";
    echo "PROJECT_VERSION=${PROJECT_VERSION}";
    echo "DEFAULT_USERNAME=${DEFAULT_USERNAME}";
    echo "DEFAULT_USER_PASS=${DEFAULT_USER_PASS}";
    echo "DEFAULT_EMAIL=${DEFAULT_EMAIL}";
    echo "HASH_ALGORITHM=${HASH_ALGORITHM}";
    echo "ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}";
    echo "BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}";
    echo "SECRET_KEY=${SECRET_KEY:-$RANDOM_SECRET_STR}";
    echo "# FastAPI SQLAlchemy 2.0 migration specific warning flag";
    echo "# remove once SQLAlchemy is officially updated to 2.0"
    echo "SQLALCHEMY_WARN_20=1";

    echo "# Postgres Settings (also used by FastAPI)";
    echo "POSTGRES_USER=${POSTGRES_USER:-$RANDOM_USER}";
    echo "POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-$RANDOM_POSTGRES_PW}";
    echo "POSTGRES_DB=${POSTGRES_DB:-$POSTGRES_DB}${TEST_POSTFIX}";
    echo "POSTGRES_SERVER=${TEST_POSTGRES_SERVER}";
    echo "POSTGRES_PORT=${POSTGRES_PORT:-$POSTGRES_PORT}";

    echo "# Postgres Adminer dashboard settings (dev only)"
    echo "ADMINER_PORT=${ADMINER_PORT:-$ADMINER_PORT}"

    echo "# Redis (Celery) Settings";
    echo "REDIS_HOST=${REDIS_HOST:-$REDIS_HOST}";
    echo "REDIS_PASSWORD=${REDIS_PASSWORD:-$RANDOM_REDIS_PW}";
    echo "REDIS_PORT=${REDIS_PORT:-$REDIS_PORT}";
    echo "REDIS_DB=${REDIS_DB:-$REDIS_DB}";
    echo "CELERY_BROKER_URL=redis://${TEST_REDIS_HOST:-$TEST_REDIS_HOST}:${REDIS_PORT:-$REDIS_PORT}/0";
    echo "CELERY_RESULT_BACKEND=redis://${TEST_REDIS_HOST:-$TEST_REDIS_HOST}:${REDIS_PORT:-$REDIS_PORT}/0";

    echo "# Redis (Celery) Flower dashboard settings (dev only)"
    echo "FLOWER_PORT=${FLOWER_PORT:-$FLOWER_PORT}"
  } >> $TEST_ENV_FILE
fi
