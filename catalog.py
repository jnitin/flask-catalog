import os, os.path
from application import create_app
from application.user import User, Role
from application.catalog import Category, Item
from application.extensions import db

# Create an instance of the application
app = create_app()

# if the database does not yet exist:
# - Create the database and tables
# - Insert the roles
# - Populate with lots of beers
print ('TODO: Remove lines.... in catalog.py')
#path = app.config['DATABASE_PATH']
#if os.path.isfile(path) is False:
#    print("Creating & initializing a new data-base...")
#    with app.app_context():
#        db.create_all()
#        Role.insert_roles()
#        User.insert_default_users()
#        Item.insert_default_items()
#else:
#    print("Connecting to existing data-base...")


if __name__ == '__main__':
    # USE THIS WHEN RUNNING IN THE UDACITY VAGRANT ENVIRONMENT
    #
    # - app.debug = True
    #   -> tells server to restart itself when it finds code changes
    #   -> provides a debugger in the browser
    #
    # - host='0.0.0.0' tells the server to listen on ALL public IP addresses
    #app.debug = True
    #app.run(host = '0.0.0.0', port = 5000)

    # USE THIS WHEN RUNNING LOCAL, WITH debug
    #app.run(debug=True)

    # USE THIS WHEN RUNNING LOCAL & DEBUGGING INSIDE WING IDE
    # IMPORTANT, also do this, else debugger will not stop at breakpoints:
    # http://www.wingware.com/pub/wingide/5.1.3/doc/wingide-howtos-en-a4.pdf
    """The use_reloader argument is optional, but speeds up debugging
    considerably because Flask won't need a restart to load code changes. If
    this option is set to True you will need to enable Debug Child Processes
    under the Debug/Execute tab in Project Properties from the Project menu.
    Otherwise the reloaded process will not be debugged.

    Once this is done, use Set Main Debug File in the Debug menu to set this
    file as your main debug file in Wing IDE. Then you can start debugging from
    the IDE, and load pages from a browser to reach breakpoints or exceptions.
    If you did not set the use_reloader argument to app.run() to True then you
    will need to use Restart Debugging in the Debug menu or the restart icon in
    the toolbar to load changed code into Flask.

    Passing the --no-debug flag or setting environment variable FLASK_DEBUG=0
    are other documented ways to turn of Flask's debug support, although we've
    had reports of --no-debug failing to function as expected.
    """

    import os
    if 'WINGDB_ACTIVE' in os.environ:
        app.debug = False

    ##
    ## Setting up automatic restart if files change.
    ##
    watch_files = []
    ## watch_files = ['app/templates/index.html']
    #app.run(port = 5000, use_reloader=True, extra_files=watch_files)  # localhost
    app.run(port = 5000, use_reloader=False, extra_files=watch_files)  # localhost
