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
    advertiser = rb.ReadJson(arg.Flags.configsettings['root'], arg.Flags.configsettings['data'], arg.Flags.configsettings['advfile'])
    advertiser.readinput()
    creative = rb.ReadJson(arg.Flags.configsettings['root'], arg.Flags.configsettings['data'], arg.Flags.configsettings['adfile'])
    creative.readinput()
    msg.DEBUG("Adding Advertiser: {}".format(advertiser.data))
    c, aid = addadvertiser(baseurl, advertiser.data)
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
                msg.VERBOSE("Advertiser: Unknown status code or no response")
        else:
            msg.ERROR("Advertiser: {} {} {}".format(code, status, rj['msg']))
    else:
        msg.ERROR("Add of advertiser failed [{}]".format(aid))
    creative.data['advId'] = aid
    msg.DEBUG("Adding Creative: {}".format(creative.data))
    c, mid = addcreative(baseurl, creative.data)
    if c == 0:
        code, status, rj = querycreative(baseurl, mid)
        if code == 0:
            if status == 1:
                msg.VERBOSE("Review Pending for {}". format(mid))
            elif status == 3:
                msg.VERBOSE("Creative Rejected {}".format(mid, rj['result'][0]['rejectReason']))
            elif status == 4:
                msg.VERBOSE("Creative Approved! {}".format(mid))
            else:
                msg.VERBOSE("Creative: Unknown status code or no response")
        else:
            msg.ERROR("Creative: {} {} {}".format(code, status, rj['msg']))
    else:
        msg.ERROR("Add of creative failed [{}]".format(mid))

    # doput(baseurl)


def queryadvertiser(u: str, a):
    actionURL = u + "/v1/advertiser/query?advId=" + str(a)
    msg.VERBOSE("GET: {}".format(actionURL))
    r = requests.get(actionURL)
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
    actionURL = u + "/v1/advertiser/add"
    msg.VERBOSE("POST: {}".format(actionURL))
    add_data = baseadvertiser
    add_data['advertisers'].append(data)
    r = requests.post(actionURL, json=add_data, headers=baseheader)
    msg.DEBUG("{}\n\t{}\n\t{}".format(actionURL, r.status_code, r.content.decode('utf-8')))
    if r.status_code == 200:
        rj = json.loads(r.content.decode('utf-8'))
        if rj['code'] != 0:
            return rj['code'], rj['msg']
        else:
            return rj['code'], rj['result'][0]['advId']
    else:
        return None


def querycreative(u: str, a):
    actionURL = u + "/v1/creative/query?materialId=" + str(a)
    msg.VERBOSE("GET: {}".format(actionURL))
    r = requests.get(actionURL)
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
    actionURL = u + "/v1/creative/add"
    msg.VERBOSE("POST: {}".format(actionURL))
    add_data = basecreative
    add_data['materials'].append(data)
    r = requests.post(actionURL, json=add_data, headers=baseheader)
    msg.DEBUG("{}\n\t{}\n\t{}".format(actionURL, r.status_code, r.content.decode('utf-8')))
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
