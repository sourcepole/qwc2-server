#!/usr/bin/python
# Copyright 2018, Sourcepole AG
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import hashlib
import random
import json
try:
    from urllib.parse import urlparse, parse_qs
except:
    from urlparse import urlparse, parse_qs

app = Flask(__name__)
CORS(app)

permalinks = {}

@app.route("/createpermalink", methods=['GET','POST'])
# /createpermalink?url=<url>
# url: the url for which to generate a permalink
# payload: a json document with additional state information
# output: a json document: `{permalink: <permalink_url>}`
def createpermalink():
    url = request.args['url']
    parts = urlparse(url)
    query = parse_qs(parts.query)
    for key in query:
        query[key] = query[key][0]
    data = {
        "query": query
    }
    if request.method == 'POST':
        data["state"] = request.json
    datastr = json.dumps(data).encode('utf-8')
    hexdigest = hashlib.sha224(datastr).hexdigest()[0:9]
    while hexdigest in permalinks and permalinks[hexdigest] != parts.query:
        hexdigest = hashlib.sha224(datastr + bytes(random.random())).hexdigest()[0:9]
    permalinks[hexdigest] = data
    result = {
        "permalink": parts.scheme + "://" + parts.netloc + parts.path + "?k=" + hexdigest
    }
    return jsonify(**result)

@app.route("/resolvepermalink")
# /resolvepermalink?key=<key>
# key: the key query parameter of the permalink url
# output: a json document: `{query: <query_parameters>, state: <state>}`
#   - `query_parameters`: all query parameters of the URL passed to `createpermalink`
#   - `state`: the state data passed as POST payload to `createpermalink`
def resolvepermalink():
    key = request.args['key']
    data = {}
    if key in permalinks:
        data = permalinks[key]
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True,port=5001)
