#!/bin/bash

if [ "$#" -eq 0 ]; then
    echo "specify the apps to reset the migrations for"
    exit 1
fi

OWD=$(basename $(pwd))
if [ $OWD == "scripts" ]; then
    # Make sure that we are in the same directory as manage.py
    pushd ".."
fi

MANAGE=./manage.py

# Rollback all migrations and remove the migration files for the app
for app in "$@"
do
    $MANAGE migrate $app zero
    rm ./$app/migrations/[0-9]*.py
done

# Make migrations for all of the apps, then migrate them
$MANAGE makemigrations "$@"

for app in "$@"
do
    $MANAGE migrate $app
done

if [ $OWD == "scripts" ]; then
    # Make sure we return the user to where they were when we left off
    popd
fi
