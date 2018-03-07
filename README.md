# Catalog

---
## Overview
This is a project for the Udacity Full Stack Web Developer Nanodegree.

A web application is created with the Flask framework. These are the requirements:
- It provides a catalog of items within a variety of categories.
- The application provides a user registration and authentication system.
- Registered users have the ability to post, edit and delete their own items.
- The application has both an HTML frontend and a REST API as backend.

The items I chose to catalog are jokes. One can envision this as a first step towards a market place like eBay, where comedians can upload their jokes, which are consumed by the public, by registered users and other comedians, either for free, through subscription or pay-per-joke mechanisms.

The first step in such an endeavor is to create a catalog of jokes, which is done in this project.


## Framework & Extensions

The application is using the Flask (Python microframework), using several extensions.

##### Flask Extensions
TODO: UPDATE THIS
- [SQLAlchemy](http://www.sqlalchemy.org) and [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org)
- [WTForms](http://wtforms.readthedocs.io) and [Flask-WTF](https://flask-wtf.readthedocs.io).
- [Flask-Login](https://flask-login.readthedocs.io)
- [Flask-Testing](https://pythonhosted.org/Flask-Testing/)
- [Flask-RESTful](http://flask-restful-cn.readthedocs.io/)

##### Frontend
TODO: UPDATE THIS

- [HTML5 Boilerplate](https://github.com/h5bp/html5-boilerplate)
- [jQuery](http://jquery.com/)
- [Twitter Bootstrap](https://github.com/twitter/bootstrap)
- [Jinja2](http://jinja.pocoo.org/docs/dev/)


## Project Structure
TODO: UPDATE THIS

The project structure is based on [fbone](https://github.com/imwilsonxu/fbone), with some small changes.

    ├── CHANGES                     Change logs
    ├── README.md
    ├── fabfile.py                  Fabric file to automated managament project
    ├── application.conf            Apache config
    ├── requirements.txt            3rd libraries
    ├── tests.py                    Unittests
    ├── wsgi.py                     Wsgi app
    ├── application
       ├── __init__.py
       ├── app.py                   Main App
       ├── config.py                Develop / Testing configs
       ├── constants.py             Constants
       ├── decorators.py            Customized decorators
       ├── extensions.py            Flask extensions
       ├── filters.py               Flask filters
       ├── utils.py                 Python utils
       ├── frontend                 Frontend blueprint
       │   ├── __init__.py
       │   ├── forms.py             Forms used in frontend modular
       │   ├── views.py             Views used in frontend modular
       ├── user
       ├── api
       ├── static                   Static files
       │   ├── css
       │   ├── favicon.png
       │   ├── humans.txt
       │   ├── img
       │   ├── js
       │   └── robots.txt
       └── templates                Jinja2 templates
           ├── errors
           ├── frontend
           ├── index.html
           ├── layouts              Jinja2 layouts
           │   ├── base.html
           │   └── user.html
           ├── macros               Jinja2 macros
           ├── mails                Mail templates
           └── user


## Usage

The project is written for Python 3

Development and testing was done on Ubuntu 16.04, using Python 3.5

The steps described here show how to run <b>catalog</b> within a python virtual environment.

1. Clone the project repository
```bash
$ git clone https://github.com/ArjaanBuijk/FullstackND-Catalog
```

2. One time: prepare the python virtual environment
```bash
$ cd FullstackND-Catalog
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install --upgrade pip
(venv) $ pip install -r requirements.txt
```

 Alternatively, instead of installing the required python packages using the file <em>'requirements.txt'</em>, which installs the specific versions that were used during development and testing, you can also enter these commands, to install the latest version of each package:
```bash
$ cd FullstackND-Catalog
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install --upgrade pip
(venv) $ pip install flask
(venv) $ pip install Flask-REST-JSONAPI
(venv) $ pip install flask-sqlalchemy
(venv) $ pip install requests
(venv) $ pip install flask-bcrypt
(venv) $ pip install flask-httpauth
(venv) $ pip install flask-login
(venv) $ pip install Flask-WTF
(venv) $ pip install flask-testing
(venv) $ pip install blinker
```

3. Activate the python virtual environment and start the application server
```bash
$ cd FullstackND-Catalog
$ source venv/bin/activate
(venv) $ export FLASK_APP=catalog.py
(venv) $ flask run
```

 You should see this output printed to the console:
 ```bash
 * Serving Flask app "catalog"
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

4. Test it all works by running the unit tests
```bash
$ cd FullstackND-Catalog
$ source venv/bin/activate
(venv) $ python tests.py
```
