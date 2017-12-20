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
            status_code, rj = querycreative(baseurl, el['id'])
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
                        msg.VERBOSE("Creative: Unknown status code or no response")
                else:
                    checkresp = "Creative Check Failed for materialId: {}: \n\tMessage: {}\n\tError Code: {}"\
                                "\n\tError Message: {}\n\tDescription: {}"
                    print(checkresp.format(el['id'], rj['msg'], rj['result'][0]['code'], rj['result'][0]['msg'],
                                           rj['result'][0]['desc']))
            else:
                msg.ERROR("HTTP Response {}".format(status_code))
    tracking_out.data = tracking_init.data
    tracking_out.writeoutput()


def querycreative(u: str, a):
    action_u_r_l = u + "/v1/creative/query?materialId=" + str(a)
    msg.DEBUG("GET: {}".format(action_u_r_l))
    try:
        r = requests.get(action_u_r_l)
        msg.DEBUG("{}\n\t{}".format(r.status_code, r.content.decode('utf-8')))
    except requests.exceptions.Timeout:
        # Maybe set up for a retry, or continue in a retry loop
        msg.ERROR("Connection timeout Error")
    except requests.exceptions.RequestException as e:
        msg.ERROR(e)
    return r.status_code, json.loads(r.content.decode('utf-8'))


if __name__ == '__main__':
    main()
