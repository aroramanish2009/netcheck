class NetcheckCommon:
    def __init__(self):
        pass

def append2list(listname, *argv):
    for arg in argv:
        listname.append(arg)
    return listname
