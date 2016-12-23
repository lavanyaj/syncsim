from frugal1 import *

def get_cap(cap_file):
    f = open(cap_file, "r")
    links = {}
    for line in f.readlines():
        linkCapStr = line.rstrip("\n")
        linkStr, cap = line.split(" ")
        cap = float(cap)
        links[linkStr] = Link(linkStr, cap)
    #print "finished parsing cap file to get " + str(links)
    return links

def get_flows(tm_file):
    f = open(tm_file, "r")
    flows = {}
    for line in f.readlines():
        pathStr = line.rstrip("\n")
        if pathStr in flows:
            flows[pathStr].numFlows += 1
        else:
            pathList = pathStr.split(" ")[1:-1]
            flows[pathStr] = Msg(pathStr, 1, pathList)
    #print "finished parsing tm file to get " + str(flows)
    return flows

