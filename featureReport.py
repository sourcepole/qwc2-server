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
# x: x coordinate of click which selected the feature
# y: y coordinate of click which selected the feature
# crs: crs of click coordinates
# output: A blob with matching content-type
def featurereport():
    template = request.args['template']
    feature = request.args['feature']
    x = request.args['x']
    y = request.args['y']
    crs = request.args['crs']
    return Response("Feature report for feature %s (at %s, %s %s), using template %s" % (feature, x, y, crs, template), mimetype='text/plain')


if __name__ == "__main__":
    app.run(debug=True,port=5020)
