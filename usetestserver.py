import requests
import argbase as arg

# define global variables
# options as globals
usagemsg = "This program uses the localhost test server and checks that it can process GET, POST and PUTs"
msg = arg.MSG()


def main():
    """main processing loop"""
    do = arg.MyArgs(usagemsg)
    do.processargs()
    msg.TEST("Running in test mode. Using Localhost")
    if arg.Flags.test:
        baseurl = "http://localhost:8081"
    else:
        baseurl = arg.Flags.configsettings['baseurl']
    msg.DEBUG(do)
    doget(baseurl)
    # dopost(baseurl)
    # doput(baseurl)


def doget(u: str):
    msg.VERBOSE("GET: {}".format(u))
    actionURL = u
    r = requests.get(actionURL)
    print("Response:\nJSON: {}\nStatus: {}\nContent: {}\nHeaders: {}".format(r.json,
                                                                            r.status_code,
                                                                            r.content,
                                                                            r.headers))


if __name__ == '__main__':
    main()
