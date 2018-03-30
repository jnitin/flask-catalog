# Calories

Flask application with a REST API to track calories, following JSON API 1.0 specification


### Features
1. API users can create an account and log in.

2. All API calls are authenticated. 

3. New users need to verify their account by email. Users are not able to log in until this verification is complete.

4. There are three roles with different permission levels: 
 (-) a regular user, who is only able to CRUD their own records
 (-) a user manager, who is able to CRUD only users
 (-) an admin, who is able to CRUD all records and users

5. When a user fails to log in three times in a row, his or her account will be blocked automatically, and only admins and managers are able to unblock it.

6. An admin is able to invite someone to the application by specifying an email address; the system will send an invitation message automatically, prompting the user to complete the registration by setting first name, last name, and password.

7. Users are able to upload and change their profile picture.

8. Users can post 'meals', and each meal has a date, time, text, and number of calories.

9. If the number of calories is not provided, the API will connect to [Nutritionix](https://www.nutritionix.com) and try to get the number of calories for the entered meal.

10. In a user setting, a target number of calories per day is defined.

11. When retrieving the details for a meal an extra boolean field is set to true if the total for that day is less than expected number of calories per day, otherwise it will be false.

12. The API return data according to the [JSON API 1.0](http://jsonapi.org/) specification

13. The API provides filter capabilities for all endpoints that return a list of elements, and supports pagination.

14. The API filtering allows definition of operations precedence and use any combination of the available fields.

15. The application includes rigorous unit tests.

16. End 2 end scenarios are tested via a python client written in a [Jupyter notebook](http://jupyter.org/)


### Framework & Extensions

The application is written in [Python 3](https://www.python.org/) using the [Flask](http://flask.pocoo.org/)  microframework, with following extensions.

- [Flask-REST-JSONAPI](http://flask-rest-jsonapi.readthedocs.io/en/latest/)
- [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org)
- [Flask-Bcrypt](https://flask-bcrypt.readthedocs.io/en/latest/)
- [Flask-HTTPAuth](https://flask-httpauth.readthedocs.io/en/latest/)
- [Flask-Login](https://flask-login.readthedocs.io/en/latest/)
- [Flask-Mail](https://pythonhosted.org/Flask-Mail/)
- [Flask-Uploads](https://pythonhosted.org/Flask-Uploads/)


The front-end HTML pages are generated with:

- [Flask-WTF](https://flask-wtf.readthedocs.io)
- [Bootstrap V4.0.0](https://getbootstrap.com/) (*)


The end-2-end test client is written in Python with following extensions:

- [requests](http://docs.python-requests.org/en/master/)
- [Pillow](https://pillow.readthedocs.io/en/latest/)


(*) We do not install Bootstrap V4.0.0, but use a CDN.

### API usage

The API is demonstrated in this [end-2-end test scenario](link-to-HTML).

(The link is an HTML export of this [Jupyter notebook](link-to-notebook) after all cells were run.)


### Installation

Development and testing was done on Ubuntu 16.04, using Python 3.5

The steps described here show how to run <b>calories</b> within a python virtual environment.

**Step 1. Clone the project repository**
```bash
$ git clone https://github.com/ArjaanBuijk/Calories.git
```

**Step 2. Configure project**
Install the secret configuration file into: Calories/instance/config.py
Note that for security reasons this configuration file is not included in the github repository.

**Step 3. One time: make sure python3-pip and python3-env are installed**
```bash
$ sudo apt install python3-pip
$ sudo apt-get install python3-venv
```

**Step 4. One time: prepare the python3 virtual environment**
```bash
$ cd Calories
$ python3 -m venv venv
$ source venv/bin/activate
(venv)
(venv) $ pip install --upgrade pip
(venv) $ pip install -r requirements.txt
```

 Alternatively, instead of installing the required python packages using the file 'requirements.txt', which installs the specific versions that were used during development and testing, you can also enter these commands, to install the latest version of each package:
```bash
$ cd Calories
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install --upgrade pip
(venv) $ pip install flask
(venv) $ pip install Flask-REST-JSONAPI
(venv) $ pip install flask-sqlalchemy
(venv) $ pip install flask-bcrypt
(venv) $ pip install flask-httpauth
(venv) $ pip install flask-login
(venv) $ pip install flask-mail
(venv) $ pip install flask-uploads
(venv) $ pip install Flask-WTF
(venv) $ pip install requests
(venv) $ pip install Pillow
```

**Step 5. Activate the python virtual environment and start the application server**
```bash
$ cd Calories
$ source venv/bin/activate
(venv) $ export FLASK_APP=calories.py
(venv) $ flask run
```

 You will see this output printed to the console:
 ```bash
 Connecting to existing data-base...
 * Serving Flask app "calories"
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 ```

### Notes for developer

**Start with a clean database**

To start with a clean and fresh database, just remove the existing database before starting the application:

```bash
$ cd Calories
$ source venv/bin/activate
(venv) $ rm app.db
(venv) $ export FLASK_APP=calories.py
(venv) $ flask run
```

You will see this output printed to the console:

```bash
 Creating & initializing a new data-base...
 * Serving Flask app "calories"
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```



For end-2-end testing, a Jupyter notebook with the python 3 kernel is used. 
This must be installed and configured with:

```bash
(venv) $ pip install --upgrade pip
(venv) $ pip install jupyter
(venv) $ pip install ipykernel
(venv) $ python3 -m ipykernel install --user
```

For validating python syntax, pylint is used. This can be installed with:

```bash
(venv) $ pip install --upgrade pip
(venv) $ pip install pylint
```

