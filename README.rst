RecordExpress
=============

RecordExpress lightweight EAD generator
---------------------------------------

A tool for creating lightweight, high level descriptive EAD files to which you can attach an internet hosted pdf file containing detailed collection descriptions.

Currently uses the DjangoDublinCore models, which makes the admin interface a bit brittle (need to have correct qualifier text field to make export correct).
I want to refactor into a direct EAD model of the data. This will cause numerous tables to be created but will simplify the design.

It currently also has a number of dependencies on OAC data and software.

TODO
----

0. fix problem with new django-sortable package
1. Test project bundled with package.
2. Make tests pass on clean install. 
3. Detail the mapping of QDC to EAD elements.
4. How to make the "preview" work when not on an OAC box?
5. Refactor to remove DjangoDublinCore and use direct foreign key metadata fields.
6. Add creating the DB and initializing a publishing institution on install or first run of server.
7. Add usage in typical workflow. Create repo, create EAD and then cut & paste?

QUICKSTART
----------

You'll need a python 2 (2.6, 2.7 have been tested) installed on your machine with `setuptools <https://pypi.python.org/pypi/setuptools>`_ installed. 
You'll also need a github client (if you don't have git goto `github:windows <http://windows.github.com/>`_ or `github:mac <http://mac.github.com/>`_)

TODO: add virtualenv setup, gets around admin privileges.

1. Install python (`http://www.python.org/download/ <http://www.python.org/download/>`_).
2. Install setuptools (`setuptools <https://pypi.python.org/pypi/setuptools>`_). 
3. From your GitHub client clone `https://github.com/cdlib/RecordExpress.git <https://github.com/cdlib/RecordExpress.git>`_
4. Move to the RecordExpress directory in a terminal.
5. At the command prompt run::

    python setup.py install

6. At command prompt run::

    python test_project\manage.py runserver

7. Point your browser at `http://localhost:8000/admin <http://localhost:8000/admin>`_. Login is admin:admin. `http://localhost:8000/collection-record <http://localhost:8000/collection-record>`_ is the entrance to the application for end user creation of collection records.

