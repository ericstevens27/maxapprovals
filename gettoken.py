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

baseheader = {'content-type': 'application/json'}

# options as globals
usagemsg = "This program gets the DPS token required for Xiaomi ADX authentication"
msg = arg.MSG()


def main():
    """main processing loop"""
    do = arg.MyArgs(usagemsg)
    do.processargs()
    if arg.Flags.test:
        msg.TEST("Running in test mode.")
        baseurl = arg.Flags.configsettings['testtokenurl']
    else:
        baseurl = arg.Flags.configsettings['tokenurl']
    msg.DEBUG(do)
    rt = rb.ReadJson('', '', arg.Flags.configsettings['tokenfile'])
    rt.readinput()
    now = time.time()
    if rt.data['generatetime'] == '':
        # no token
        msg.VERBOSE("Need to generate a token")
        rt.data['generatetime'] = 0
    then = int(rt.data['generatetime'])
    msg.VERBOSE("Duration: {} seconds".format(now - then))
    tokenlife = now - then
    if tokenlife > 1800 or arg.Flags.force:
        wt = rb.WriteJson('', '', arg.Flags.configsettings['tokenfile'])
        wt.data['token'] = gettoken(baseurl, arg.Flags.configsettings['clientId'], arg.Flags.configsettings['clientSecret'])
        wt.data['generatetime'] = now
        wt.writeoutput()
        print("New token generated [{}]".format(wt.data['token']))
    else:
        print("Token is still valid")



def gettoken(u: str, c:str, s: str):
    action_u_r_l = u + "get?clientId=" + str(c) + "&clientSecret=" + str(s)
    msg.DEBUG("GET: {}".format(action_u_r_l))
    try:
        r = requests.get(action_u_r_l, headers=baseheader)
        msg.DEBUG("{}\n\t{}".format(r.status_code, r.content.decode('utf-8')))
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
        rl = json.loads(r.content.decode('utf-8'))
        return rl['token']
    else:
        msg.ERROR("HTTP Response {}\n{}".format(r.status_code, r.content.decode('utf-8')))
        return None


if __name__ == '__main__':
    main()
