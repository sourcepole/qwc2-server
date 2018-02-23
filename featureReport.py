#!/usr/bin/python
# Copyright 2018, Sourcepole AG
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

from flask import Flask, request, Response
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

@app.route("/")
# `/?template=<template>&feature=<feature>`
# template: a template ID
# feature: a feature ID
# output: A blob with matching content-type
def featurereport():
    template = request.args['template']
    feature = request.args['feature']
    return Response("Feature report for feature %s, using template %s" % (feature, template), mimetype='text/plain')


if __name__ == "__main__":
    app.run(debug=True,port=5020)
