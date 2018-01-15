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

baseheader = {'content-type': 'application/json', 'authorization': ''}

# options as globals
usagemsg = "This program reads the advertiser from the JSON and adds it to the server"
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
    advertiser = rb.ReadJson(arg.Flags.configsettings['root'], arg.Flags.configsettings['data'],
                             arg.Flags.configsettings['advfile'])
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
    advertiser.readinput()
    msg.DEBUG("Adding Advertiser: {}".format(advertiser.data))
    addadvertiser(baseurl, advertiser.data, tracking_out)


def writetracking(a, s, d, t):
    newrec = trackingentry
    newrec['type'] = 'advertiser'
    newrec['id'] = a
    newrec['status'] = s
    newrec['raw'] = d
    t.data.append(newrec)
    t.writeoutput()


def addadvertiser(u: str, data, track):
    action_u_r_l = u + "/v1/advertiser/add"
    msg.DEBUG("POST: {}".format(action_u_r_l))
    add_data = baseadvertiser
    add_data['advertisers'].append(data)
    try:
        r = requests.post(action_u_r_l, json=add_data, headers=baseheader)
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
            msg.ERROR("Add of advertiser failed with [{}]\n\t{}".format(errorcodes[rj['result'][0]['code']], rj))
        else:
            writetracking(rj['result'][0]['advId'], 0, data, track)
            print("Advertiser added with advID {}".format(rj['result'][0]['advId']))
    else:
        msg.ERROR("HTTP Response {}\n{}".format(r.status_code, r.content.decode('utf-8')))


if __name__ == '__main__':
    main()
