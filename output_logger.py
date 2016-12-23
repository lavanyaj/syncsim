def output_log(links, flows):
    i = 0
    for linkId in sorted(links.keys()):
        i += 1

        rate = 0
        if (links[linkId].numUnsat > 0):
            rate = round((links[linkId].C - links[linkId].sumSat)/links[linkId].numUnsat)
            
        out = "OUT: Link # %d %s removed in level %d with sumSat %d numUnsat %d rate %d ."%\
            (i, linkId, links[linkId].level, links[linkId].sumSat, links[linkId].numUnsat, rate)

        out += " " + str(i)
        out += " " + str(linkId)
        out += " " + str(rate)
        print out

    i = 0
    for flowId in sorted(flows.keys()):
        i += 1
        linkId = flows[flowId].t
        if (linkId == -1):
            out = "OUT: Flow # %d removed @ -1 when link -1 removed in level -1 with sumSat -1 numUnsat -1 ."
            continue

        rate = 0
        if (links[linkId].numUnsat > 0):
            rate = round((links[linkId].C - links[linkId].sumSat)/links[linkId].numUnsat)

        out = "OUT: Flow # %d removed @ %d when link %s removed in level %d with sumSat %d, numUnsat %d rate %d ."%\
            (i, flows[flowId].AR, linkId, links[linkId].level, links[linkId].sumSat, links[linkId].numUnsat, rate)

        out += " " + str(i)
        out += " " + str(linkId)
        out += " " + str(rate)
        print out
