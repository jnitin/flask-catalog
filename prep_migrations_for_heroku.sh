#!/bin/bash
#
############
## README ##
############
#
# This will:
#   - remove the content of the migrations folder
#   - initize the migrations repository
#
# Note that on heroku, the command flask upgrade will be run at startup
#
##################
## Instructions ##
##################
# run this:
#  (venv) $ ./prep_migrations_for_heroku.sh
#

echo 'removing migrations folder and content'
rm -rf migrations

echo 'initializing the migration repository'
flask db init

echo 'Now, first reset the database in Heroku console in web' 
echo 'Then deploy it to Heroku via git add, git commit and git push!!'
