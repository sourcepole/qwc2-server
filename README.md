QWC2 Services
=============

Certain QGIS Web Client (QWC2) components call web services, e.g. for generating permalinks.

This repository contains some sample services for testing.

The services are [Flask](http://flask.pocoo.org/) applications, written in Python.


Proxy service
-------------

Proxies requests, adding the CORS headers

Run as

    python proxy.py

API:
* Runs by default on `http://localhost:5000`
* `GET, POST, PUT, DELETE: /?url=<url>&filename=<filename>`
  - *url*: the url to proxy
  - *filename*: optional, if set it sets a content-disposition header with the specified filename


Permalink service
-----------------

Generates and resolves compact permalinks.

Run as

    python permalink.py

API:
* Runs by default on `http://localhost:5001`
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

Returns elevations.

Run as

    python elevation.py <path/to/dtm.tif>

Requires GDAL Python bindings. `python-gdal` or `python3-gdal` packages on Debian/Ubuntu.

API:
* Runs by default on `http://localhost:5002`
* `GET: /getelevation?pos=<pos>&crs=<crs>`
  - *pos*: the query position, as `x,y`
  - *crs*: the crs of the query position
  - *output*: a json document with the elevation in meters: `{elevation: h}`
* `POST: /getheightprofile`
  - *payload*: a json document as follows:

        {
            coordinates: [[x1,y1],[x2,y2],...],
            distances: [<dist_p1_p2>, <dist_p2_p3>, ...],
            projection: <EPSG:XXXX, projection of coordinates>,
            samples: <number of height samples to return>
        }

  - *output*: a json document with heights in meters: `{elevations: [h1, h2, ...]}`

Map info service
----------------

Returns additional information for the right-click map-info tooltip.

Run as

    python mapInfo.py

API:
* Runs by default on `http://localhost:5003`
* `GET: /?pos=<pos>&crs=<crs>`
  - *pos*: the query position, as `x,y`
  - *crs*: the crs of the query position
  - *output*: a json document with map info for the specified position: `{results: [[title1, value1], [title2, value2], ...]}`
