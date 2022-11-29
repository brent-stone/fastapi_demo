FROM python:3.10-slim as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml pyproject.toml
COPY ./poetry.lock poetry.lock

RUN poetry export --format requirements.txt --output requirements.txt --without-hashes
RUN poetry export --format requirements.txt --output requirements-dev.txt --without-hashes --with dev

FROM python:3.10-slim as development

LABEL maintainer="Brent Stone <brent-stone@github.com>"

# Ensure curl is available for healthcheck via curl
RUN apt update
RUN apt upgrade -y
RUN apt install curl -y

# Install git. NOTE: The Git repo and information will be mounted via docker-compose
# The additional packages are to support compiling google-re python wheel with the C++
# library
RUN apt-get install -y --no-install-recommends git gcc g++ libre2-dev
RUN apt-get purge -y --auto-remove
RUN rm -rf /var/lib/apt/lists/*

WORKDIR /fastapi_demo/backend

COPY ./start.sh start.sh
RUN chmod +x start.sh

COPY ./gunicorn_conf.py gunicorn_conf.py

COPY ./start-reload.sh start-reload.sh
RUN chmod +x start-reload.sh

COPY ./prestart.sh prestart.sh
RUN chmod +x prestart.sh

COPY --from=requirements-stage /tmp/requirements-dev.txt /fastapi_demo/backend/requirements.txt

# Caching with BuildKit: https://pythonspeed.com/articles/docker-cache-pip-downloads/
# In you dev environment, be sure BuildKit is active using an enivornment variable:
# export DOCKER_BUILDKIT=1
# This setting may be permenently enabled on Ubuntu by adding it to user profile config
# via `gedit ~/.profile` in terminal
RUN --mount=type=cache,target=/root/.cache \
  pip install --upgrade -r requirements.txt

COPY ./alembic.ini alembic.ini
COPY ./pyproject.toml pyproject.toml
COPY ./alembic alembic
COPY ./demo_backend demo_backend
COPY ./stubs stubs
COPY ./tests tests

ENV PYTHONPATH=./

EXPOSE 8883

FROM python:3.10-slim as production

LABEL maintainer="Stoneguard Software LLC <contact@stoneguardsoftware.com>"

# Ensure curl is available for healthcheck via curl
RUN apt update
RUN apt upgrade -y
RUN apt install curl -y

# Install git. NOTE: The Git repo and information will be mounted via docker-compose
# The additional packages are to support compiling google-re python wheel with the C++
# library
RUN apt-get install -y --no-install-recommends git gcc g++ libre2-dev
RUN apt-get purge -y --auto-remove
RUN rm -rf /var/lib/apt/lists/*

WORKDIR /fastapi_demo/backend

COPY ./start.sh start.sh
RUN chmod +x start.sh

COPY ./gunicorn_conf.py gunicorn_conf.py

COPY ./start-reload.sh start-reload.sh
RUN chmod +x start-reload.sh

COPY ./prestart.sh prestart.sh
RUN chmod +x prestart.sh

COPY --from=requirements-stage /tmp/requirements.txt /fastapi_demo/backend/requirements.txt

# Caching with BuildKit: https://pythonspeed.com/articles/docker-cache-pip-downloads/
# In you dev environment, be sure BuildKit is active using an enivornment variable:
# export DOCKER_BUILDKIT=1
# This setting may be permenently enabled on Ubuntu by adding it to user profile config
# via `gedit ~/.profile` in terminal
RUN --mount=type=cache,target=/root/.cache \
  pip install --upgrade -r requirements.txt

# Alternate caching method without BuildKit as recommended on FastAPI docs:
# https://fastapi.tiangolo.com/deployment/docker/#docker-cache
#RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./alembic.ini alembic.ini
COPY ./pyproject.toml pyproject.toml
COPY ./alembic alembic
COPY ./demo_backend demo_backend

ENV PYTHONPATH=./

EXPOSE 8883

# Note: We opt to use docker-compose to trigger these scripts instead of the image itself
# this final run command left as an example of how to auto-trigger when migrating to something
# like kubernetes, docker swarm, etc.

# Run the start script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Gunicorn with Uvicorn
# This version starts without live-reload
#CMD ["/start.sh"]
# This version starts with live-reload
#CMD ["/start-reload.sh"]