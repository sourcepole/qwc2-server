QWC2 Server
===========

Certain QGIS Web Client (QWC2) components call web services, e.g. for generating permalinks.

This repository contains the API specification and a demo server for testing.

The demo server is a [Flask](http://flask.pocoo.org/) application, written in Python.


API
---

### Search

...


Setup
-----

Install dependencies:

    # Flask package on Debian/Ubuntu
    sudo apt-get install python-flask

    # Flask from PyPI
    pip install --user flask

Run demo server:

    python qwc2demo.py
