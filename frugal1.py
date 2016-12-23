import sys
import copy
INFINITY = 1e6
# 3 types of messages/ links- AR/t, pickUpMinB, nd
SAT = "SAT"
UNSAT = "UNSAT"


class Msg:
    def __init__(self, flowId, numFlows, path):
        # flow presents in round 1,
        # link uses to calculate new label/ alloc
        self.AR = INFINITY
        self.t = -1

        # link fills in, in round 1
        # link uses to get maxSat in round 2
        self.labels = {}
        self.alloc = {}

        # link uses to calculate R in round 1
        self.oldLabels = {}
        self.oldAlloc = {}


        self.flowId = flowId
        self.numFlows = numFlows # numFlows on this path
        self.path = path

        # not sure if I'll use this
        self.hop = 0
        
        # flow picks up in round 3
        self.minB = INFINITY
        self.minBT = -1
        self.type = 3
        return

    def setType(self, type):
        if type == 1:
            self.oldLabels = copy.deepcopy(self.labels)
            self.labels = {}
            self.oldAlloc = copy.deepcopy(self.alloc)
            self.alloc = {}
            self.AR = self.minB
            self.t = self.minBT
            self.type = type
        elif type == 2:
            self.minB = INFINITY
            self.minBT = -1
            self.type = type
        else:
            print "nothing changed given type %d" % type

    def getString(self):
        ret = "Showing Flow ;"
        ret += "id: %s, type: %d, numFlows: %d; " % (str(self.flowId), self.type, self.numFlows)
        ret += "path: %s; " % str(self.path)
        ret += "labels: %s, alloc: %s;" % (str(self.labels), str(self.alloc))
        ret += "old labels: %s, alloc: %s;" % (str(self.oldLabels), str(self.oldAlloc))
        ret += "AR: %s, t: %s, minB: %s, minBT: %s; " % (str(self.AR), str(self.t), str(self.minB), str(self.minBT))
        ret += "type: %s" % (str(self.type))
        return ret
    
    def show(self):
        print self.getString()
        return

class Link:
    def __init__(self, linkId, C, ind=True):
        self.C = C
        self.linkId = linkId
        self.type = 3
        self.ind = ind
        # link uses in round 1, to calculate
        # different residual level per flow
        # based on its old alloc/ label
        self.sumSat = 0
        self.numSat = 0
        self.numUnsat = 0
        
        # link fills in, in round 1, based on comparing
        # flow's AR with calculated residual level
        self.newSumSat = 0
        self.newNumSat = 0
        self.newNumUnsat = 0

        # link fills in, in round 2 and uses to calculate
        # different B per flow (maxSat includes flow's own sat!!?)
        self.maxSat = 0

        # metadata: when link "converged"
        self.level = INFINITY
        return

    def setType(self, type):
        # reset values filled in during round type
        if type == 1:
            self.sumSat = self.newSumSat
            self.newSumSat = 0
            self.numSat = self.newNumSat
            self.newNumSat = 0
            self.numUnsat = self.newNumUnsat
            self.newNumUnsat = 0
            self.maxSat = 0
            self.type = type
        elif type == 2:
            # don't change anything
            # flow just picks up max(T, maxSat)
            self.type = type
        else:
            print "nothing changed for link given type %d" % type
        return

    def getString(self):
        ret = "Showing Link "
        oldR = self.getResidualLevel(msg=None, sumSat = self.sumSat, numSat = self.sumSat,\
                                           numUnsat = self.numUnsat)
        newR = self.getResidualLevel(msg=None, sumSat = self.newSumSat, numSat = self.newNumSat,\
                                           numUnsat = self.newNumUnsat)
        ret += ("id: %s, type: %d, C: %d; " % (str(self.linkId), self.type, self.C))
        
        ret += "new sumSat: %d, numSat: %d, numUnsat: %d; " % (self.newSumSat, self.newNumSat, self.newNumUnsat)
        ret += "sumSat: %d, numSat: %d, numUnsat: %d; " % (self.sumSat, self.numSat, self.numUnsat)
        ret += "maxSat: %d; " % self.maxSat
        ret += "newR: %s; " % str(newR)
        ret += "oldR: %s; " % str(oldR)
        if self.type == 2:
            ret += "B = max(maxSat = %d, newR for flow = %d); " % (self.maxSat, newR)
        
        ret += "type: %d" % self.type
        return ret 

    def show(self):
        print self.getString()

    def handleMsg(self, msg):
        if (self.type == 1 and msg.type == 1):
            self.handle1Msg(msg)
        elif (self.type == 2 and msg.type == 2):
            self.handle2Msg(msg)
        else:
            print "link type " + str(self.type) +\
                " does not match msg type " + str(msg.type) +\
                " or type not handled"
            
        return

    def handle2Msg(self, msg):
        # uses newly calculated rates to get bottleneck level
        R = self.getResidualLevel(msg = msg, sumSat = self.newSumSat,\
                                      numSat = self.newNumSat, numUnsat = self.newNumUnsat)
        B = R
        if round(self.maxSat) > round(B):
            B = self.maxSat

#         print "residual level at link " + str(self.linkId) +\
#             " is " + str(R) + ", maxSat is " + str(self.maxSat) +\
#             " so B is " + str(B)

        if round(msg.minB) > round(B):
            msg.minB = B
            msg.minBT = self.linkId
        return

    def getResidualLevel(self, msg, sumSat, numUnsat, numSat):        
        if (self.ind or msg == None):
            R = self.C
            if (numUnsat > 0):
                R = (self.C - sumSat)/numUnsat
            return R
        
        tmpSumSat = sumSat
        tmpNumUnsat = numUnsat
        tmpNumSat = numSat
        
        if self.linkId in msg.oldAlloc and self.linkId in msg.oldLabels:
            oldLabel = msg.oldLabels[self.linkId]
            if oldLabel == SAT:
                oldAlloc = msg.oldAlloc[self.linkId]
                tmpSumSat -= oldAlloc * msg.numFlows
                tmpNumUnsat += msg.numFlows
                tmpNumSat -= msg.numFlows
        elif (self.linkId not in msg.oldAlloc) and (self.linkId not in msg.oldLabels):            
            # new flow
            #print "new flow"
            tmpNumUnsat += msg.numFlows
            
        assert(tmpNumUnsat > 0)
        R = (self.C - tmpSumSat)/tmpNumUnsat        
        return R
    
    def handle1Msg(self, msg):
        # use old sumSat, numUnsat etc. to calculate residual level to
        # decide if flow is sat or unsat

        R = self.getResidualLevel(msg=msg, numSat=self.numSat,\
                                      numUnsat=self.numUnsat, sumSat = self.sumSat)
        if (round(msg.AR) < round(R)):
            # print("Flow " + str(msg.flowId) + " marked SAT at link " + str(self.linkId) +\
            #           " because AR " + str(msg.AR) + " is less than oldR " + str(R))
            # flow should be marked SAT at AR now
            msg.alloc[self.linkId] = msg.AR
            msg.labels[self.linkId] = SAT
            # update sumSat/ numSat
            self.newSumSat += msg.AR * msg.numFlows
            self.newNumSat += msg.numFlows
            if round(msg.AR) > round(self.maxSat):
                self.maxSat = msg.AR
            
        else:
            #msg.alloc[self.linkId] = R
            msg.labels[self.linkId] = UNSAT
            msg.alloc[self.linkId] = None
            self.newNumUnsat += msg.numFlows
            # print("Flow " + str(msg.flowId) + " marked UNSAT at link " + str(self.linkId) +\
            #           " because AR " + str(msg.AR) + " is >= than oldR" + str(R))

            



# for rounds 1 to 3
# round 1 of all flows- set type to 1 for all flows and links and reset state for type??
# for each flow, process at all hops in forward direction (handle_msg_1/2/3)
# print state of all links at end of round

def run(maxRounds, maxEvents, links, flows):
    linkList = sorted(links.keys())
    flowList = sorted(flows.keys())
    #for i in flowList:
        #flows[i].show()

    #for i in linkList:
        #links[i].show()

    ev = 0
    round = 0
    
    oldMsgs = []
    newMsgs = []
    print "Flows starting"
    while (round < maxRounds and ev < maxEvents):
        print "\nRound " + str(round)
        for type in range(1,3):
            # change type of link/ flow to forward(1) or backward(2)
            for flowId in flowList:
                flows[flowId].setType(type)
            for linkId in linkList:
                links[linkId].setType(type)
            print "\nPass " + str(type)

            # for each flow, process packet on each hop (order doesn't matter for now)
            for flowId in flowList:
                for linkId in flows[flowId].path:
                    #print "handle msg of " + str(flowId) + " at " + str(linkId) + " type of msg " + str(flows[flowId].type)
                    links[linkId].handleMsg(flows[flowId])
                    ev += 1

            # show messages and link state at end of round
            #print "\n At the end of Round " + str(round) + ", pass " + str(type)
            #for linkId in linkList:
                #links[linkId].show()
            for flowId in flowList:
                newMsgs.append(flows[flowId].getString())
                #flows[flowId].show()

            # check if converged
            if (type == 1):
                if len(oldMsgs) > 0:                    
                    if str(newMsgs) == str(oldMsgs):
                        print "converged after %d rounds (%d events)" % (round, ev)
                        sys.exit(0)
                oldMsgs = copy.deepcopy(newMsgs)
                newMsgs = []
            # end of for type in ..
        round += 1
        # end of for round in ..
    print("ending ev is " + str(ev) + ", round is " + str(round))


