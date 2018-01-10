import json

import requests

from modules import readbase as rb, argbase as arg

import time
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
    "status": 3,
    "reason": ""
}

baseheader = {'content-type': 'application/json', 'authorization': ''}

# options as globals
usagemsg = "This program uses the judge api for the advertiser or creative. It takes a single advertiser or material id."
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
    rt = rb.ReadJson('', '', arg.Flags.configsettings['tokenfile'])
    rt.readinput()
    now = time.time()
    if rt.data['generatetime'] == '':
        # no token
        msg.ERROR("Need to generate a new token (run gettoken.py)")
    then = int(rt.data['generatetime'])
    msg.VERBOSE("Token Life: {} seconds".format(now - then))
    tokenlife = now - then
    if tokenlife > 1800:
        msg.ERROR("Please generate a new token (run gettoken.py)")
    else:
        msg.VERBOSE("DPS token is still valid")
        baseheader['authorization'] = rt.data['token']
    objId = arg.Flags.id
    type = arg.Flags.type
    status_code, rj = judgeadvertiser(baseurl, objId, type)
    if status_code == 200:
        # we don't know what to expect so just print out whatever you got
        # we assume it is json
        print("Received JSON as follows:\n{}".format(rj))


def judgeadvertiser(u: str, a: str, t: str):
    action_u_r_l = u + "/v1/" + t + "/judge"
    msg.DEBUG("POST: {}".format(action_u_r_l))
    if t == 'advertiser':
        basejudge["advId"] = a
        action_u_r_l = action_u_r_l + "?advId=" + a + "&status=4"
    elif t == 'material':
        basejudge["materialId"] = a
        action_u_r_l = action_u_r_l + "?materialId=" + a + "&status=4"
    else:
        msg.ERROR("Bad Type: {} is not supported".format(t))
    msg.DEBUG("POST data: {}".format(basejudge))
    try:
        r = requests.post(action_u_r_l, json=basejudge, headers=baseheader)
        msg.DEBUG("{}\n\t{}".format(r.status_code, r.content.decode('utf-8')))
    except requests.exceptions.Timeout:
        # Maybe set up for a retry, or continue in a retry loop
        msg.ERROR("Connection timeout Error")
    except requests.exceptions.RequestException as e:
        msg.ERROR("Request Exception: {}\nDetails: {}".format(e, e.args))
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
