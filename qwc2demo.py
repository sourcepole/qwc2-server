from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import requests
import os
import hashlib
import random
try:
    from urllib.parse import urlparse, parse_qs
except:
    from urlparse import urlparse, parse_qs

app = Flask(__name__)
CORS(app)

permalinks = {}

@app.route("/proxy")
def proxy():
    url = request.args.get('url')
    filename = request.args.get('filename')
    req = requests.get(url, stream=True, timeout=5)
    response = Response(stream_with_context(req.iter_content()))
    if filename:
        response.headers['content-disposition'] = 'attachment; filename=' + filename
    else:
        response.headers['content-type'] = req.headers['content-type']
    return response

@app.route("/createpermalink")
def createpermalink():
    url = request.args['url']
    parts = urlparse(url)
    hexdigest = hashlib.sha224(parts.query.encode("utf-8")).hexdigest()[0:9]
    while hexdigest in permalinks and permalinks[hexdigest] != parts.query:
        hexdigest = hashlib.sha224(parts.query.encode("utf-8") + str(random.random())).hexdigest()[0:9]
    permalinks[hexdigest] = parts.query
    result = {
        "permalink": parts.scheme + "://" + parts.netloc + parts.path + "?k=" + hexdigest,
        "permalinks": permalinks,
    }
    return jsonify(**result)

@app.route("/resolvepermalink")
def resolvepermalink():
    key = request.args['key']
    result = {}
    if key in permalinks:
        query = parse_qs(permalinks[key])
        for key in query:
            query[key] = query[key][0]
        result['query'] = query
    return jsonify(**result)

@app.route("/search")
def search():
    # QWC API Uster
    query = request.args['query']
    # https://webgis.uster.ch/wsgi/search.wsgi?&searchtables=&query=Greifensee
    result = {
        "results": [
            {
                "searchtable": None,
                "display_name": "Bodenbedeckungsname",
                "boundingbox": [0, 0, 0, 0]
            },
            {
                "searchtable": "av_user.suchtabelle",
                "display_name": "Greifensee (Niederuster, Gew\u00e4sser stehendes)",
                "boundingbox": [
                    693792.00009343,
                    242423.70345183,
                    695931.8623783,
                    245435.1384952
                ]
            },
            {
                "searchtable": "av_user.suchtabelle",
                "display_name": "Greifensee (Riedikon, Gew\u00e4sser stehendes)",
                "boundingbox": [
                    693792.00009343,
                    242423.70345183,
                    695931.8623783,
                    245435.1384952
                ]
            },
            {
                "searchtable": None,
                "display_name": "Flurnamen",
                "boundingbox": None
            },
            {
                "searchtable": "av_user.suchtabelle",
                "display_name": "Greifensee (Flurname, Uster)",
                "boundingbox": [
                    693792.00009343,
                    242404.13851517,
                    695957.0926848,
                    245459.80353041
                ]
            },
            {
                "searchtable": None,
                "display_name": "Strassen",
                "boundingbox": None
            },
            {
                "searchtable": "av_user.suchtabelle",
                "display_name": "Greifenseestrasse (Strasse, Uster)",
                "boundingbox": [
                    693868.82257669,
                    247149.7305494,
                    694092.20209108,
                    247621.97038983
                ]
            }
        ]
    }
    return jsonify(**result)


@app.route("/getSearchGeom")
def getSearchGeom():
    # QWC API Uster
    # https://webgis.uster.ch/wsgi/getSearchGeom.wsgi?&searchtable=av_user.suchtabelle&display_name=1001%20(Parzellennummer)
    return 'POLYGON((693957.29 246878.75,693944.31 246875.8,693941.144 246877.851,693959.07 246904.701,693965.016 246900.731,693962.24 246896.572,693964.402 246895.129,693967.179 246899.287,693972.777 246895.549,693972.69 246895.369,693961.67 246876.32,693957.29 246878.75))'


if __name__ == "__main__":
    app.run(debug=True)
