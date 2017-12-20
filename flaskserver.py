#!flask/bin/python
from flask import Flask
from flask import request
import json
import readbase as rb

app = Flask(__name__)

advertiser = rb.ReadJson('', '', 'adv_list_1.json')
creative = rb.ReadJson('', '', 'creat_list_1.json')


def makeadvresponse(c1, c2, s, r):
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
        if c2 == 3:
            good['result'][0]['rejectReason'] = r
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

def makecreativeresponse(c1, c2, cid, s, r):
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
        if c2 == 3:
            good['result'][0]['rejectReason'] = r
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

def loaddata():
    advertiser.readinput()
    creative.readinput()


def savedata(type):
    if type == 'advertiser':
        f = 'adv_list_1.json'
        d = advertiser.data
    elif type == 'creative':
        f = 'creat_list_1.json'
        d = creative.data
    else:
        print("[ERROR] Bad save data type")
    w_obj = rb.WriteJson('', '', f)
    w_obj.data = d
    w_obj.writeoutput()


@app.route('/')
def index():
    return "Hello, World!"


@app.route('/v1/advertiser/query', methods=['GET'])
def get_adv():
    advid = request.args.get('advId')
    advertiser_status = 9
    for ad in advertiser.data:
        if str(ad['advId']) == advid:
            advertiser_status = ad['status']
    if advertiser_status == 9:
        # did not find advid
        review = makeadvresponse(2, 1002, "Did not find advertiser {}".format(advid), '')
    else:
        if advertiser_status == 3:
            rr = "Not good company"
        else:
            rr = ''
        review = makeadvresponse(0, advertiser_status, advid, rr)
    return json.dumps(review), 200


@app.route('/v1/advertiser/add', methods=['POST'])
def add_advertiser():
    if not request.json or not 'advertisers' in request.json:
        bad = makeadvresponse(2, 1002, "No json or missing advertiser block")
        return json.dumps(bad), 400
    advtoadd = request.json['advertisers'][0]
    newid = len(advertiser.data) + 10000 + 1
    advtoadd['advId'] = newid
    advtoadd['status'] = 1
    newidstr = str(newid)

    advertiser.data.append(advtoadd)
    savedata('advertiser')
    resp = makeadvresponse(0, 0, newidstr, '')
    return json.dumps(resp), 200


@app.route('/v1/creative/add', methods=['POST'])
def add_creative():
    if not request.json or not 'materials' in request.json:
        bad = makeadvresponse(2, 1002, "No json or missing materials block", 'Bad JSON')
        return json.dumps(bad), 400
    adtoadd = request.json['materials'][0]
    newid = len(creative.data) + 50000 + 1
    adtoadd['materialId'] = newid
    adtoadd['status'] = 1
    newidstr = str(newid)

    creative.data.append(adtoadd)
    savedata('creative')
    resp = makecreativeresponse(0, 0, adtoadd['creativeId'], newidstr, '')
    return json.dumps(resp), 200


@app.route('/v1/creative/query', methods=['GET'])
def get_creative():
    matid = request.args.get('materialId')
    createid = ''
    ad_status = 9
    for ad in creative.data:
        if str(ad['materialId']) == matid:
            createid = ad['creativeId']
            ad_status = ad['status']
    if ad_status == 9:
        # did not find materialid
        review = makecreativeresponse(2, 1002, '', "Did not find material {}".format(matid), '')
    else:
        if ad_status == 3:
            rr = "Very bad ad"
        else:
            rr = ''
        review = makecreativeresponse(0, ad_status, createid, matid, rr)
    return json.dumps(review), 200


if __name__ == '__main__':
    loaddata()
    app.run(debug=True)