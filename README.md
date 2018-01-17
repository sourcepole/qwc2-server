QWC2 Server
===========

Certain QGIS Web Client (QWC2) components call web services, e.g. for generating permalinks.

This repository contains the API specification and a demo server for testing.

The demo server is a [Flask](http://flask.pocoo.org/) application, written in Python.


API
---

### `/createpermalink`

`POST: createpermalink?url=<url>`
- *url*: the url for which to generate a permalink
- *payload*: a json document with additional state information
- *output*: a json document `{permalink: <permalink_url>}`

### `/resolvepermalink`
`GET: resolvepermalink?key=<key>`
- *key*: the key query parameter of the permalink url
- *output*: a json document `{query: <query_parameters>, state: <state>}`
  - `query_parameters`: all query parameters of the URL passed to `createpermalink`
  - `state`: the state data passed as POST payload to `createpermalink`


Setup
-----

Install dependencies:

    # Flask package on Debian/Ubuntu
    sudo apt-get install python-flask

    # Flask from PyPI
    pip install --user flask
    pip install --user Flask-Cors

Run demo server:

    python qwc2demo.py
