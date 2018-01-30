#!/usr/bin/python
# Copyright 2018, Sourcepole AG
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

from flask import Flask, g, abort, request, Response, jsonify
from flask_cors import CORS
from itertools import accumulate
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
import math
import os
import re
import struct
import sys

app = Flask(__name__)
CORS(app)


def get_dataset():
    dataset = getattr(g, '_dataset', None)
    if dataset is None:
        dataset = g._dataset = load_dataset()
    return dataset


def load_dataset():
    dsfn = os.environ.get('ELEVATION_DATASET')
    if dsfn is None:
        abort(Response('ELEVATION_DATASET undefined', 500))

    raster = gdal.Open(dsfn)
    if not raster:
        abort(Response('Failed to open dataset', 500))

    gtrans = raster.GetGeoTransform()
    if not gtrans:
        abort(Response('Failed to read dataset geotransform', 500))

    rasterSpatialRef = osr.SpatialReference()
    if rasterSpatialRef.ImportFromWkt(raster.GetProjectionRef()) != 0:
        abort(Response('Failed to parse dataset projection', 500))

    band = raster.GetRasterBand(1)
    if not band:
        abort(Response('Failed to open dataset raster band', 500))

    rasterUnitsToMeters = 1
    if band.GetUnitType() == "ft":
        rasterUnitsToMeters = 0.3048

    dataset = {
        "raster": raster,
        "band": band,
        "spatialRef": rasterSpatialRef,
        "geoTransform": gtrans,
        "unitsToMeters": rasterUnitsToMeters
    }
    return dataset


@app.route("/getelevation", methods=['GET'])
# `/getelevation?pos=<pos>&crs=<crs>`
# pos: the query position, as `x,y`
# crs: the crs of the query position
# output: a json document with the elevation in meters: `{elevation: h}`
def getelevation():
    dataset = get_dataset()
    try:
        pos = request.args['pos'].split(',')
        pos = [float(pos[0]), float(pos[1])]
    except:
        return jsonify({"error": "Invalid position specified"})
    try:
        epsg = int(re.match(r'epsg:(\d+)', request.args['crs'], re.IGNORECASE).group(1))
    except:
        return jsonify({"error": "Invalid projection specified"})

    inputSpatialRef = osr.SpatialReference()
    if inputSpatialRef.ImportFromEPSG(epsg) != 0:
        return jsonify({"error": "Failed to parse projection"})

    crsTransform = osr.CoordinateTransformation(inputSpatialRef, dataset["spatialRef"])
    gtrans = dataset["geoTransform"]

    pRaster = crsTransform.TransformPoint(pos[0], pos[1])

    # Geographic coordinates to pixel coordinates
    col = ( -gtrans[0] * gtrans[5] + gtrans[2] * gtrans[3] - gtrans[2] * pRaster[1] + gtrans[5] * pRaster[0] ) / ( gtrans[1] * gtrans[5] - gtrans[2] * gtrans[4] )
    row = ( -gtrans[0] * gtrans[4] + gtrans[1] * gtrans[3] - gtrans[1] * pRaster[1] + gtrans[4] * pRaster[0] ) / ( gtrans[2] * gtrans[4] - gtrans[1] * gtrans[5] )

    data = dataset["band"].ReadRaster(math.floor(col), math.floor(row), 2, 2, 2, 2, gdal.GDT_Float64)
    if not data or len(data) != 32:
        return jsonify({"elevation": 0})
    else:
        values = struct.unpack('d' * 4, data)
        kRow = row - math.floor( row );
        kCol = col - math.floor( col );
        value = ( values[0] * ( 1. - kCol ) + values[1] * kCol ) * ( 1. - kRow ) + ( values[2] * ( 1. - kCol ) + values[3] * kCol ) * ( kRow )
        return jsonify({"elevation": value * dataset["unitsToMeters"]})


@app.route("/getheightprofile", methods=['POST'])
# `/getheightprofile`
# payload: a json document as follows:
#        {
#            coordinates: [[x1,y1],[x2,y2],...],
#            distances: [<dist_x1_x2>, <dist_x2_x3>, ...],
#            projection: <EPSG:XXXX, projection of coordinates>,
#            samples: <number of height samples to return>
#        }
# output: a json document with heights in meters: `{elevations: [h1, h2, ...]}`
def getheightprofile():
    dataset = get_dataset()
    query = request.json

    if not isinstance(query, dict) or not "projection" in query or not "coordinates" in query or not "distances" in query or not "samples" in query:
        return jsonify({"error": "Bad query"})

    if not isinstance(query["coordinates"], list) or len(query["coordinates"]) < 2:
        return jsonify({"error": "Insufficient number of coordinates specified"})

    if not isinstance(query["distances"], list) or len(query["distances"]) != len(query["coordinates"]) - 1:
        return jsonify({"error": "Invalid distances specified"})

    try:
        epsg = int(re.match(r'epsg:(\d+)', query["projection"], re.IGNORECASE).group(1))
    except:
        return jsonify({"error": "Invalid projection specified"})

    try:
        numSamples = int(query["samples"])
    except:
        return jsonify({"error": "Invalid sample count specified"})

    inputSpatialRef = osr.SpatialReference()
    if inputSpatialRef.ImportFromEPSG(epsg) != 0:
        return jsonify({"error": "Failed to parse projection"})

    crsTransform = osr.CoordinateTransformation(inputSpatialRef, dataset["spatialRef"])
    gtrans = dataset["geoTransform"]

    elevations = []

    x = 0
    i = 0
    p1 = query["coordinates"][i]
    p2 = query["coordinates"][i + 1]
    dr = (p2[0] - p1[0], p2[1] - p1[1])
    n = math.sqrt(dr[0] * dr[0] + dr[1] * dr[1])
    dr = [dr[0] / n, dr[1] / n]
    cumDistances = list(accumulate(query["distances"]))
    cumDistances.insert(0, 0)
    totDistance = sum(query["distances"])
    for s in range(0, numSamples):
        while i + 2 < len(cumDistances) and x > cumDistances[i + 1]:
            i += 1
            p1 = query["coordinates"][i]
            p2 = query["coordinates"][i + 1]
            dr = (p2[0] - p1[0], p2[1] - p1[1])
            n = math.sqrt(dr[0] * dr[0] + dr[1] * dr[1])
            dr = [dr[0] / n, dr[1] / n]

        mu = x - cumDistances[i]
        pRaster = crsTransform.TransformPoint(p1[0] + mu * dr[0], p1[1] + mu * dr[1])

        # Geographic coordinates to pixel coordinates
        col = ( -gtrans[0] * gtrans[5] + gtrans[2] * gtrans[3] - gtrans[2] * pRaster[1] + gtrans[5] * pRaster[0] ) / ( gtrans[1] * gtrans[5] - gtrans[2] * gtrans[4] )
        row = ( -gtrans[0] * gtrans[4] + gtrans[1] * gtrans[3] - gtrans[1] * pRaster[1] + gtrans[4] * pRaster[0] ) / ( gtrans[2] * gtrans[4] - gtrans[1] * gtrans[5] )

        data = dataset["band"].ReadRaster(math.floor(col), math.floor(row), 2, 2, 2, 2, gdal.GDT_Float64)
        if not data or len(data) != 32:
            elevations.append(0.)
        else:
            values = struct.unpack('d' * 4, data)
            kRow = row - math.floor( row );
            kCol = col - math.floor( col );
            value = ( values[0] * ( 1. - kCol ) + values[1] * kCol ) * ( 1. - kRow ) + ( values[2] * ( 1. - kCol ) + values[3] * kCol ) * ( kRow )
            elevations.append(value * dataset["unitsToMeters"])

        x += totDistance / (numSamples - 1)

    return jsonify({"elevations": elevations})


if __name__ == "__main__":
    app.run(debug=True, port=5002)
