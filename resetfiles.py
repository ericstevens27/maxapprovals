from modules import readbase as rb, argbase as arg

# define global variables

# options as globals
usagemsg = "This program resets the json files used for advertiser and cretive submission testing"
msg = arg.MSG()


def main():
    """main processing loop"""
    do = arg.MyArgs(usagemsg)
    do.processargs()
    msg.DEBUG(do)
    advertiser = rb.WriteJson(arg.Flags.configsettings['root'], arg.Flags.configsettings['data'],
                             'adv_list_1.json')
    tracking = rb.WriteJson(arg.Flags.configsettings['root'], arg.Flags.configsettings['data'],
                             arg.Flags.configsettings['tracking'])
    creative = rb.WriteJson(arg.Flags.configsettings['root'], arg.Flags.configsettings['data'],
                             'creat_list_1.json')
    advertiser.data = []
    tracking.data = []
    creative.data = []
    advertiser.writeoutput()
    tracking.writeoutput()
    creative.writeoutput()

if __name__ == '__main__':
    main()
