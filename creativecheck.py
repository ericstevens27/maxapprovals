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
usagemsg = "This program checks on the status of the approval for the creative"
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
    tracking_init = rb.ReadJson(arg.Flags.configsettings['root'], arg.Flags.configsettings['data'],
                             arg.Flags.configsettings['tracking'])
    tracking_init.readinput()
    tracking_out = rb.WriteJson(arg.Flags.configsettings['root'], arg.Flags.configsettings['data'],
                             arg.Flags.configsettings['tracking'])
    for el in tracking_init.data:
        if el['type'] == 'creative':
            code, status, rj = querycreative(baseurl, el['id'])
            if code == 0:
                el['status'] = status
                if status == 1:
                    print("Review Pending for {}".format(el['id']))
                elif status == 3:
                    print("Creative Rejected {}".format(el['id'], rj['result'][0]['rejectReason']))
                elif status == 4:
                    print("Creative Approved! {}".format(el['id']))
                else:
                    msg.VERBOSE("Creative: Unknown status code or no response")
            else:
                msg.ERROR("Creative: {} {} {}".format(code, status, rj['msg']))
    tracking_out.data = tracking_init.data
    tracking_out.writeoutput()


def queryadvertiser(u: str, a):
    action_u_r_l = u + "/v1/advertiser/query?advId=" + str(a)
    msg.DEBUG("GET: {}".format(action_u_r_l))
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
    msg.DEBUG("POST: {}".format(action_u_r_l))
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
    msg.DEBUG("GET: {}".format(action_u_r_l))
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
    msg.DEBUG("POST: {}".format(action_u_r_l))
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
