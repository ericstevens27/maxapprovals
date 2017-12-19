import requests
import argbase as arg
import json

# define global variables
api = {
    "addadvertiser": {
        "description": "Add Advertiser Information",
        "api": "",
        # "api": "v1/advertiser/add",
        "verb": "post"
    },
    "getsession": {
        "description": "Get session Info",
        "api": "security/currentSessionInfo",
        "verb": "get"
    },
    "logout": {
        "description": "Logout",
        "api": "security/logout",
        "verb": "post"
    },
    "list": {
        "description": "List app ads",
        "api": "app-ads?offset=0&limit=10",
        "verb": "get"
    },
    "create": {
        "description": "Create app ad",
        "api": "app-ads",
        "verb": "post"
    },
    "update": {
        "description": "Update app ad",
        "api": "app-ads",
        "verb": "put"
    }
}
sampleadvertiser = {
  "advertisers": [
    {
      "companyName": "name==",
      "businessLicenseNum": "123321",
      "businessLicensePic": "http://c1.mifile.cn/f/i/15/item/buyphone/MIX-heise!600x600.jpg",
      "websiteName": "wangzhan",
      "icpPic": "http://c1.mifile.cn/f/i/15/item/buyphone/MIX-heise!600x600.jpg ",
      "websiteAddress": "www.mi.com",
      "industry": "2664",
      "qualifications": [
        {
          "key": "信息网络传播视听节目许可证",
          "url": "http://f2.market.xiaomi.com/download/AdCenter/078f5047a225142c82393a3d7f923d02534330cf4/AdCenter078f5047a225142c82393a3d7f923d02534330cf4.png"
        },
        {
          "key": "广电总局备案证明",
          "url": "http://f2.market.xiaomi.com/download/AdCenter/078f5047a225142c82393a3d7f923d02534330cf4/AdCenter078f5047a225142c82393a3d7f923d02534330cf4.png"
        }
      ]
    }
  ]
}
errcodes = {
    "200": {
        "addadvertiser": "Success",
        "getsession": "Success",
        "logout": "Success",
        "list": "Success",
        "create": "Success",
        "update": "Success"
    },
    "400": {
        "addadvertiser": "Bad request (Invalid JSON)",
        "getsession": "Unknown error",
        "logout": "Unknown error",
        "list": "Bad request (Invalid parameters)",
        "create": "Bad request (Invalid JSON or Duplicate ad name)",
        "update": "Bad request (Invalid JSON, invalid ad-key or Duplicate ad name)"
    },
    "401": {
        "addadvertiser": "Unauthorized request (Invalid username or password)",
        "getsession": "Unauthorized request (Invalid XSRF-TOKEN)",
        "logout": "Unauthorized request (Invalid XSRF-TOKEN)",
        "list": "Unauthorized request (Invalid XSRF-TOKEN)",
        "create": "Unauthorized request (Invalid XSRF-TOKEN)",
        "update": "Unauthorized request (Invalid XSRF-TOKEN)"
    },
    "other": {
        "addadvertiser": "Unknown error",
        "getsession": "Unknown error",
        "logout": "Unknown error",
        "list": "Unknown error",
        "create": "Unknown error",
        "update": "Unknown error"
    }
}
sampleheader = {'content-type': 'application/json'}

# options as globals
usagemsg = "This program uses the localhost test server and checks that it can process GET, POST and PUTs"
msg = arg.MSG()


def main():
    """main processing loop"""
    do = arg.MyArgs(usagemsg)
    do.processargs()
    msg.TEST("Running in test mode. Using Localhost")
    if arg.Flags.test:
        baseurl = "http://localhost:5000"
    else:
        baseurl = arg.Flags.configsettings['baseurl']
    msg.DEBUG(do)
    c, aid = addadvertiser(baseurl)
    if c == 0:
        code, status, rj = queryadvertiser(baseurl, aid)
        if code == 0:
            if status == 1:
                msg.VERBOSE("Review Pending for {}". format(aid))
            elif status == 3:
                msg.VERBOSE("Advertiser Rejected {}".format(aid, rj['result'][0]['rejectReason']))
            elif status == 4:
                msg.VERBOSE("Advertiser Approved! {}".format(aid))
            else:
                msg.VERBOSE("Unknown status code or no response")
        else:
            msg.ERROR("{} {} {}".format(code, status, rj['msg']))
    else:
        msg.ERROR("Add of advertiser failed [{}]".format(aid))

    # doput(baseurl)


def queryadvertiser(u: str, a):
    actionURL = u + "/v1/advertiser/query?advId=" + str(a)
    msg.VERBOSE("GET: {}".format(actionURL))
    r = requests.get(actionURL)
    msg.DEBUG("{}\n{}".format(r.status_code, r.content.decode('utf-8')))
    rj = json.loads(r.content.decode('utf-8'))
    if r.status_code == 200:
        if rj['code'] != 0:
            return rj['code'], rj['result'][0]['code'], rj
        else:
            return rj['code'], rj['result'][0]['status'], rj
    else:
        return None



def addadvertiser(u: str):
    actionURL = u + "/v1/advertiser/add"
    msg.VERBOSE("POST: {}".format(actionURL))
    r = requests.post(actionURL, json=sampleadvertiser, headers=sampleheader)
    msg.DEBUG("{}\n{}\n{}".format(actionURL, r.status_code, r.content.decode('utf-8')))
    if r.status_code == 200:
        rj = json.loads(r.content.decode('utf-8'))
        if rj['code'] != 0:
            return rj['code'], rj['msg']
        else:
            return rj['code'], rj['result'][0]['advId']
    else:
        return None


def callserver(u, action):
    """general routine to call ssrm api using pre-defined actions and apis"""
    actionurl = u + api[action]['api']
    msg.DEBUG("\n\tURL: {}\n\tjson: {}\n\tHeaders: {}".format(actionurl, sampleadvertiser, sampleheader))
    msg.DEBUG("{}".format(api[action]['description']))
    r = None
    if api[action]['verb'] == 'post':
        r = requests.post(actionurl, json=sampleadvertiser, headers=sampleheader)
    elif api[action]['verb'] == 'get':
        r = requests.get(actionurl, headers=sampleheader)
    elif api[action]['verb'] == 'put':
        r = requests.put(actionurl, json=sampleadvertiser, headers=sampleheader)
    else:
        msg.ERROR("Invalid verb in internal structure. Cannot process {} verb: {}".format(action,
                                                                                          api[action]['verb']))
    if checkstatus(r, action):
        return json.loads(r.content.decode('utf-8'))
    else:
        return None

def checkstatus(r, action) -> bool:
    if str(r.status_code) in errcodes:
        if r.status_code == 200:
            msg.VERBOSE("{} {}".format(api[action]['description'],
                                       errcodes[str(r.status_code)][action]))
        else:
            msg.VERBOSE("{} {} [HTTP Response: {}]".format(api[action]['description'],
                                                           errcodes[str(r.status_code)][action],
                                                           r.status_code))
    else:
        msg.VERBOSE("{} {} [HTTP Response: {}]".format(api[action]['description'],
                                                       errcodes['other'][action],
                                                       r.status_code))
    if r.status_code == 200:
        return True
    else:
        return False



if __name__ == '__main__':
    main()
