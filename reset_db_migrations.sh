#!/bin/bash
#
############
## README ##
############
#
# This will:
#   - delete an existing sqlite database: app.db
#   - remove the content of the migrations folder
#   - reinitialize the database:
#      -> creates tables
#      -> inserts default content
#
##################
## Instructions ##
##################
# run this:
#  (venv) $ ./reset_db_migrations.sh
#

echo 'removing existing sqlite database'
rm -rf app.db

echo 'removing migrations folder and content'
rm -rf migrations

echo 'initializing the migration repository'
flask db init

echo 'doing first database migration, by creating first migration script and running it'
flask db migrate -m "initial"
flask db upgrade

echo 'initializing content of the database (will drop & create tables)'
flask initdb
