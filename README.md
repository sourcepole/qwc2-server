QWC2 Services
=============

Certain QGIS Web Client (QWC2) components call web services, e.g. for generating permalinks.

This repository contains some sample services for testing.

The services are [Flask](http://flask.pocoo.org/) applications, written in Python.


Setup
-----

Install dependencies:

    # Flask package on Debian/Ubuntu
    sudo apt-get install python-flask

    # Flask from PyPI
    pip install --user flask
    pip install --user Flask-Cors


Permalink service
-----------------

Run as

    python permalink.py

API:

* Runs by default on `http://localhost:5000`
* `POST: /createpermalink?url=<url>`
  - *url*: the url for which to generate a permalink
  - *payload*: a json document with additional state information
  - *output*: a json document: `{permalink: <permalink_url>}`
* `GET: /resolvepermalink?key=<key>`
  - *key*: the key query parameter of the permalink url
  - *output*: a json document: `{query: <query_parameters>, state: <state>}`
    - `query_parameters`: all query parameters of the URL passed to `createpermalink`
    - `state`: the state data passed as POST payload to `createpermalink`

Elevation service
-----------------

Run as

    python elevation.py <path/to/dtm.tif>

API:
* Runs by default on `http://localhost:5001`
* `POST: /`
  - *payload*: a json document as follows:

        {
            coordinates: [[x1,y1],[x2,y2],...],
            distances: [<dist_x1_x2>, <dist_x2_x3>, ...],
            projection: <EPSG:XXXX, projection of coordinates>
        }

  - *output*: a json document with heights in meters: `{elevations: [h1, h2, ...]}`
