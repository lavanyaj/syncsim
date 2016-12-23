import sys
import copy
INFINITY = 1e6

# all we need from flows is path
# all we need from links is capacity
# frugal1 Link/ Msg has more than enough..

def cpg(maxRounds, maxEvents, links, flows):
    linkList = sorted(links.keys())
    flowList = sorted(flows.keys())
    numLinks = len(linkList)
    numFlows = len(flowList)
    
    ev = 0

    # links that are still active in Cpg
    activeLinks = {}

    # capacity of active links, after subtracting
    # allocations of frozen flows 
    activeLinkCapacities = {}


    # flows that are still active in Cpg
    activeFlows = {}
    
    for linkId in links:
        activeLinks[linkId] = True
        activeLinkCapacities[linkId] = links[linkId].C

    for flowId in flows:
        activeFlows[flowId] = True

    flowsPerLink = {}
    for flowId in flowList:
        path = flows[flowId].path
        for link in path:
            if link not in flowsPerLink:
                flowsPerLink[link] = {flowId: True}
            elif flowId not in flowsPerLink[link]:
                flowsPerLink[link][flowId] = True
            # else do nothing

    for linkId in sorted(flowsPerLink.keys()):
        af = sorted([f for f in flowsPerLink[linkId]\
                         if f in activeFlows and activeFlows[f]])
        
        print "Link %s has %d active flows: %s"\
            % (linkId, sum([flows[f].numFlows for f in af]),\
                   str(af))
        
    coLinks = {}
    for link in flowsPerLink:
        listFlows = sorted(flowsPerLink[link].keys())
        flowsPerLink[link] = listFlows
        coLinks[link] = []

    flowsPerLinkPair = {}
    for i in range(numLinks):
        link1 = linkList[i]
        if link1 not in flowsPerLink:
            continue
        for j in range(i+1, numLinks):
            link2 = linkList[j]
            if link2 not in flowsPerLink:
                continue

            key = (link1, link2)
            if link2 < link1:
                key = (link2, link1)

            common = list(set(flowsPerLink[link1])\
                              & set(flowsPerLink[link2]))
            if (len(common) > 0):
                flowsPerLinkPair[key] = common
                coLinks[link1].append(link2)
                coLinks[link2].append(link1)
    # closes for i in range(..
                
    # all the variables
    # activeLinks, activeLinkCapacities, currentLinkRates, currentMinLinks
    # activeFlows
    # flowsPerLink[link] is a list of flows sorted by flowId,
    # coLinks[link] is a set of coLinks of link, flowsPerLinkPair[(link1,link2)]
    # is the list of common flows of link1 and link2 (defined only if at least one)
                
    level = 1
    linksRemovedByLevel = {}
    linksRemovedSp = []
    
    flowsRemovedByLevel = {}
    while(level < maxRounds):
        print ("Level %s" % level)
        linksRemovedByLevel[level] = []
        flowsRemovedByLevel[level] = []
        
        currentLinkRates = {}
        currentMinLinks = []
        # all active links calculate rate using active capacity and active flows
        for linkId in activeLinks:
            if not activeLinks[linkId]:
                continue

            C = activeLinkCapacities[linkId]
            if C == 0:
                activeLinks[linkId] = False
                linksRemovedSp.append((linkId, "active capacity is 0", level))
                continue
            assert(round(C)> 0)
            
            
            if linkId not in flowsPerLink:
                activeLinks[linkId] = False
                linksRemovedSp.append((linkId, "no flows", level))
                continue

            N = 0
            for f in flowsPerLink[linkId]:
                if f in activeFlows and activeFlows[f]:
                    N += flows[f].numFlows
            if (N == 0):
                activeLinks[linkId] = False
                linksRemovedSp.append((linkId, "no active flows", level))
                continue            
            R = C/float(N)
            currentLinkRates[linkId] = R

            print "Link %s is active with %d active flows sharing %d Mb/s: R = %d"\
                % (linkId, N, C, R)

        # all active links check if they're minimum
        for linkId in activeLinks:
            if not activeLinks[linkId]:
                continue
            assert(linkId in currentLinkRates)
            rates = []
            assert(linkId in coLinks)
            for otherLink in coLinks[linkId]:
                if otherLink in activeLinks and activeLinks[otherLink]:
                    assert(otherLink in currentLinkRates)
                    rates.append(currentLinkRates[otherLink])
            if len(rates) == 0 or\
                    round(currentLinkRates[linkId]) < round(min(rates)):
                currentMinLinks.append(linkId)
               
        # for all min links
        #  update capacities of active co links
        #  update number of active common flows
        #  remove link from list of active links
        # alternative: for each link: for each flow check active : for each link in path check active
        # versus this: for each link: for each co-link check active: for each common flow check active ..
        for linkId in currentMinLinks:
            # Fill in bottleneck info in link struct
            # sumSat, numUnsat and numSat
            links[linkId].sumSat = links[linkId].C - activeLinkCapacities[linkId]
            N = 0
            for f in flowsPerLink[linkId]:
                if f in activeFlows and activeFlows[f]:
                    N += flows[f].numFlows
            assert(N > 0)
            links[linkId].numUnsat = N
            links[linkId].numSat = len(flowsPerLink[linkId]) - N
            links[linkId].level = level
            
            for otherLink in coLinks[linkId]:
                if otherLink not in activeLinks or not activeLinks[otherLink]:
                    # could be some link that became inactive
                    # during this loop, once its active cap hit 0
                    continue
                key = (linkId, otherLink)
                if otherLink < linkId:
                    key = (otherLink, linkId)
                assert(key in flowsPerLinkPair)
                numCommon = 0
                for f in flowsPerLinkPair[key]:
                    if f in activeFlows and activeFlows[f]:
                        numCommon += flows[f].numFlows
                        # don't mark this flow inactive yet,
                        # since we need to remove it from more
                        # colinks
                if numCommon > 0:
                    print ("Links %s have %d active flows in common, sat @ rate %d" %\
                               (str(key), numCommon, currentLinkRates[linkId]))
                    totalAlloc = numCommon * currentLinkRates[linkId]
                    activeLinkCapacities[otherLink] -= totalAlloc
                    if round(activeLinkCapacities[otherLink]) == 0:
                        # okay to mark as inactive since we no longer
                        # do anything with this link, which has
                        # no more flows unless its in minLinks too
                        activeLinkCapacities[otherLink] = 0
                        # activeLinks[otherLink] = False
                        # linksRemovedSp.append((linkId, "active cap became 0", level))

        for linkId in currentMinLinks:
            assert(links[linkId].numUnsat > 0)
            R = (links[linkId].C - links[linkId].sumSat)\
                /links[linkId].numUnsat
            for f in flowsPerLink[linkId]:
                if (f in activeFlows and activeFlows[f]):
                    # fill in bottleneck info for flow
                    flows[f].AR = R
                    flows[f].t = linkId
                    activeFlows[f] = False
                    flowsRemovedByLevel[level].append(f)
                    
            if linkId in activeLinks and activeLinks[linkId]:
                activeLinks[linkId] = False
                linksRemovedByLevel[level].append(linkId)
        print ("%d links removed in level %d: %s" %\
                   (len(linksRemovedByLevel[level]),\
                        level, linksRemovedByLevel[level][:3]))
        print ("%d flows remove in level %d: %s" %\
                   (len(flowsRemovedByLevel[level]),\
                        level, flowsRemovedByLevel[level][:3]))
        numActiveFlows = len([f for f in activeFlows if activeFlows[f]])
        if (numActiveFlows == 0):
            break
        level += 1
    print("level is " + str(level))
