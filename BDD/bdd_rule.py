'''
By Lichee

To hold BDD rules waiting to be generated into BDD

Represent by BDD_RULE
'''


class BDD_RULE(object):
    '''
    store the rules needed to generate BDD trees;
    one BDD_RULE specifies a set of rules who have same inports and outports
    '''

    def __init__(self, length):
        self.rulenum = 0
        self.rules = set()
        self.inport = 0
        self.outport = 0

    def __delete__(self):
        self.rules.clear()

def constructbddrules(file):
    f = open(file, 'r')
    bddrules = dict()
    for line in f:
        tokens = line.split()
        if line.startswith("New"):
            pass
        elif line.startswith("Action"):
            if not tokens[1] == "fwd":
                newfwdrule = False
            else:
                newfwdrule = True
        elif line.startswith("Inport"):
            inport = tokens[1].replace('[', '')
            inport = inport.replace(']', '')
        elif line.startswith("Outport"):
            outport = tokens[1].replace('[', '')
            outport = outport.replace(']', '')
        else:
            match = tokens[1].replace(',', '')
            if newfwdrule:
                if (inport, outport) not in bddrules.keys():
                    bddrules[(inport, outport)] = list()
                bddrules[(inport, outport)].append(match.upper())
    f.close()
    return bddrules

