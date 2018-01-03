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
trackingentry = {
    "type": "",
    "id": "",
    "status": 0,
    "raw": {}
}


baseheader = {'content-type': 'application/json'}

# options as globals
usagemsg = "This program reads the reative from the JSON and adds it to the server"
msg = arg.MSG()


def main():
    """main processing loop"""
    do = arg.MyArgs(usagemsg)
    do.processargs()
    msg.TEST("Running in test mode. Using Localhost")
    baseurl = arg.Flags.configsettings['baseurl']
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
    creative.data['advId'] = arg.Flags.id
    msg.DEBUG("Adding Creative: {}".format(creative.data))
    c, mid = addcreative(baseurl, creative.data)
    if c == 0:
        writetracking(mid, 0, creative.data, tracking_out)
        print("Creative added with materialId of {}".format(mid))
    else:
        msg.ERROR("Add of creative failed [{}]".format(mid))


def writetracking(a, s, d, t):
    newrec = trackingentry
    newrec['type'] = 'creative'
    newrec['id'] = a
    newrec['status'] = s
    newrec['raw'] = d
    t.data.append(newrec)
    t.writeoutput()


def addcreative(u: str, data):
    action_u_r_l = u + "/v1/creative/add"
    msg.DEBUG("POST: {}".format(action_u_r_l))
    add_data = basecreative
    add_data['materials'].append(data)
    try:
        r = requests.post(action_u_r_l, json=add_data, headers=baseheader)
        msg.DEBUG("{}\n\t{}\n\t{}".format(action_u_r_l, r.status_code, r.content.decode('utf-8')))
    except requests.exceptions.Timeout:
        # Maybe set up for a retry, or continue in a retry loop
        msg.ERROR("Connection timeout Error")
    except requests.exceptions.RequestException as e:
        msg.ERROR(e)
    if arg.Flags.test:
        msg.TEST("full json is \n\t{}".format(json.loads(r.content.decode('utf-8'))))
        msg.TEST("\n\tstatus: {}\n\theaders: {}\n\turl: {}\n\treason: {}".format(r.status_code, r.headers, r.url, r.reason))

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
