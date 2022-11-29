FROM postgres:14-alpine as production

# Add the expect function in order to interactively create a new postgres user and
# and database using environment variables passed to the PostgreSQL createuser and
# createdb functions.

# Using these functions avoids complications with trying to escape arbitrary passwords
# provided by environment variables.

# The actual execution is done by the scripts passed in by docker compose to the image's
# default directory for custom setup scripts.

# NOTE: The postgres image will 'source' all the scripts which means directly calling
# expect as the script command (e.g. shebang like `#!/usr/bin/expect -f`) will fail.
# LESSON LEARNED: If at some point you do want to directly run expect and then script
# expect specific commands, environment variables must be accessed like
# "$env(ENV_VARAIBLE)".
USER root
RUN apk add expect
