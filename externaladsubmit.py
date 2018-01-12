import json

import requests
import re
from modules import readbase as rb, argbase as arg

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
usagemsg = "This program inserts the creative identified by id into the SSEA server"
msg = arg.MSG()


def main():
    """main processing loop"""
    do = arg.MyArgs(usagemsg)
    do.processargs()
    if arg.Flags.test:
        msg.TEST("Running in test mode.")
    msg.DEBUG(do)
    if arg.Flags.test:
        # use creative file as listed in config
        creative = rb.ReadJson(arg.Flags.configsettings['root'], arg.Flags.configsettings['data'],
                           arg.Flags.configsettings['adfile'])
        creative.readinput()
    else:
        # read the creative from the tracking file
        track = rb.ReadJson(arg.Flags.configsettings['root'], arg.Flags.configsettings['data'],
                           arg.Flags.configsettings['tracking'])
        track.readinput()

    ad = SSEAApi(arg.Flags.configsettings['username'], arg.Flags.configsettings['password'],
                 arg.Flags.configsettings['easerverurl'])
    if ad.gettoken():
        if arg.Flags.test:
            msg.DEBUG("Adding Creative to SSEA: {}".format(creative.data))
            ad.makeappad(creative.data, 0)
        else:
            for c in track.data:
                if c['status'] == 4:
                    # creative approved - add this to SSEA, otherwise skip
                    cd = c['raw']
                    msg.DEBUG("Adding Creative to SSEA: {}".format(cd))
                    ad.makeappad(cd, c['id'])
        res = ad.callssea('logout', '', '')


def extractgroup(match):
    """extract the group (index: 1) from the match object"""
    if match is None:
        return None
    return match.group(1)


class SSEAApi:
    def __init__(self, user: str, password: str, sseapath: str):
        self.user = user
        self.password = password
        self.ssea = sseapath + '/api/v2/web/'
        self.xsrf_token = ''
        self.nameprefix = "Xiaomi_"
        self.tokenheader = {'content-type': 'application/json', 'X-XSRF-TOKEN': ''}
        self.data = {
                "adName": "creative_id",
                "content": {
                    "title": "Title",
                    "icon": "http://iconurl",
                    "actionurl": "http://aurl",
                    "summary": "my app",
                    "packagename": "package.name",
                    "appid": 123,
                    "landingurl": "http://aurl",
                    "adid": 232,
                    "imgurl": "http://animgurl"

                },
                "useTracking": False
            }
        self.api = {
            "gettoken": {
                "description": "Get session token",
                "api": "security/login",
                "verb": "post"
            },
            "getsession": {
                "description": "Get session Info",
                "api": "security/currentSessionInfo",
                "verb": "get"
            },
            "logout": {
                "description": "Logout",
                "api": "security/logout",
                "verb": "post"
            },
            "list": {
                "description": "List app ads",
                "api": "external-ads?offset=0&limit=10",
                "verb": "get"
            },
            "create": {
                "description": "Create app ad",
                "api": "external-ads",
                "verb": "post"
            },
            "update": {
                "description": "Update app ad",
                "api": "external-ads",
                "verb": "put"
            }
        }
        self.errcodes = {
            "200": {
                "gettoken": "Success",
                "getsession": "Success",
                "logout": "Success",
                "list": "Success",
                "create": "Success",
                "update": "Success"
            },
            "400": {
                "gettoken": "Bad request (Invalid JSON)",
                "getsession": "Unknown error",
                "logout": "Unknown error",
                "list": "Bad request (Invalid parameters)",
                "create": "Bad request (Invalid JSON or Duplicate ad name)",
                "update": "Bad request (Invalid JSON, invalid ad-key or Duplicate ad name)"
            },
            "401": {
                "gettoken": "Unauthorized request (Invalid username or password)",
                "getsession": "Unauthorized request (Invalid XSRF-TOKEN)",
                "logout": "Unauthorized request (Invalid XSRF-TOKEN)",
                "list": "Unauthorized request (Invalid XSRF-TOKEN)",
                "create": "Unauthorized request (Invalid XSRF-TOKEN)",
                "update": "Unauthorized request (Invalid XSRF-TOKEN)"
            },
            "other": {
                "gettoken": "Unknown error",
                "getsession": "Unknown error",
                "logout": "Unknown error",
                "list": "Unknown error",
                "create": "Unknown error",
                "update": "Unknown error"
            }
        }

    def gettoken(self) -> bool:
        """get the session token - required for all other calls"""
        action = "gettoken"
        actionurl = self.ssea + self.api[action]['api']
        authjson = {"username": self.user, "password": self.password}
        header = {'content-type': 'application/json'}
        msg.DEBUG("\n\tURL: {}\n\tjson: {}\n\tHeaders: {}".format(actionurl, authjson, header))
        r = requests.post(actionurl, json=authjson, headers=header)
        if self.checkstatus(r, action):
            self.xsrf_token = r.json()['xsrfToken']
            self.tokenheader['X-XSRF-TOKEN'] = self.xsrf_token
            msg.DEBUG("Got Token: {}".format(self.xsrf_token))
            return True
        else:
            return False

    def makeappad(self, ad, matid):
        """forms up the data fields needed to construct or update the ad"""
        # Name is the prefix 'Xiaomi_' plus to package name to be unique
        self.data['adName'] = ad['creativeId']
        self.data['useTracking'] = False
        self.data['content']['title'] = ad['title']
        self.data['content']['icon'] = ad['icon']
        self.data['content']['actionurl'] = ad['actionUrl']
        self.data['content']['summary'] = ad['summary']
        self.data['content']['packagename'] = ad['packageName']
        re_appid = r"download\/(\d*)"
        self.data['content']['appid'] = extractgroup(re.search(re_appid, ad['actionUrl']))
        self.data['content']['landingurl'] = ad['landingUrl']
        self.data['content']['adid'] = matid
        self.data['content']['imgurl'] = ad['imgUrl'][0]
        msg.DEBUG(json.dumps(self.data, indent=4))
        self.pushappad()

    def pushappad(self):
        """Checks for an ad with the same packname and if not then creates the ad"""
        msg.VERBOSE("Processing ad {}".format(self.data['adName']))
        adkey = self.getad(self.data['adName'])
        if adkey is not None:
            if arg.Flags.update:
                # Update this ad
                self.callssea('update', adkey, '')
            else:
                msg.VERBOSE(
                    "An ad for {} exists ({}). Update flag is false. Skipping creation".format(self.data['adName'],
                                                                                               adkey))
        else:
            self.callssea('create', '', '')

    def callssea(self, action, key, field):
        """general routine to call ssrm api using pre-defined actions and apis"""
        actionurl = self.ssea + self.api[action]['api']
        if action == 'update':
            actionurl = actionurl + "/" + key
        if action == 'list':
            actionurl = actionurl + "&filter={}&filterField={}".format(key, field)
        msg.DEBUG("\n\tURL: {}\n\tjson: {}\n\tHeaders: {}".format(actionurl, self.data, self.tokenheader))
        msg.DEBUG("{} {}".format(self.api[action]['description'], self.data['adName']))
        r = None
        if self.api[action]['verb'] == 'post':
            try:
                r = requests.post(actionurl, json=self.data, headers=self.tokenheader)
                msg.DEBUG("{}\n\t{}\n\t{}".format(actionurl, r.status_code, r.content.decode('utf-8')))
            except requests.exceptions.Timeout:
                # Maybe set up for a retry, or continue in a retry loop
                msg.ERROR("Connection timeout Error")
            except requests.exceptions.RequestException as e:
                msg.ERROR(e)
            if r.status_code == 200:
                if arg.Flags.test:
                    msg.TEST("full json is \n\t{}".format(json.loads(r.content.decode('utf-8'))))
                    msg.TEST(
                        "\n\tstatus: {}\n\theaders: {}\n\turl: {}\n\treason: {}".format(r.status_code, r.headers, r.url,
                                                                                        r.reason))
            else:
                msg.ERROR("HTTP Response {}\n{}".format(r.status_code, r.content.decode('utf-8')))

        elif self.api[action]['verb'] == 'get':
            try:
                r = requests.get(actionurl, headers=self.tokenheader)
                msg.DEBUG("{}\n\t{}\n\t{}".format(actionurl, r.status_code, r.content.decode('utf-8')))
            except requests.exceptions.Timeout:
                # Maybe set up for a retry, or continue in a retry loop
                msg.ERROR("Connection timeout Error")
            except requests.exceptions.RequestException as e:
                msg.ERROR(e)
            if r.status_code == 200:
                if arg.Flags.test:
                    msg.TEST("full json is \n\t{}".format(json.loads(r.content.decode('utf-8'))))
                    msg.TEST(
                        "\n\tstatus: {}\n\theaders: {}\n\turl: {}\n\treason: {}".format(r.status_code, r.headers, r.url,
                                                                                        r.reason))
            else:
                msg.ERROR("HTTP Response {}\n{}".format(r.status_code, r.content.decode('utf-8')))

        elif self.api[action]['verb'] == 'put':
            try:
                r = requests.put(actionurl, json=self.data, headers=self.tokenheader)
                msg.DEBUG("{}\n\t{}\n\t{}".format(actionurl, r.status_code, r.content.decode('utf-8')))
            except requests.exceptions.Timeout:
                # Maybe set up for a retry, or continue in a retry loop
                msg.ERROR("Connection timeout Error")
            except requests.exceptions.RequestException as e:
                msg.ERROR(e)
            if r.status_code == 200:
                if arg.Flags.test:
                    msg.TEST("full json is \n\t{}".format(json.loads(r.content.decode('utf-8'))))
                    msg.TEST(
                        "\n\tstatus: {}\n\theaders: {}\n\turl: {}\n\treason: {}".format(r.status_code, r.headers, r.url,
                                                                                        r.reason))
            else:
                msg.ERROR("HTTP Response {}\n{}".format(r.status_code, r.content.decode('utf-8')))

        else:
            msg.ERROR("Invalid verb in internal structure. Cannot process {} verb: {}".format(action,
                                                                                              self.api[action]['verb']))
        if self.checkstatus(r, action):
            return json.loads(r.content.decode('utf-8'))
        else:
            return None

    def checkstatus(self, r, action) -> bool:
        if str(r.status_code) in self.errcodes:
            if r.status_code == 200:
                msg.VERBOSE("{} {}".format(self.api[action]['description'],
                                           self.errcodes[str(r.status_code)][action]))
            else:
                msg.VERBOSE("{} {} [HTTP Response: {}]".format(self.api[action]['description'],
                                                               self.errcodes[str(r.status_code)][action],
                                                               r.status_code))
        else:
            msg.VERBOSE("{} {} [HTTP Response: {}]".format(self.api[action]['description'],
                                                           self.errcodes['other'][action],
                                                           r.status_code))
        if r.status_code == 200:
            return True
        else:
            return False

    def getad(self, name: str):
        """searches for an ad by the adName field which must be unique. Returns None if no record found"""
        actionurl = self.ssea + "external-ads?offset=0&limit=10&filter={}&filterField={}".format(name, 'adName')
        msg.DEBUG("Checking for ad\n\tURL: {}\n\tHeaders: {}".format(actionurl, self.tokenheader))
        r = requests.get(actionurl, headers=self.tokenheader)
        if r.status_code == 200:
            result = json.loads(r.content.decode('utf-8'))
            if result['count'] != 1:
                # if we get 0 then no record. If we get more than one then we cannot update
                return None
            else:
                # print(result)
                return result['items'][0]['key']
        else:
            return None



if __name__ == '__main__':
    main()
