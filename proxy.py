#!/usr/bin/python
# Copyright 2018, Sourcepole AG
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route("/", methods=['GET','POST','PUT','DELETE'])
# /?url=<url>&filename=<filename>
# url: the url to proxy
# filename: optional, if set it sets a content-disposition header with the specified filename
def proxy():
    url = request.args.get('url')
    filename = request.args.get('filename')
    if request.method == 'POST':
        headers={'content-type': request.headers['content-type']}
        req = requests.post(url, stream=True, timeout=30, data=request.get_data(), headers=headers)
    elif request.method == 'PUT':
        headers={'content-type': request.headers['content-type']}
        req = requests.put(url, stream=True, timeout=30, data=request.get_data(), headers=headers)
    elif request.method == 'DELETE':
        req = requests.delete(url, stream=True, timeout=10)
    elif request.method == 'GET':
        req = requests.get(url, stream=True, timeout=10)
    else:
        raise "Invalid operation"
    response = Response(stream_with_context(req.iter_content(chunk_size=1024)), status=req.status_code)
    if filename:
        response.headers['content-disposition'] = 'attachment; filename=' + filename
    response.headers['content-type'] = req.headers['content-type']
    return response

if __name__ == "__main__":
    app.run(debug=True, port=5000)
