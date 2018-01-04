import json

import requests

from modules import argbase as arg

# define global variables

baseadvertiser = {
    "advertisers": [

    ]
}
basecreative = {
    "materials": [

    ]
}
errorcodes = {
    1001: "Authentication error (dsp-token error)",
    1002: "Missing required parameter error",
    1003: "Illegal parameters",
    1004: "File format error",
    1005: "File size error",
    1006: "The file size is incorrect",
    1007: "File get error",
    2001: "Upload failed",
    2002: "Data does not exist",
    2003: "Database error"
}

trackingentry = {
    "type": "",
    "id": "",
    "status": 0,
    "raw": {}
}

basejudge = {
    "advId": "",
    "status": "",
    "reason": ""
}

baseheader = {'content-type': 'application/json', 'authorization': ''}

# options as globals
usagemsg = "This program uses the judge api for the advertiser. It takes a single advertiser id."
msg = arg.MSG()


def main():
    """main processing loop"""
    do = arg.MyArgs(usagemsg)
    do.processargs()
    if arg.Flags.test:
        msg.TEST("Running in test mode.")
        baseurl = arg.Flags.configsettings['testurl']
    else:
        baseurl = arg.Flags.configsettings['serverurl']
    msg.DEBUG(do)
    baseheader['authorization'] = arg.Flags.configsettings['dsptoken']
    advId = arg.Flags.id
    status_code, rj = judgeadvertiser(baseurl, advId)
    if status_code == 200:
        # we don't know what to expect so just print out whatever you got
        # we assume it is json
        print("Received JSON as follows:\n{}".format(rj))


def judgeadvertiser(u: str, a):
    action_u_r_l = u + "/v1/advertiser/judge"
    msg.DEBUG("POST: {}".format(action_u_r_l))
    basejudge["advId"] = a
    try:
        r = requests.post(action_u_r_l, json=basejudge, headers=baseheader)
        msg.DEBUG("{}\n\t{}".format(r.status_code, r.content.decode('utf-8')))
    except requests.exceptions.Timeout:
        # Maybe set up for a retry, or continue in a retry loop
        msg.ERROR("Connection timeout Error")
    except requests.exceptions.RequestException as e:
        msg.ERROR(e)
    if r.status_code == 200:
        if arg.Flags.test:
            msg.TEST("full json is \n\t{}".format(json.loads(r.content.decode('utf-8'))))
            msg.TEST("\n\tstatus: {}\n\theaders: {}\n\turl: {}\n\treason: {}".format(r.status_code, r.headers,r.url, r.reason))
        return r.status_code, json.loads(r.content.decode('utf-8'))
    else:
        msg.ERROR("HTTP Response {}\n{}".format(r.status_code, r.content.decode('utf-8')))
        return None



if __name__ == '__main__':
    main()
