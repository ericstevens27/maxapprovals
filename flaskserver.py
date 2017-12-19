#!flask/bin/python
from flask import Flask
from flask import request
import json

app = Flask(__name__)

# choose a status flag to force specific response codes
status_flag = 'accept'
# status_flag = 'reject'
# status_flag = 'pending'
add_flag = True

adv_list = []
adv_status = {}
creative_list = []
creative_status = {}


def makeadvresponse(c1, c2, s):
    if c1 == 0:
        # good response
        good = {
            "code": 0,
            "result": [
                {
                    "advId": "",
                    "status": 1
                }
            ]
        }
        good['code'] = c1
        good['result'][0]['status'] = c2
        good['result'][0]['advId'] = s
        return good
    else:
        # bad reponse
        errorresponse = {
          "code": 0,
          "msg": "",
          "result": [
            {
              "code": 0,
              "msg": "",
              "desc": ""
            }
            ]
        }
        errorresponse['code'] = c1
        errorresponse['msg'] = s
        errorresponse['result'][0]['code'] = c2
        errorresponse['result'][0]['msg'] = s
        return errorresponse

def makecreativeresponse(c1, c2, cid, s):
    if c1 == 0:
        # good response
        good = {
            "code": 0,
            "result": [
                {
                    "materialId": "",
                    "creativeId": "",
                    "templateId": "2.4",
                    "status": 1
                }
            ]
        }
        good['code'] = c1
        good['result'][0]['status'] = c2
        good['result'][0]['materialId'] = s
        good['result'][0]['creativeId'] = cid
        return good
    else:
        # bad reponse
        errorresponse = {
          "code": 0,
          "msg": "",
          "result": [
            {
              "code": 0,
              "msg": "",
              "desc": ""
            }
            ]
        }
        errorresponse['code'] = c1
        errorresponse['msg'] = s
        errorresponse['result'][0]['code'] = c2
        errorresponse['result'][0]['msg'] = s
        return errorresponse


@app.route('/')
def index():
    return "Hello, World!"


@app.route('/v1/advertiser/query', methods=['GET'])
def get_adv():
    advid = request.args.get('advId')
    if advid in adv_status:
        advertiser_status = adv_status[advid]
    else:
        advertiser_status = 9
    if advertiser_status == 9:
        # did not find advid
        review = makeadvresponse(2, 1002, "Did not find advertiser {}".format(advid))
    else:
        review = makeadvresponse(0, advertiser_status, advid)
    return json.dumps(review), 200


@app.route('/v1/advertiser/add', methods=['POST'])
def add_advertiser():
    if not request.json or not 'advertisers' in request.json:
        bad = makeadvresponse(2, 1002, "No json or missing advertiser block")
        return json.dumps(bad), 400
    advtodadd = request.json['advertisers'][0]
    newid = len(adv_list) + 10000 + 1
    advtodadd['advId'] = newid
    newidstr = str(newid)

    adv_list.append(advtodadd)
    adv_status[newidstr] = 1

    resp = makeadvresponse(0, 0, newidstr)
    return json.dumps(resp), 200


@app.route('/v1/creative/add', methods=['POST'])
def add_creative():
    if not request.json or not 'materials' in request.json:
        bad = makeadvresponse(2, 1002, "No json or missing materials block")
        return json.dumps(bad), 400
    adtodadd = request.json['materials'][0]
    newid = len(creative_list) + 50000 + 1
    adtodadd['materialId'] = newid
    newidstr = str(newid)

    creative_list.append(adtodadd)
    creative_status[newidstr] = 1

    resp = makecreativeresponse(0, 0, adtodadd['creativeId'], newidstr)
    return json.dumps(resp), 200


@app.route('/v1/creative/query', methods=['GET'])
def get_creative():
    matid = request.args.get('materialId')
    if matid in creative_status:
        ad_status = creative_status[matid]
    else:
        ad_status = 9
    if ad_status == 9:
        # did not find advid
        review = makeadvresponse(2, 1002, "Did not find material {}".format(matid))
    else:
        review = makeadvresponse(0, ad_status, matid)
    return json.dumps(review), 200


if __name__ == '__main__':
    app.run(debug=True)