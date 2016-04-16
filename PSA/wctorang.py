# By Lichee
# For checker project
# This file contains the self-made function to transfer wildcard expression into ranges;

from policyspace import HyperRect
from policyspace import PolicySpace

def constructwcrule(file):
    f = open(file, 'r')
    wcrules = dict()
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
            match = tokens[1]
            if newfwdrule:
                if (inport, outport) not in wcrules.keys():
                    wcrules[(inport, outport)] = list()
                wcrules[(inport, outport)].append(match.upper())
    f.close()
    return wcrules


def wildcard2range(length, wildcard):
    """

    :param length:
    :param wildcard:
    :return:
    """
    range = list()
    if wildcard.isdigit():
        digi = 0
        for i in xrange(length):
            if wildcard[i] is '1':
                digi += 2 ** (length - 1 - i)
        range.append(digi)
        range.append(digi)
        return range
    first_x = wildcard.index('X')
    if first_x is 0:
        range.append(0)
    else:
        number = wildcard[0:first_x]
        digi = 0
        for i in xrange(len(number)):
            if number[i] is '1':
                digi += 2 ** (len(number) - 1 - i)
        range.append(digi)
    range.append(range[0] + 2 ** (length - first_x))
    return range


def splitmatch(rule):
    """

    :param rule:
    :return:
    """
    splitrule = list()
    tokens = rule.split(',')
    splitrule.append(tokens[0])
    splitrule.append(tokens[1] + tokens[2])
    splitrule.append(tokens[3] + tokens[4])
    splitrule.append(tokens[5])
    splitrule.append(tokens[6] + tokens[7] + tokens[8] + tokens[9])
    splitrule.append(tokens[10] + tokens[11] + tokens[12] + tokens[13])
    splitrule.append(tokens[14] + tokens[15])
    return splitrule


def wcruletorangerule(wcrules):
    """

    :return:
    """
    rangeruleset = dict()
    for ruleindex in wcrules:
        rangeruleset[ruleindex] = list()
        for singlematch in wcrules[ruleindex]:
            splitrule = splitmatch(singlematch)
            singlerangerule = list()
            for dims in splitrule:
                singlerangerule.append(wildcard2range(len(dims), dims))
            rangeruleset[ruleindex].append(singlerangerule)
    return rangeruleset


if __name__ == "__main__":

    # test of wc to range
    wcrules = constructwcrule("../bdd_rule.txt")
    rangerule = wcruletorangerule(wcrules)
    hyrectset = dict()
    for ruleindex in rangerule:
        hyrectset[ruleindex] = PolicySpace([HyperRect(rangerule[ruleindex][0])])
        for rule in rangerule[ruleindex][1:]:  # rangerule[] is a policy
            hyrectset[ruleindex].or_rect(HyperRect(rule))
    for ruleindex in rangerule:
        print ruleindex
    hyrectset[('100006', '')].__or__(hyrectset[('110002', '120002')])
    print "..."


