import json

import requests

from modules import readbase as rb, argbase as arg

import time

import re

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
    "creativeId": "",
    "xmAppId": 0,
    "raw": {}
}


baseheader = {'content-type': 'application/json', 'authorization': ''}

# options as globals
usagemsg = "This program reads the reative from the JSON and updates it on the server"\
            "Requires --id=[material id] of the creative id to update"
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
    creative = rb.ReadJson(arg.Flags.configsettings['root'], arg.Flags.configsettings['data'],
                           arg.Flags.configsettings['adfile'])
    creative.readinput()
    tracking_init = rb.ReadJson(arg.Flags.configsettings['root'], arg.Flags.configsettings['data'],
                             arg.Flags.configsettings['tracking'])
    tracking_init.readinput()
    tracking_out = rb.WriteJson(arg.Flags.configsettings['root'], arg.Flags.configsettings['data'],
                             arg.Flags.configsettings['tracking'])
    tracking_out.data = tracking_init.data
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
    if not arg.Flags.id:
        msg.ERROR("Missing --id option. id must be the creativeID to update")
    msg.DEBUG("Updating Creative: id: {} with data: {}".format(arg.Flags.id, creative.data))
    foundad = False
    c = 1
    mid = None
    for item in tracking_init.data:
        msg.DEBUG("Found this item in tracking {}".format(item))
        if item['type'] == 'creative':
            if item['creativeId'] == arg.Flags.id:
                msg.DEBUG("Found the creative id")
                creative.data['materialId'] = item['id']
                creative.data['advId'] = item['advId']
                msg.VERBOSE("About to update with this data \n{}".format(creative.data))
                c, mid = updatecreative(baseurl, creative.data)
                foundad = True
    if not foundad:
        msg.ERROR("Could not find creative in tracking file to get material Id")
    if c == 0:
        # writetracking(mid, 0, creative.data, tracking_out)
        print("Creative updated with materialId of {}".format(mid))
    else:
        if mid == None:
            msg.ERROR("Update of creative failed - No tracking data")
        else:
            msg.ERROR("Update of creative failed with [{}]\n\t{}".format(errorcodes[mid['result'][0]['code']], mid))


def extractgroup(match):
    """extract the group (index: 1) from the match object"""
    if match is None:
        return None
    return match.group(1)


def writetracking(a, s, d, t, aid):
    newrec = trackingentry
    newrec['type'] = 'creative'
    newrec['id'] = a
    newrec['status'] = s
    newrec['raw'] = d
    newrec['creativeId'] = d['creativeId']
    re_appid = r"download\/(\d*)"
    newrec['xmAppId'] = extractgroup(re.search(re_appid, d['actionUrl']))
    t.data.append(newrec)
    t.writeoutput()


def updatecreative(u: str, data):
    action_u_r_l = u + "/v1/creative/update"
    msg.DEBUG("POST: {}".format(action_u_r_l))
    update_data = basecreative
    update_data['materials'].append(data)
    try:
        r = requests.post(action_u_r_l, json=update_data, headers=baseheader)
        msg.DEBUG("{}\n\t{}\n\t{}".format(action_u_r_l, r.status_code, r.content.decode('utf-8')))
    except requests.exceptions.Timeout:
        # Maybe set up for a retry, or continue in a retry loop
        msg.ERROR("Connection timeout Error")
    except requests.exceptions.RequestException as e:
        msg.ERROR("Request Exception: {}\nDetails: {}".format(e, e.args))
    if r.status_code == 200:
        if arg.Flags.test:
            msg.TEST("full json is \n\t{}".format(json.loads(r.content.decode('utf-8'))))
            msg.TEST("\n\tstatus: {}\n\theaders: {}\n\turl: {}\n\treason: {}".format(r.status_code, r.headers, r.url,
                                                                                     r.reason))
        rj = json.loads(r.content.decode('utf-8'))
        if rj['code'] != 0:
            return rj['code'], rj
        else:
            return rj['code'], rj['result'][0]['materialId']
    else:
        msg.ERROR("HTTP Response {}\n{}".format(r.status_code, r.content.decode('utf-8')))
        return None


if __name__ == '__main__':
    main()
