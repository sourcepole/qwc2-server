from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import requests
import os
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

@app.route("/proxy", methods=['GET','POST','PUT','DELETE'])
# proxy?url=<url>&filename=<filename>
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

@app.route("/createpermalink", methods=['GET','POST'])
# createpermalink?url=<url>
# url: the url for which to generate a permalink
# output: a json document {permalink: <permalink_url>}
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
        hexdigest = hashlib.sha224(datastr + str(random.random())).hexdigest()[0:9]
    permalinks[hexdigest] = data
    result = {
        "permalink": parts.scheme + "://" + parts.netloc + parts.path + "?k=" + hexdigest
    }
    return jsonify(**result)

@app.route("/resolvepermalink")
# resolvepermalink?key=<key>
# key: the key query parameter of the permalink url
# output: a json document containing all query parameters which were encoded in the permalink key
def resolvepermalink():
    key = request.args['key']
    data = {}
    if key in permalinks:
        data = permalinks[key]
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
