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

@app.route("/proxy", methods=['GET','POST'])
def proxy():
    url = request.args.get('url')
    filename = request.args.get('filename')
    if request.method == 'POST':
        req = requests.post(url, stream=True, timeout=30, data=request.form)
    else:
        req = requests.get(url, stream=True, timeout=10)
    response = Response(stream_with_context(req.iter_content(chunk_size=1024)))
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

if __name__ == "__main__":
    app.run(debug=True)
