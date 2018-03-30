#!/bin/bash
#
##################
## Instructions ##
##################
# first do this:
#  $ python3 -m venv venv
#  $ source venv/bin/activate
#
# then run this:
#  (venv) $ ./pip_all.sh
#

##########################################
## Verify we are running the proper pip ##
##########################################
which pip

##########################################
## Install flask and all the extensions ##
##########################################
pip install --upgrade pip
pip install flask
pip install Flask-REST-JSONAPI
pip install flask-sqlalchemy
pip install flask-bcrypt
pip install flask-httpauth
pip install flask-login
pip install flask-mail
pip install flask-uploads
pip install Flask-WTF

##########################################
## Install python packages for e2e test ##
##########################################
pip install requests
pip install Pillow

###########################################
## Install Jupyter notebook for e2e test ##
###########################################
pip install --upgrade pip
pip install jupyter
pip install ipykernel
python3 -m ipykernel install --user

####################
## Install Pylint ##
####################
pip install pylint
