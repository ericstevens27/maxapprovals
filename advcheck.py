import requests
import argbase as arg
import readbase as rb
import json

# define global variables

baseadvertiser = {
    "advertisers": [

    ]
}
basecreative = {
    "materials": [

    ]
}

baseheader = {'content-type': 'application/json'}

# options as globals
usagemsg = "This program checks on the status of the approval for the advertiser"
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
    aid = arg.Flags.id
    code, status, rj = queryadvertiser(baseurl, aid)
    if code == 0:
        if status == 1:
            msg.VERBOSE("Review Pending for {}".format(aid))
        elif status == 3:
            msg.VERBOSE("Advertiser Rejected {}".format(aid, rj['result'][0]['rejectReason']))
        elif status == 4:
            msg.VERBOSE("Advertiser Approved! {}".format(aid))
        else:
            msg.VERBOSE("Advertiser: Unknown status code or no response")
    else:
        msg.ERROR("Advertiser: {} {} {}".format(code, status, rj['msg']))


def queryadvertiser(u: str, a):
    action_u_r_l = u + "/v1/advertiser/query?advId=" + str(a)
    msg.VERBOSE("GET: {}".format(action_u_r_l))
    r = requests.get(action_u_r_l)
    msg.DEBUG("{}\n\t{}".format(r.status_code, r.content.decode('utf-8')))
    rj = json.loads(r.content.decode('utf-8'))
    if r.status_code == 200:
        if rj['code'] != 0:
            return rj['code'], rj['result'][0]['code'], rj
        else:
            return rj['code'], rj['result'][0]['status'], rj
    else:
        return None


def addadvertiser(u: str, data):
    action_u_r_l = u + "/v1/advertiser/add"
    msg.VERBOSE("POST: {}".format(action_u_r_l))
    add_data = baseadvertiser
    add_data['advertisers'].append(data)
    r = requests.post(action_u_r_l, json=add_data, headers=baseheader)
    msg.DEBUG("{}\n\t{}\n\t{}".format(action_u_r_l, r.status_code, r.content.decode('utf-8')))
    if r.status_code == 200:
        rj = json.loads(r.content.decode('utf-8'))
        if rj['code'] != 0:
            return rj['code'], rj['msg']
        else:
            return rj['code'], rj['result'][0]['advId']
    else:
        return None


def querycreative(u: str, a):
    action_u_r_l = u + "/v1/creative/query?materialId=" + str(a)
    msg.VERBOSE("GET: {}".format(action_u_r_l))
    r = requests.get(action_u_r_l)
    msg.DEBUG("{}\n\t{}".format(r.status_code, r.content.decode('utf-8')))
    rj = json.loads(r.content.decode('utf-8'))
    if r.status_code == 200:
        if rj['code'] != 0:
            return rj['code'], rj['result'][0]['code'], rj
        else:
            return rj['code'], rj['result'][0]['status'], rj
    else:
        return None


def addcreative(u: str, data):
    action_u_r_l = u + "/v1/creative/add"
    msg.VERBOSE("POST: {}".format(action_u_r_l))
    add_data = basecreative
    add_data['materials'].append(data)
    r = requests.post(action_u_r_l, json=add_data, headers=baseheader)
    msg.DEBUG("{}\n\t{}\n\t{}".format(action_u_r_l, r.status_code, r.content.decode('utf-8')))
    if r.status_code == 200:
        rj = json.loads(r.content.decode('utf-8'))
        if rj['code'] != 0:
            return rj['code'], rj['msg']
        else:
            return rj['code'], rj['result'][0]['materialId']
    else:
        return None


if __name__ == '__main__':
    main()
