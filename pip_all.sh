#!/bin/bash
#
##################
## Instructions ##
##################
# first do this:
#  $ python3.6 -m venv venv
#  $ source venv/bin/activate
#
# then run this:
#  (venv) $ ./pip_all.sh
#

##########################################
## Verify we are running the proper pip ##
##########################################
which pip
pip install --upgrade pip

##########################################
## Install flask and all the extensions ##
##########################################
pip install flask
pip install Flask-REST-JSONAPI
pip install flask-sqlalchemy
pip install flask-migrate
pip install flask-httpauth
pip install flask-login
pip install flask-mail
pip install flask-uploads
pip install Flask-WTF

############################################################
## Install additional python packages used by application ##
############################################################
pip install oauth2client
pip install python-dotenv

##########################################
## Install python packages for e2e test ##
##########################################
pip install requests
pip install Pillow

###########################################
## Install Jupyter notebook for e2e test ##
###########################################
pip install jupyter
pip install ipykernel
python3 -m ipykernel install --user

###########################
## Install PEP8 checkers ##
## - Pylint              ##
## - pycodestyle         ##
## - pep8                ##
###########################
pip install pylint
pip install pep8
pip install pycodestyle

################################
## Install gunicorn webserver ##
################################
pip install gunicorn

############################################################################
## Install package that allows SQLAlchemy to connect to Postgres database ##
############################################################################
pip install psycopg2-binary
