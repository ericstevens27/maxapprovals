#!flask/bin/python
import json
import random

from flask import Flask
from flask import request

from modules import readbase as rb

app = Flask(__name__)

advertiser = rb.ReadJson('', 'data', 'adv_list_1.json')
creative = rb.ReadJson('', 'data', 'creat_list_1.json')

force_error = False


def randomerror():
    errcode = {
        1001: ["Authentication error (dsp-token error)", ""],
        1002: ["Missing required parameter error", "This will tell you which field is bad"],
        1003: ["Illegal parameters", "This will tell you which field is illegal"],
        1004: ["File format error", "This will tell you which file was bad"],
        1005: ["File size error", "This will tell you which file had a problem"],
        1006: ["The file size is incorrect", "This will tell you which file had a problem"],
        1007: ["File get error", "This will tell you which file had a problem"],
        2001: ["Upload failed", "This will tell you which upload had a problem"],
        2002: ["Data does not exist", "This will tell you which data is missing"],
        2003: ["Database error", "This will tell you the database error"],
    }
    i = random.randrange(2) + 1
    if i == 1:
        d = random.randrange(7) + 1
    elif i == 2:
        d = random.randrange(3) + 1
    else:
        i = 1
        d = random.randrange(7) + 1
    errkey = (i * 1000) + d
    # print(i, d, errkey)
    return(errkey, errcode[errkey][0], errcode[errkey][1])


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
        # errorresponse['code'] = c1
        # errorresponse['msg'] = s
        # errorresponse['result'][0]['code'] = c2
        # errorresponse['result'][0]['msg'] = s
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
        # errorresponse['code'] = c1
        # errorresponse['msg'] = s
        # errorresponse['result'][0]['code'] = c2
        # errorresponse['result'][0]['msg'] = s
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
    w_obj = rb.WriteJson('', 'data', f)
    w_obj.data = d
    w_obj.writeoutput()


@app.route('/')
def index():
    return "Hello, World!"


@app.route('/v1/advertiser/query', methods=['GET'])
def get_adv():
    advid = request.args.get('advId')
    advertiser_status = 9
    rr = ''
    for ad in advertiser.data:
        if str(ad['advId']) == advid:
            advertiser_status = ad['status']
            if 'reason' in ad:
                rr = ad['reason']
    if advertiser_status == 9 or force_error:
        # did not find advid
        review = makeadvresponse(2, '', '', '')
        review['code'] = 2
        review['msg'] = "All Failed"
        code, msg, desc = randomerror()
        review['result'][0]['code'] = code
        review['result'][0]['msg'] = msg
        review['result'][0]['desc'] = desc
    else:
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
    rr = ''
    for ad in creative.data:
        if str(ad['materialId']) == matid:
            createid = ad['creativeId']
            ad_status = ad['status']
            if 'reason' in ad:
                rr = ad['reason']
    if ad_status == 9 or force_error:
        # did not find materialid
        # code is 2 == All failed (since only one sent)
        review = makecreativeresponse(2, '', '', '', '')
        review['code'] = 2
        review['msg'] = "All Failed"
        code, msg, desc = randomerror()
        review['result'][0]['code'] = code
        review['result'][0]['msg'] = msg
        review['result'][0]['desc'] = desc
    else:
        review = makecreativeresponse(0, ad_status, createid, matid, rr)
    return json.dumps(review), 200


if __name__ == '__main__':
    loaddata()
    app.run(debug=True)