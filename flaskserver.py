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
creative_Status = {}


def makeresponse(c1, c2, s):
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
        review = makeresponse(2, 1002, "Did not find advertiser {}".format(advid))
    else:
        review = makeresponse(0, advertiser_status, advid)
    return json.dumps(review), 200


@app.route('/v1/advertiser/add', methods=['POST'])
def add_advertiser():
    if not request.json or not 'advertisers' in request.json:
        bad = makeresponse(2, 1002, "No json or missing advertiser block")
        return json.dumps(bad), 400
    advtodadd = request.json['advertisers'][0]
    newid = len(adv_list) + 10000 + 1
    advtodadd['advId'] = newid
    newidstr = str(newid)

    adv_list.append(advtodadd)
    adv_status[newidstr] = 1

    resp = makeresponse(0, 0, newidstr)
    return json.dumps(resp), 200


@app.route('/v1/creative/add', methods=['POST'])
def add_creative():
    bad = {
      "code": 1,
      "msg": "上传部分成功",
      "result": [
        {
          "creativeId": "",
          "code": 1006,
          "msg": "文件尺寸错误",
          "desc": "imgUrl对应的图片宽高比不符合模板建议"
        }
      ],
      "auditId": "0d0b70ecbdd53641"
    }
    good = {
      "code": 1,
      "msg": "上传部分成功",
      "result": [
        {
          "creativeId": "",
          "code": 0,
          "materialId": "fedcba0987654321"
        }
      ],
      "auditId": "0d0b70ecbdd53641"
    }

    if not request.json or not 'materials' in request.json:
        return json.dumps(bad), 400
    if add_flag:
        resp = good
    else:
        resp = bad
    postdata = json.loads(request.json)
    resp['result'][0]['creativeId'] = postdata['materials'][0]['creativeId']
    return json.dumps(resp), 200


@app.route('/v1/creative/query', methods=['GET'])
def get_creative():
    matid = request.args.get('materialId')
    pending = {
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
    approved = {
          "code": 0,
          "result": [
            {
              "materialId": "",
              "creativeId": "",
              "status": 4,
              "classification": "L3"
            }
            ]
        }
    reject = {
          "code": 0,
          "result": [
            {
              "materialId": "",
              "creativeId": "",
              "status": 3,
              "rejectReason": "Very bad ad"
            }
            ]
        }
    bad = {
          "code": 2,
          "msg": "Bad request",
          "result": [
            {
              "code": 1002,
              "msg": "Missing required parameter error",
              "desc": "Missing required parameter error"
            }
            ]
        }
    review = bad
    if status_flag == 'accept':
        review = approved
    elif status_flag == 'pending':
        review = pending
    elif status_flag == 'reject':
        review = reject
    if review['code'] != 2:
        review['result'][0]['materialId'] = matid

    return json.dumps(review), 200



if __name__ == '__main__':
    app.run(debug=True)