#############################################################################
# THESE ARE TYPICAL STEPS TO TAKE WHEN USING THIS AS BASE FOR A NEW project #
#                                                                           #
# At bottom also ideas for further enhancements of this portfolio project   #
#############################################################################

venv
====
( ) Create a NEW venv from scratch. Do NOT copy from other location:
	( )Temporarily remove venv activation in .bashrc
    ( )Install python3-pip, python3-venv
    ( )Follow instructions inside pip_all.sh
    ( )Restore venv activation in .bashrc


models
======
( ) user blueprint
	( ) remove application specific columns
    ( ) remove application specific methods
    ( ) define application specific columns
    ( ) define application specific methods
    ( ) update tests_user_model.py
    ( ) Delete owned entries of a user when Deleting a user

( ) catalog blueprint
    ( ) Register the blueprint
    ( ) models.py
        ( ) Define ORM classes
        ( ) Define method: insert_default_items
        ( ) Call this method from catalog.py, if app.db not there.
        ( ) Remove app.db, then startup web server, and verify that app.db
	        contains correct tables & default entries
    ( ) create tests/tests_catalog_model.py

( ) do NOT use Flask-Bcrypt
	( ) bcrypt does not play nice with PostgreSQL, which is the database used
	    on Heroku.


permissions
===========
(-) Only admin can change role of users
    (-) via web-page
	(-) via API

(-) Only admin can create categoriies
    (-) via web-page
    (-) via API

(-) Only logged in users can create items
    (-) via web-page
    (-) via API

branding
========
( ) Rename startup python file: catalog.py
( ) Replace icons in static (favicon.ico & img/logo* )
( ) In base.html
    ( ) meta name --> for SEO
( ) In index.html
    ( ) set page_title = '.......' --> for web-browser tab on home page
    ( ) update jumbotron content

credits
=======
( ) In index.html
    ( ) update credits

configuration
=============
(-) Update SECRET_KEY in .env using method described in flask quickstart

views & html
============
( ) Add capability to add new categories & items
( ) Add capability to edit new categories & items
( ) Add capability to delete categories & items

auth
====

GOOGLE OAUTH2
=============
( ) Get auth keys at google for this application
    ( ) https://console.developers.google.com/apis
		(See nd004 3.11-5 instructions on Google Drive)

( ) Add keys to .env

( ) LOGIN & REGISTER
	(-) We need to update to latest OAUTH methods of Google
	( ) Add button & javascript to login_oauth.html base template
		( ) Extend from this in both login.html and register.html templates
	( ) In login_oauth.html, set correct redirect upon succesful login
	( ) gconnect method in views.py
		( ) Create CSRF token (state) in auth.views.login and pass to template
			(-) Test this on multiple login sessions going on at once...
		( ) If user does not yet exist, create it.
		( ) Register user with flask_login
		( ) In verify password, do not check on password for users that
			logged in via Google OAUTH
	(-) Write a unit test for Google signin
	(-) Write a e2e test for Google signin


profile pictures
============
(-) Avoid clutter in uploads folder
	(-) In tests, remove any uploaded pictures during teardown
	(-) When deleting user, make sure his uploads are deleted as well
	(-) When changing profile picture, make sure to delete previous one


api
===
( ) Delete user must also delete the Categories and Items.
( ) Create application specific package, like api/catalog, with:
	( ) model_schemas.py
	( ) views.py
	( ) __init__.py


(-) All responses must return JSON API 1.0 specification

e2e testing
===========
( ) Update e2e_tests.ipynb

configuration
=============
( ) Create multiple configs, as in Flask Web Development book

cleanup
=======


code review
===========
(-) Do all POST requests return a redirect instead of render_template?
     --> This is important to avoid resubmission of forms
          (see: https://en.wikipedia.org/wiki/Post/Redirect/Get )
(-) Do all entries in HTML for forms have error printing (See login as example)
(-) Fix all Pylint Errors
(-) Fix all Pylint Warnings
(-) Fix all Pylint Info messages


deployment
==========
(-) Checklist before deployment
	(-) Did I add all required credits to index.html?
	(-) Is DEBUG mode turned off?
	(-) Is SECRET_KEY updated?


promotion
=========


#############################
# TO DO FOR NEXT deployment #
#############################

(-) Refactor with Templates moved into each blueprint folder
(-) Activate link in /unconfirmed : Need another confirmation email?
(-) Refactor @email.route('/confirm/<token>') to @auth.route
(-) Implement email_change request


##########################
# IDEAS FOR NEW FEATURES #
##########################

(-) Enter New Feature Requests and Issues with the Github repo.

(-) Send emails via a background thread

(-) Demonstrator of Javascript as in chapter 20 of MEGA Tutorial:
	(-) When hovering over a category name or an item name for 2 seconds,
	    create a popover with:
		(-) Name of category or item
		(-) Description of the item (if it is an item)
		(-) Name of the owner of the category or item
			(-) When hovering over the owner name for 2 seconds, pop up the
				owner's public profile
		(-) If the user is logged in show Edit / Delete at bottom:
			(-) Clicking on those will will act as before.

(-) Add code coverage as in Flask Web Development book

(-) Add performance testing as in Flask Web Development book

(-) Add user notifications as in Mega Tutorial

(-) Add application issue notification via email to webmaster

(-) Add a background process as in MEGA Tutorial
