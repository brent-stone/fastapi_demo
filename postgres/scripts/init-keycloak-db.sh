#!/bin/bash

expect << END
        spawn createuser --username "$POSTGRES_USER" --echo --encrypted --pwprompt "$DB_USER"
        expect "Enter password for new role:"
        send "$DB_PASSWORD\r"
        expect "Enter it again:"
        send "$DB_PASSWORD\r"
        expect eof
        spawn createdb --username "$POSTGRES_USER" -O "$DB_USER" "$DB_DATABASE"
        expect eof
END
