class NetcheckCommon:
    def __init__(self):
        pass

def append2list(listname, *argv):
    for arg in argv:
        listname.append(arg)
    return listname

import re
def intf_range_expand(interface_listofdict):
    expanded_interface_listofdict = []
    for i in interface_listofdict:
        for ki,vi in i.items():
            intfs = vi.get('interfaces')
            if intfs:
                expanded_intf = []
                for intf in intfs:
                    if re.search('(\d+-\d+)', intf):
                        intf_name, intf_range, junk = ((re.split(r'(\d+-\d+)', intf)))
                        intf_range_start,  intf_range_end = ((re.split(r'-', intf_range)))
                        intf_range_start, intf_range_end = int(intf_range_start), int(intf_range_end)
                        for j in range(intf_range_start, intf_range_end + 1):
                            interfaces = intf_name + str(j)
                            expanded_intf.append(interfaces)
                    else:
                        expanded_intf.append(intf)
            
                vi['interfaces'] = expanded_intf
    return interface_listofdict

def dict_filter(mydict, myset):
    newmydict = []
    for i in mydict:
        if i in set(myset):
            newmydict.append((i,mydict[i]))
    if newmydict:
        return(dict(newmydict))
    else:
        empty_dict = {}
        return(empty_dict)
