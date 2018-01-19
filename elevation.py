#!/usr/bin/python

from flask import Flask, request, jsonify
from flask_cors import CORS
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


@app.route("/", methods=['POST'])
def elevation():
    numSamples = 500

    query = request.json

    if not isinstance(query, dict) or not "projection" in query or not "coordinates" in query or not "distances" in query:
        return jsonify({"error": "Bad query"})

    if not isinstance(query["coordinates"], list) or len(query["coordinates"]) == 0:
        return jsonify({"error": "Invalid or empty coordinates specified"})

    if not isinstance(query["distances"], list) or len(query["distances"]) != len(query["coordinates"]) - 1:
        return jsonify({"error": "Invalid distances specified"})

    try:
        epsg = int(re.match(r'epsg:(\d+)', query["projection"], re.IGNORECASE).group(1))
    except:
        return jsonify({"error": "Invalid projection specified"})

    inputSpatialRef = osr.SpatialReference()
    if inputSpatialRef.ImportFromEPSG(epsg) != ogr.OGRERR_NONE:
        return jsonify({"error": "Failed to parse projection"})

    raster = gdal.Open(sys.argv[1])
    if not raster:
        return jsonify({"error": "Failed to open dataset"})

    gtrans = raster.GetGeoTransform()
    if not gtrans:
        return jsonify({"error": "Failed to read dataset geotransform"})

    rasterSpatialRef = osr.SpatialReference()
    if rasterSpatialRef.ImportFromWkt(raster.GetProjectionRef()) != ogr.OGRERR_NONE:
        return jsonify({"error": "Failed to parse dataset projection"})

    band = raster.GetRasterBand(1)
    if not band:
        return jsonify({"error": "Failed to open dataset raster band"})

    rasterUnitsToMeters = 1
    if band.GetUnitType() == "ft":
        rasterUnitsToMeters = 0.3048

    crsTransform = osr.CoordinateTransformation(inputSpatialRef, rasterSpatialRef)

    elevations = []

    x = 0
    totDistance = sum(query["distances"])
    for i in range(0, len(query["coordinates"]) - 1):
        if x >= query["distances"][i]:
            continue
        p1 = query["coordinates"][i]
        p2 = query["coordinates"][i + 1]
        dr = (p2[0] - p1[0], p2[1] - p1[1])
        n = math.sqrt(dr[0] * dr[0] + dr[1] * dr[1])
        dr = [dr[0] / n, dr[1] / n]

        while x < query["distances"][i]:
            point = [p1[0] + x * dr[0], p1[1] + x * dr[1]]
            pRaster = crsTransform.TransformPoint(point[0], point[1])

            # Geographic coordinates to pixel coordinates
            col = ( -gtrans[0] * gtrans[5] + gtrans[2] * gtrans[3] - gtrans[2] * pRaster[1] + gtrans[5] * pRaster[0] ) / ( gtrans[1] * gtrans[5] - gtrans[2] * gtrans[4] )
            row = ( -gtrans[0] * gtrans[4] + gtrans[1] * gtrans[3] - gtrans[1] * pRaster[1] + gtrans[4] * pRaster[0] ) / ( gtrans[2] * gtrans[4] - gtrans[1] * gtrans[5] )

            data = band.ReadRaster(math.floor(col), math.floor(row), 2, 2, 2, 2, gdal.GDT_Float64)
            if not data or len(data) != 32:
                elevations.append(0.)
            else:
                values = struct.unpack('d' * 4, data)
                kRow = row - math.floor( row );
                kCol = col - math.floor( col );
                value = ( values[0] * ( 1. - kCol ) + values[1] * kCol ) * ( 1. - kRow ) + ( values[2] * ( 1. - kCol ) + values[3] * kCol ) * ( kRow )
                elevations.append(value)
            x += totDistance / numSamples
        x -= query["distances"][i]

    return jsonify({"elevations": elevations})

if __name__ == "__main__":
    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
        print("Usage: %s dtm.tif" % sys.argv[0], file=sys.stderr)
        sys.exit(1)

    app.run(debug=True, port=5001)
