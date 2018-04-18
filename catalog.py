"""Creates instance of the application"""

import os
import os.path
from application import create_app

APP = create_app()

if __name__ == '__main__':
    ###########################################################################
    # USE THIS WHEN RUNNING IN THE UDACITY VAGRANT ENVIRONMENT
    #
    # - APP.debug = True
    #   -> tells server to restart itself when it finds code changes
    #   -> provides a debugger in the browser
    #
    # - host='0.0.0.0' tells the server to listen on ALL public IP addresses
    ###########################################################################
    # APP.debug = True
    # APP.run(host='0.0.0.0', port=5000)

    ###########################################################################
    # USE THIS WHEN RUNNING LOCAL, WITH debug
    ###########################################################################
    # APP.run(debug=True)

    ###########################################################################
    # USE THIS WHEN RUNNING LOCAL & DEBUGGING INSIDE WING IDE
    # IMPORTANT, also do this, else debugger will not stop at breakpoints:
    # http://www.wingware.com/pub/wingide/5.1.3/doc/wingide-howtos-en-a4.pdf
    # The use_reloader argument is optional, but speeds up debugging
    # considerably because Flask won't need a restart to load code changes. If
    # this option is set to True you will need to enable Debug Child Processes
    # under the Debug/Execute tab in Project Properties from the Project menu.
    # Otherwise the reloaded process will not be debugged.
    #
    # Once this is done, use Set Main Debug File in the Debug menu to set this
    # file as your main debug file in Wing IDE. Then you can start debugging
    # from the IDE, and load pages from a browser to reach breakpoints or
    # exceptions.
    #
    # If you did not set the use_reloader argument to APP.run() to True then
    # you will need to use Restart Debugging in the Debug menu or the restart
    # @icon in the toolbar to load changed code into Flask.
    #
    # Passing the --no-debug flag or setting environment variable
    # FLASK_DEBUG=0 are other documented ways to turn of Flask's debug
    # support, although we've had reports of --no-debug failing to function
    # as expected.
    ###########################################################################

    if 'WINGDB_ACTIVE' in os.environ:
        APP.debug = False

    APP.run(port=5000, use_reloader=False)
