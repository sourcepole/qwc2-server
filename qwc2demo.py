from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/search")
def search():
    # QWC API Uster
    query = request.args['query']
    # https://webgis.uster.ch/wsgi/search.wsgi?&searchtables=&query=Greifensee
    result = {
        "results": [
            {
                "searchtable": None,
                "displaytext": "Bodenbedeckungsname",
                "bbox": None
            },
            {
                "searchtable": "av_user.suchtabelle",
                "displaytext": "Greifensee (Niederuster, Gew\u00e4sser stehendes)",
                "bbox": [
                    693792.00009343,
                    242423.70345183,
                    695931.8623783,
                    245435.1384952
                ]
            },
            {
                "searchtable": "av_user.suchtabelle",
                "displaytext": "Greifensee (Riedikon, Gew\u00e4sser stehendes)",
                "bbox": [
                    693792.00009343,
                    242423.70345183,
                    695931.8623783,
                    245435.1384952
                ]
            },
            {
                "searchtable": None,
                "displaytext": "Flurnamen",
                "bbox": None
            },
            {
                "searchtable": "av_user.suchtabelle",
                "displaytext": "Greifensee (Flurname, Uster)",
                "bbox": [
                    693792.00009343,
                    242404.13851517,
                    695957.0926848,
                    245459.80353041
                ]
            },
            {
                "searchtable": None,
                "displaytext": "Strassen",
                "bbox": None
            },
            {
                "searchtable": "av_user.suchtabelle",
                "displaytext": "Greifenseestrasse (Strasse, Uster)",
                "bbox": [
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
    # https://webgis.uster.ch/wsgi/getSearchGeom.wsgi?&searchtable=av_user.suchtabelle&displaytext=1001%20(Parzellennummer)
    return 'POLYGON((693957.29 246878.75,693944.31 246875.8,693941.144 246877.851,693959.07 246904.701,693965.016 246900.731,693962.24 246896.572,693964.402 246895.129,693967.179 246899.287,693972.777 246895.549,693972.69 246895.369,693961.67 246876.32,693957.29 246878.75))'


if __name__ == "__main__":
    app.run(debug=True)
