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

baseheader = {'content-type': 'application/json', 'authorization': ''}

# options as globals
usagemsg = "This program checks on the status of the approval for the advertiser"
msg = arg.MSG()


def main():
    """main processing loop"""
    do = arg.MyArgs(usagemsg)
    do.processargs()
    msg.TEST("Running in test mode.")
    baseurl = arg.Flags.configsettings['serverurl']
    msg.DEBUG(do)
    tracking_init = rb.ReadJson(arg.Flags.configsettings['root'], arg.Flags.configsettings['data'],
                                arg.Flags.configsettings['tracking'])
    tracking_init.readinput()
    tracking_out = rb.WriteJson(arg.Flags.configsettings['root'], arg.Flags.configsettings['data'],
                                arg.Flags.configsettings['tracking'])
    baseheader['authorization'] = arg.Flags.configsettings['dsptoken']
    for el in tracking_init.data:
        if el['type'] == 'advertiser':
            status_code, rj = queryadvertiser(baseurl, el['id'])
            if status_code == 200:
                if rj['code'] == 0:
                    el['status'] = rj['result'][0]['status']
                    if el['status'] == 1:
                        print("Review Pending for {}".format(el['id']))
                    elif el['status'] == 3:
                        print("Advertiser Rejected {} with Reason: [{}]".format(el['id'],
                                                                                rj['result'][0]['rejectReason']))
                    elif el['status'] == 4:
                        print("Advertiser Approved! {}".format(el['id']))
                    else:
                        msg.VERBOSE("Advertiser: Unknown status code or no response")
                else:
                    checkresp = "Advertiser Check Failed for advId: {}: \n\tMessage: {}\n\tError Code: {}" \
                                "\n\tError Message: {}\n\tDescription: {}"
                    print(checkresp.format(el['id'], rj['msg'], rj['result'][0]['code'], rj['result'][0]['msg'],
                                           rj['result'][0]['desc']))
            else:
                msg.ERROR("HTTP Response {}".format(status_code))
    tracking_out.data = tracking_init.data
    tracking_out.writeoutput()


def queryadvertiser(u: str, a):
    action_u_r_l = u + "/v1/advertiser/query?advId=" + str(a)
    msg.DEBUG("GET: {}".format(action_u_r_l))
    r = requests.get(action_u_r_l)
    try:
        r = requests.get(action_u_r_l)
        msg.DEBUG("{}\n\t{}".format(r.status_code, r.content.decode('utf-8')))
    except requests.exceptions.Timeout:
        # Maybe set up for a retry, or continue in a retry loop
        msg.ERROR("Connection timeout Error")
    except requests.exceptions.RequestException as e:
        msg.ERROR(e)
    if arg.Flags.test:
        msg.TEST("full json is \n\t{}".format(json.loads(r.content.decode('utf-8'))))
        msg.TEST("\n\tstatus: {}\n\theaders: {}\n\turl: {}\n\treason: {}".format(r.status_code, r.headers,r.url, r.reason))

    return r.status_code, json.loads(r.content.decode('utf-8'))


if __name__ == '__main__':
    main()
