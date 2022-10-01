FROM python:3.10-slim as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export --format requirements.txt --output requirements.txt --without-hashes
RUN poetry export --format requirements.txt --output requirements-dev.txt --without-hashes --dev

FROM python:3.10-slim as production

LABEL maintainer="Brent Stone <brent-stone@github.com>"

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

COPY ./gunicorn_conf.py /gunicorn_conf.py

COPY ./start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh

COPY ./prestart.sh /app/prestart.sh
RUN chmod +x /app/prestart.sh

COPY ./alembic.ini /app/alembic.ini
COPY ./pyproject.toml /app/pyproject.toml

# For now we're going to bloat the prod image with dev dependencies.
# TODO: Look for layering in an install of prod requirements, then dev requirements, then
#  do a good job of referencing the appropriate layer from docker compose.
COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt
#COPY --from=requirements-stage /tmp/requirements-dev.txt /app/requirements.txt


# Caching pip with BuildKit: https://pythonspeed.com/articles/docker-cache-pip-downloads/
# In you dev environment, be sure BuildKit is active using an enivornment variable:
# export DOCKER_BUILDKIT=1
#RUN --mount=type=cache,target=/root/.cache \

# Alternate caching method without BuildKit as recommended on FastAPI docs:
# https://fastapi.tiangolo.com/deployment/docker/#docker-cache
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./alembic /app/alembic
COPY ./tests /app/tests
COPY demo_backend /app/demo_backend
WORKDIR /app/

ENV PYTHONPATH=/app

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