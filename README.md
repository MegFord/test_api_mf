README
======
1) Spin up an api in your framework of choice (bonus points for making it an flask app)
2) Create endpoints that creates/updates/deletes students
3) Create endpoints that creates/updates/deletes classes for a student (No need to ask for a preset list of classes as you can make them up yourself arbitrarily)
4) Create an endpoint that shows all students
5) Create an endpoint that shows all classes for a given student
6) The data has to be persisted in a data store
7) Write a test or two to demonstrate your ability to feature/unit test - use a testing framework of your choice.

OS requirements:
    postgresql-9.4
    virtualenv

Clone repo and cd into repo

Create virtualenv:
    $ virtualenv env
    $ . env/bin/activate

Install requirements:
    $ pip3 install -r requirements.txt

Set up database:
    == Linux ==
    $ su - postgres
    $ createuser -P studentuser # password abc123
    $ createdb student
    $ psql -c 'GRANT CREATE ON DATABASE student TO studentuser;'
    == Mac ==
    $ psql postgres
    # CREATE ROLE studentuser;
    # ALTER USER studentuser WITH ENCRYPTED PASSWORD 'abc123';
    # ALTER USER studentuser CREATEDB;
    # CREATE DATABASE student;

Run Django migrations on the database:
    $ python manage.py makemigrations
    $ python manage.py migrate

Run the server:
    $ python manage.py runserver

Run the tests:
    $ python manage.py tests

