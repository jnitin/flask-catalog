############################################################
# THESE ARE TYPICAL STEPS TO TAKE WHEN DEPLOYING TO HEROKU #
############################################################

(-) Prep for deployment to heroku (Follow mega tutorial instructions...)

     ( ) At google console https://console.developers.google.com/apis/credentials/oauthclient/524473164280-d6r6vijbej0fvj6g3m3vb6hsp3nb7n4q.apps.googleusercontent.com?project=catalog-199918&folder&organizationId
         -> Add Authorized JavaScript origins:
                https://flask-catalog.herokuapp.com

     ( ) Upgrade to Python 3.6.2 (https://docs.google.com/document/d/1hMlS6pfl_bG0vz6ns2bG4NMRgsVdIzpyPQxIkmsOubs/edit)

     ( ) Update requirements.txt

     ( ) Implement database migration
          ( ) Follow section 4.2 of Mega Tutorial
               (-) Add extension Flask-Migrate
                    (o) This adds sub-command: flask db
               (-) Initialize migration repository:
                    (venv) $ flask db init
                    --> creates a folder ./migrations which must be put under source control
               (-) Do a database migration, with comment
                    $ flask db migrate -m "initial"    (Creates migration script)
                    $ flask db upgrade                 (Creates/Upgrades db)

                    NOTE:
                    (o) When working with database servers such as MySQL and
                        PostgreSQL, you have to create the database in the
                        database server before running upgrade.
                    (o) If you ever need to downgrade the database, use this:
                         $ flask db downgrade
                         $ rm <last migration script>
                    (o) Question: does Flask-Migrate get rid of content???

     ( ) Refactor database initialization into a cli command: flask initdb
          Test it by runnning the initdb command:
          $ flask initdb
          $ sqlitebrowser app.db   (VERIFY CONTENT)

          NOTE: initdb is NOT related to Flask-Migrate. It uses the
                standard capability of Flask, which comes with cli out of
                the box (http://flask.pocoo.org/docs/0.12/cli/)

     ( ) Prep to work with Heroku Postgres database:
          ( ) Update config.py to use DATABASE_URL environment variable, like this:
               SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                    'sqlite:///' + os.path.join(basedir, 'app.db')

     (-) Option to log to stdout:
          --> Follow method of mega tutorial, using LOG_TO_STDOUT

(-) Initial deployment to heroku (Follow mega tutorial instructions...)

     ( ) install heroku CLI (https://devcenter.heroku.com/articles/heroku-cli#download-and-install)
          $ sudo snap install heroku --classic
          $ heroku --version
          heroku-cli/6.16.4 (linux-x64) node-v9.9.0

     ( ) login to heroku CLI
          $ heroku login
          NOTE: The heroku CLI saves your email address and an API token to ~/.netrc
                for future use. For more information, see Heroku CLI Authentication:
                https://devcenter.heroku.com/articles/authentication

     ( ) Create a Heroku application
          (venv) $ heroku apps:create flask-catalog
          Creating ⬢ flask-catalog... done
          https://flask-catalog.herokuapp.com/ | https://git.heroku.com/flask-catalog.git

          NOTE: The local git repository will be configured with an extra
                remote, called heroku. Verify that it exists with the git remote
                command:

          (venv) $ git remote -v

     ( ) Create a free postgressql database:

          There is a command line to do this, but it is not clear which one to use:
          $ heroku addons:add heroku-postgresql:hobby-dev        (Mega Tutorial)
          or
          $ heroku addons:create heroku-postgresql:hobby-dev     (https://elements.heroku.com/addons/heroku-postgresql)

          To avoid mistakes, I provisioned the database via the heroku website:
          --> https://elements.heroku.com/addons/heroku-postgresql
          Just login, and install it to the flask-catalog app. Then redirected to this:
          https://dashboard.heroku.com/apps/flask-catalog/resources?justInstalledAddonServiceId=6c67493d-8fc2-4cd4-9161-4f1ec11cbe69


          NOTE: The environment variable DATABASE_URL is automatically set
                     on Heroku when using a Postgres database (see below), so
                     nothing else needs to be done to prep for deployment.
                Read: https://elements.heroku.com/addons/heroku-postgresql
                      --> hobby-dev is free
                      https://www.heroku.com/postgres
                      https://www.postgresql.org/

     ( ) Add psycopg2 as a new dependency to requirements.txt

          $ pip install psycopg2
          $ pip freeze > requirements.txt

          NOTE: The application will be connecting to a Postgres database, and
                for that to work SQLAlchemy requires the psycopg2 package to be
                installed.

     ( ) Logging to stdout
          Set the LOG_TO_STDOUT environment variable

          $ heroku config:set LOG_TO_STDOUT=1
          Setting LOG_TO_STDOUT and restarting ⬢ flask-catalog... done, v4
          LOG_TO_STDOUT: 1

          (o) to view all logs of application:
          $ heroku logs

          NOTE: Heroku expects applications to log directly to stdout. Anything
                the application prints to the standard output is saved and
                returned when you use the '$ heroku logs' command.

     ( ) Add gunicorn webserver as a new dependencies to requirements.txt

          $ pip install gunicorn
          $ pip freeze > requirements.txt

          NOTE: Heroku does not provide a web server of its own. Instead, it
                expects the application to start its own web server on the port
                number given in the environment variable $PORT . Since the Flask
                development web server is not robust enough to use for production,
                I’m going to use gunicorn, the server recommended by Heroku for
                Python applications.
               (http://gunicorn.org/)


     ( ) Define all environment variables from .env on heroku as config vars

          Option 1: use the command line:
               $ heroku config:set ++++++=........     (Set a config variable)
               $ heroku config:unset ++++++            (Unset a config variable)
               $ heroku config                         (Lists all config variables)
               $ heroku config:get ++++++              (Lists a specific config variable)

          Option 2: Edit config vars on the app's settings tab on Dashboard:
               https://dashboard.heroku.com/apps/flask-catalog/settings

          Note: https://devcenter.heroku.com/articles/config-vars
                Heroku manifests config vars as environment variables to the
                application. These environment variables are persistent – they
                will remain in place across deploys and app restarts – so unless
                you need to change values, you only need to set them once.

                Whenever you set or remove a config var, your app will be restarted

     ( ) Create a Procfile and put it under source control

          Procfile:
          ---------
          web: flask db upgrade; gunicorn catalog:app

          Because the first sub-command is based on the flask command, I need to
          add the FLASK_APP environment variable:

          $ heroku config:set FLASK_APP=catalog.py

          Also, don't forget to add Procfile under source control

          NOTE: Heroku needs to know how to execute the application, and for
                that it uses a file named Procfile in the root directory of the
                application. The format of this file is simple, each line
                includes a process name, a colon, and then the command that
                starts the process.

                The most common type of application that runs on Heroku is a web
                application, and for this type of application the process name
                should be 'web'.

                Here I defined the command to start the web application as two
                commands in sequence. First I run a database migration upgrade,
                then I start the server.

     ( ) Deploy --> use steps given at bottom

     ( ) heroku logs showed an error.
          The with open(GOOGLE_OAUTH2_FILE_PATH, 'w') command did not work.
          This is because the instance folder does not exist. Fixed it by
          changing the config variable to point to an existing directory.

     ( ) When trying out signin via Google, it gave this error:
          The JavaScript origin in the request, https://flask-catalog.herokuapp.com,
          does not match the ones authorized for the OAuth client.
          Visit https://console.developers.google.com/apis/credentials/oauthclient/524473164280-d6r6vijbej0fvj6g3m3vb6hsp3nb7n4q.apps.googleusercontent.com?project=524473164280
          to update the authorized JavaScript origins.

         Solution is to add 'https://flask-catalog.herokuapp.com' as an
         authorized JavaScript origin.


###########################
# DEPLOYMENT OF AN UPDATE #
###########################

     NOTE: Each time you push a change, you need to restart the one-of dyno!!!

     ( ) This step is optional if you want to just start completely fresh, with
          an initial database migration step. This script will wipe out the
          migrations folder and does a new initial migration step:

          $ ./reset_db_migrations.sh


     ( ) Commit everything to your local git repository

          $ git add .
          $ git commit -m "Ready for heroku deployment"

     ( ) Push local repository to heroku, and it will be automatically deployed

          $ git push heroku master

          --> Verify that web app is running at:
               https://flask-catalog.herokuapp.com/

          --> If this is your first deployment, the database will have the
              tables, because in the Procfile we specified that Heroku must
              run a 'flask db upgrade', but the tables will be empty.

     ( ) This step is required for initial deployment, and optional after that:
          Initialize the database using a one-off dyno:
          See: https://devcenter.heroku.com/articles/one-off-dynos

          (venv) $ heroku run bash
          ~$ flask initdb

          --> Verify in the website that database now has the default content

          In a new terminal window, stop the one-off dyno:
          (venv) $ heroku ps       (Shows the running dyno)

          (venv) $ heroku ps:stop run.1      (If the name is run.1)


     ( ) run the unittests in one-off dyno:
          (venv) $ heroku run bash
          ~$ cd tests
          ~/tests $ python tests_user_model.py


     ( ) viewing logs with: (https://devcenter.heroku.com/articles/logging)
          $ heroku logs -n 200   (Retrieves last 200 lines)
          $ heroku logs --tail   (tailing logs)


