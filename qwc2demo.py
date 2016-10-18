from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import requests
import os
import base64
from PyQt4.QtCore import *
from PyQt4.QtXml import *

app = Flask(__name__)
CORS(app)

def getSubdir(group, dir):
    for subdir in group["subdirs"]:
        if subdir["name"] == dir:
            return subdir
    entry = {"name": dir, "subdirs": [], "items": []}
    group["subdirs"].append(entry)
    return entry

def getBase64img(path):
    with open(path, "rb") as file:
        return base64.b64encode(file.read()).decode('ascii')
    return ""

def getProjectData(projectfile):
    file = QFile(projectfile)
    if not file.open(QIODevice.ReadOnly):
        return {"keywords": "", "layers": []}
    doc = QDomDocument()
    doc.setContent(file)

    # CRS & Extent
    crs = doc.firstChildElement("qgis").firstChildElement("mapcanvas").firstChildElement("destinationsrs").firstChildElement("spatialrefsys").firstChildElement("authid").text()
    extent = doc.firstChildElement("qgis").firstChildElement("mapcanvas").firstChildElement("extent")
    xmin = float(extent.firstChildElement("xmin").text() or "0")
    xmax = float(extent.firstChildElement("xmax").text() or "0")
    ymin = float(extent.firstChildElement("ymin").text() or "0")
    ymax = float(extent.firstChildElement("ymax").text() or "0")

    # Nonidentifyable layers
    disabledLayerList = doc.firstChildElement("qgis").firstChildElement("properties").firstChildElement("Identify").firstChildElement("disabledLayers").elementsByTagName("value")
    disabledLayers = []
    for i in range(0, disabledLayerList.size()):
        disabledLayers.append(disabledLayerList.at(i).toElement().text())

    # Keywords
    kwlists = doc.elementsByTagName("WMSKeywordList")
    keywords = ""
    if not kwlists.isEmpty():
        keywords = kwlists.at(0).firstChildElement("value").text()

    # Layers
    layerlist = doc.elementsByTagName("maplayer")
    layers = []
    queryable = []
    for i in range(0, layerlist.size()):
        shortname = layerlist.at(i).firstChildElement("shortname").text()
        layername = layerlist.at(i).firstChildElement("layername").text()
        name = shortname if shortname else layername
        id = layerlist.at(i).firstChildElement("id").text()
        layers.append(name)
        if id not in disabledLayers:
            queryable.append(name)

    return {"keywords": keywords, "layers": layers, "queryable": queryable, "extent": [xmin, ymin, xmax, ymax], "crs": crs}

@app.route("/getthemes")
def gettopics():
    try:
        root = os.path.join(os.path.dirname(__file__), "themes")
        result = {"themes": {"name": "root", "subdirs": [], "items": []}}
        themes = result["themes"]
        for dirname, subdirs, filelist in os.walk(root):
            projects = [filename for filename in filelist if filename.lower().endswith('.qgs')]
            if not projects:
                continue
            dirs = [dir for dir in dirname.replace(root, '').split(os.path.sep) if dir]
            groupdict = themes
            for dir in dirs:
                groupdict = getSubdir(groupdict, dir)
            for project in projects:
                entry = {
                    "id": project[:-4],
                    "name": project[:-4],
                    "url": "http://qwc2.sourcepole.ch/wms/" + dirname + "/" + project[:-4],
                    "thumbnail": getBase64img(os.path.join(dirname, project[:-4] + ".png")),
                }
                entry.update(getProjectData(os.path.join(dirname, project)))
                groupdict["items"].append(entry)
    except Exception as e:
        result = {"error": str(e)}
    return jsonify(**result)

@app.route("/proxy")
def proxy():
    url = request.args['url']
    req = requests.get(url, stream = True)
    return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])

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
