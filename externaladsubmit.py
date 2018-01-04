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
    creative = rb.ReadJson(arg.Flags.configsettings['root'], arg.Flags.configsettings['data'],
                           arg.Flags.configsettings['adfile'])
    creative.readinput()
    ad = SSEAApi(arg.Flags.configsettings['username'], arg.Flags.configsettings['password'],
                 arg.Flags.configsettings['easerverurl'])
    msg.DEBUG("Adding Creative to SSEA: {}".format(creative.data))
    if ad.gettoken():
        res = ad.callssea('list', 'Xiaomi', 'adName')
        print("I found {} ads in the SSEA".format(res['count']))
        res = ad.callssea('getsession', '', '')
        print("You are logged in as {}".format(res['username']))

        # for pgkname in rd.data:
        #     ad.makeappad(pgkname, rd.data[pgkname])
        res = ad.callssea('logout', '', '')


class SSEAApi:
    def __init__(self, user: str, password: str, sseapath: str):
        self.user = user
        self.password = password
        self.ssea = sseapath + '/api/v2/web/'
        self.xsrf_token = ''
        self.nameprefix = "Xiaomi_"
        self.tokenheader = {'content-type': 'application/json', 'X-XSRF-TOKEN': ''}
        self.data = {
            "adName": "Xiaomi_example.app.ad",
            "content": [
                {
                    "title": "Xiaomi Example App Ad",
                    "category": "Demo and Testing",
                    "description": "An app ad example for documentation",
                    "appStoreUris": [
                        {
                            "code": "thirdParty",
                            "uri": "http://example.com/third-party-us"
                        }
                    ],
                    "buttonText": "Install",
                    "visitedButtonText": "Added",
                    "images": [
                        {
                            "typeName": "BANNER",
                            "imageUri": "/dynamicAssets/f29e3843-f4c0-4fbd-80cd-d31d4c091ccc-Wechat-in-the-world.jpg",
                            "colspan": 1,
                            "rowspan": 1
                        },
                        {
                            "typeName": "SMALL_BANNER",
                            "imageUri": "/dynamicAssets/663d14a8-3fc7-4907-912d-6e6af1e75d7b-Wechat-in-the-world.jpg",
                            "colspan": 1,
                            "rowspan": 1
                        },
                        {
                            "typeName": "ICON",
                            "imageUri": "/dynamicAssets/c6655851-bdd7-473f-a78d-f2dc8a611d09-bunny.jpg",
                            "colspan": 1,
                            "rowspan": 1
                        }
                    ],
                    "language": "en_US"
                },
                {
                    "title": "演示测试",
                    "category": "演示测试",
                    "description": "演示测试",
                    "appStoreUris": [
                        {
                            "code": "thirdParty",
                            "uri": "http://example.com/third-party-cn"
                        }
                    ],
                    "buttonText": "安装",
                    "visitedButtonText": "添加",
                    "images": [
                        {
                            "typeName": "BANNER",
                            "imageUri": "/dynamicAssets/f29e3843-f4c0-4fbd-80cd-d31d4c091ccc-Wechat-in-the-world.jpg",
                            "colspan": 1,
                            "rowspan": 1
                        },
                        {
                            "typeName": "SMALL_BANNER",
                            "imageUri": "/dynamicAssets/663d14a8-3fc7-4907-912d-6e6af1e75d7b-Wechat-in-the-world.jpg",
                            "colspan": 1,
                            "rowspan": 1
                        },
                        {
                            "typeName": "ICON",
                            "imageUri": "/dynamicAssets/42efa74e-d401-4ce9-9040-61e1a9ff069c-bunny.jpg",
                            "colspan": 1,
                            "rowspan": 1
                        }
                    ],
                    "language": "zh_CN"
                }
            ],
            "category": "Documentation",
            "advertiser": "Graphite software",
            "packageName": "com.securespaces.package.name"
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
            return True
        else:
            return False

    def makeappad(self, pname, pdet):
        """forms up the data fields needed to construct or update the ad"""
        # Name is the prefix 'Xiaomi_' plus to package name to be unique
        self.data['adName'] = self.nameprefix + pname
        self.data['category'] = pdet['category_en']
        self.data['advertiser'] = pdet['company']
        self.data['packageName'] = pname
        self.data['content'][0]['title'] = pname[:30]  # title is limited to 30 characters
        self.data['content'][0]['category'] = pdet['category_en']
        self.data['content'][0]['description'] = pname
        self.data['content'][0]['appStoreUris'][0]['uri'] = pdet['directurl']
        self.data['content'][0]['images'][2]['imageUri'] = pdet['iconurl']
        self.data['content'][1]['title'] = pdet['description'][:30]  # title is limited to 30 characters
        self.data['content'][1]['category'] = pdet['category_zh']
        self.data['content'][1]['description'] = pdet['description']
        self.data['content'][1]['appStoreUris'][0]['uri'] = pdet['directurl']
        self.data['content'][1]['images'][2]['imageUri'] = pdet['iconurl']
        # print(json.dumps(self.data, indent=4))
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
        actionurl = self.ssea + "app-ads?offset=0&limit=10&filter={}&filterField={}".format(name, 'adName')
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
