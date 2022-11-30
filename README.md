# Demonstration of containerized FastAPI with PostgreSQL and Redis

# Quickstart
This code is verified working in Ubuntu and with some compatability turned on, Mac. Newer Mac Computers may need to turn
on legacy compatability settings.

- [ ] Clone this repo
- [ ] Ensure docker compose is installed
- [ ] Ensure Poetry is available at system level environment via `pip install poetry`
- [ ] `chmod +x initialize_env.sh`
- [ ] run `initialize_env.sh` to auto-generate a .env in the top level directory and a .test.env in the /backend
directory
- [ ] `docker compose up`
- [ ] From local dev host, run the following to initialize to setup local Poetry virtual environment and postgres testing table:
  - [ ] In `/backend` directory: `poetry shell` and `poetry install`
  - [ ] In activated virtual environment: `alembic upgrade head`
  - [ ] Verify everything is working by running `pytest`

The following is a list of service:localhost_url mappings available during development:

- FastAPI Swagger UI: http://localhost:8883/docs
- Adminer PostgreSQL Admin Panel: http://localhost:5701/
- Flower Redis Monitoring Panel: http://localhost:5556/

## Developer Getting Started

See [development live reload](https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker#development-live-reload) instructions from FastAPI for info for using this containerization in prod or dev.

See [this blog](https://www.jeffastor.com/blog/populating-cleaning-jobs-with-user-offers-in-fastapi) and corresponding [git repo](https://github.com/Jastor11/phresh-tutorial/tree/master) for a nice step-by-step with FastAPI and docker.

### Build the FastAPI backend container

- [ ] Open terminal in the `/demo_backend/backend/` folder
- [ ] `DOCKER_BUILDKIT=1 docker build -t demo_backend_api_image .`
- [ ] To build from compose with terminal in project root: `DOCKER_BUILDKIT=1 docker compose up --build`

**STRONGLY RECOMMEND**: Update your git settings so it doesn't auto-convert to windows line endings when pulling onto a windows box:

`git config --global core.autocrlf false`

### Run docker compose as dev or prod
- **MOST LIKELY** you'll want to run using docker compose which orchestrated multiple containers (FastAPI, Postgres, \[todo] React) instead of the API container by itself.
  - Run "live" dev: `docker compose up`
    - http://127.0.0.1:8883
    - Interactive Docs at
    - Enables 'hot reload' of changes to FastAPI code
  - Run prod: `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`
  - `docker compose down` to shutdown the orchestrated containers.
- Go to http://127.0.0.1/docs \[ip:port for dev] to see the automatic interactive API documentation (provided by Swagger UI).
- Go to http://127.0.0.1/redoc \[ip:port for dev] to see the alternative automatic documentation (provided by ReDoc)
- Open terminal in API container: `docker exec -ti demo-backend-api-dev /bin/bash`
  - `exit` to exit the session.
- Open psql session in DB container: `docker exec -ti demo_backend-db psql -h localhost -U demo --dbname=demo`
  - `\q` to exit the session.
  - `\d` to list tables.
  - `TABLE <tablename>;` to list table contents.

### Troubleshooting Postgres container authentication
- The Postgres container will grab default settings from a .env file which can be auto-generated with the `initialize_env.sh` script.
- It's necessary to prune both containers and volumes related to postgres to easily reset the initial settings.
- You'll know you adequately reset the postgres container build to grab new settings if you see `CREATE DATABASE` and extraordinarily long output generated when starting the container.


#### Context

Docker compose 2 looks for `docker-compose.yml` to begin orchestration. However, it then also looks at
`docker-compose.override.yml` to, you guessed it, override some settings from the based configuration.

`docker-compose.override.yml` is the 'dev' settings enabling hot reload via `start-reload.sh` and mounting the local
`\backend\demo_backend` directory to the container's `\app\demo_backend` directory. `start-reload.sh` directly runs a single uvicorn
worker with hot reload enabled.

`docker-compose.prod.yml` forgoes that local file system mounting (only use what's in the demo_backend-api image) and
instead runs `start.sh`. `start.sh` runs Gunicorn which spawns _n_ uvicorn workers where _n_ is the number of cores on
the server.

#### Only run the FastAPI container
Using a terminal inside the `/backend` folder...
- [ ] Run "live" dev: `docker run -d --name demo_backend_api_dev -p 80:80 -v $(pwd):/app demo_backend_api_image /start-reload.sh`
- [ ] Run prod: `docker run -d --name demo_backend_api_prod -p 80:80 demo_backend_api_image`

**NOTE**: To stop the server (e.g. to swap from dev to prod): `docker stop <container name>`

**NOTE**: To re-run (container already exists): `docker start <container name>`

**NOTE**: If the container already exists and you need to update: `docker rm -f <container-id>`

### Combine FastAPI backend container with Postgresql using Docker Compose

Enabling BuildKit will help ensure pip isn't constantly downloading the same packages over and over again.
- Caching pip with BuildKit: https://pythonspeed.com/articles/docker-cache-pip-downloads/
- In your dev environment, be sure BuildKit is active using an environment variable:
`export DOCKER_BUILDKIT=1`


- See the [tutorial here](https://www.jeffastor.com/blog/up-and-running-with-fastapi-and-docker) for a thorough
walkthough of a containerized webapp using FastAPI, Postgres, and React.
- [ ] `docker compose up -d --build --remove-orphans`
- [ ] `docker compose up`

## Docker Tips
- Remove 'everything' in Docker (images, etc.): `docker system prune -a`
- Remove all containers: `docker container prune`
- Remove all volumes: `docker volume prune`
- Remove all 'dangling' images: `docker rmi $(docker images -f "dangling=true" -q)`
- List containers: `docker container ps --all`
- Stop container: `docker stop <container-id>`
- Delete stopped container: `docker rm <container-id>`
- List images: `docker images`
- Delete image: `docker image rm <image-id>`

## Running REST FastAPI server tests
- `docker ps` to see containers
- `docker exec -it [CONTAINER_ID] bash` to get terminal in API container
- `pytest -v` in container bash session from the `/app` directory (config files will cause failure from another dir)
- Coverage + pytest: `coverage run -m pytest -v && coverage report --show-missing`

## Publishing images to GitLab
- See [this page](https://docs.gitlab.com/ee/user/packages/container_registry/index.html) for documentation.
- Look for the "CLI Commands" button in top right corner of project's **Packages & registries** menu.
- `docker login registry.gitlab.com`
  - Use a personal access token for your password
- Use a URL style tag for the image then build it.
  - `docker build -t registry.gitlab.com/<user or group>/<project name>/<image_name> .`
- Use the URL style tag to then push to the container registry.
  - `docker push registry.gitlab.com/<user or group>/<project name>/demo_backend-backend-prod`


## Pytest tips
- Run a specific test:
  - `pytest tests/db/basic_connection_test.py -k "test_db_metadata" -vv`

## Alembic tips
- Execute an autogenerate revision
  - `alembic revision --autogenerate -m "Added table XYZ"`
  - Look in alembic > versions for the revision and validate/update as needed.
  - Implement the revision with `alembic upgrade head`
