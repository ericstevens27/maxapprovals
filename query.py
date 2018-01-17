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
usagemsg = "This program checks on the status of the approval for the advertiser"\
            "Use --type=[advertiser|creative] to select which type of object to query."
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
    tracking_init = rb.ReadJson(arg.Flags.configsettings['root'], arg.Flags.configsettings['data'],
                                arg.Flags.configsettings['tracking'])
    tracking_init.readinput()
    tracking_out = rb.WriteJson(arg.Flags.configsettings['root'], arg.Flags.configsettings['data'],
                                arg.Flags.configsettings['tracking'])
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
    if arg.Flags.type:
        if arg.Flags.type == 'advertiser' or arg.Flags.type == 'creative':
            type = arg.Flags.type
        else:
            msg.ERROR("Invalid type: {} is not a valid API call".format(arg.Flags.type))
    else:
        type = None
    for el in tracking_init.data:
        if type == None:
            status_code, rj = queryelement(baseurl, el['id'], el['type'])
            if status_code == 200:
                if rj['code'] == 0:
                    if rj['result'] == []:
                        msg.ERROR("Result returned is empty")
                    else:
                        el['status'] = rj['result'][0]['status']
                        if el['status'] == 1:
                            print("Review Pending for {}".format(el['id']))
                            msg.VERBOSE(el)

                        elif el['status'] == 3:
                            print("{} Rejected {} with Reason: [{}]".format(el['type'].title(),
                                                                            el['id'],
                                                                            rj['result'][0]['rejectReason']))
                            msg.VERBOSE(el)

                        elif el['status'] == 4:
                            print("{} Approved! {}".format(el['type'].title(), el['id']))
                            msg.VERBOSE(el)

                        else:
                            msg.ERROR("{}: Unknown status code or no response".format(el['type'].title()))
                else:
                    checkresp = "{} Check Failed for advId: {}: \n\tMessage: {}\n\tError Code: {} [{}]" \
                                "\n\tError Message: {}\n\tDescription: {}"
                    print(checkresp.format(el['type'].title(),
                                           el['id'], rj['msg'], rj['code'],
                                           errorcodes[rj['code']], rj['msg'],
                                           rj['desc']))
        else:
            if el['type'] == type:
                status_code, rj = queryelement(baseurl, el['id'], type)
                if status_code == 200:
                    if rj['code'] == 0:
                        if rj['result'] == []:
                            msg.ERROR("Result returned is empty")
                        else:

                            el['status'] = rj['result'][0]['status']
                            if el['status'] == 1:
                                print("Review Pending for {}".format(el['id']))
                                msg.VERBOSE(el)
                            elif el['status'] == 3:
                                print("{} Rejected {} with Reason: [{}]".format(type.title(),
                                                                                el['id'],
                                                                                rj['result'][0]['rejectReason']))
                                msg.VERBOSE(el)

                            elif el['status'] == 4:
                                print("{} Approved! {}".format(type.title(), el['id']))
                                msg.VERBOSE(el)

                            else:
                                msg.ERROR("{}: Unknown status code or no response".format(type.upper))
                    else:
                        checkresp = "{} Check Failed for advId: {}: \n\tMessage: {}\n\tError Code: {} [{}]" \
                                    "\n\tDescription: {}"
                        print(checkresp.format(type.title(),
                                               el['id'], rj['msg'], rj['code'],
                                               errorcodes[rj['code']],
                                               rj['desc']))

    tracking_out.data = tracking_init.data
    tracking_out.writeoutput()


def queryelement(u: str, a:str, t: str):
    if t == 'advertiser':
        action_u_r_l = u + "/v1/advertiser/query?advId=" + str(a)
    else:
        action_u_r_l = u + "/v1/creative/query?materialId=" + str(a)
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
        return r.status_code, json.loads(r.content.decode('utf-8'))
    else:
        msg.ERROR("HTTP Response {}\n{}".format(r.status_code, r.content.decode('utf-8')))
        return None


if __name__ == '__main__':
    main()
