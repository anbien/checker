# By Lichee
# For checker project
# This file contains the self-made function to transfer wildcard expression into ranges;

from policyspace import HyperRect
from policyspace import PolicySpace

def constructwcrule(file):
    """
    Constructwcrule from bdd_rule file;
    Remove other information, only keep the part we care about;
    :param file: file name of bdd rule
    :return: a dict, {(inport, outport):list(match)}
    """
    f = open(file, 'r')
    wcrules = dict()
    for line in f:
        tokens = line.split()
        if line.startswith("New"):
            pass
        elif line.startswith("Action"):
            if tokens[1] not in ("fwd", "rw"):
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
    convert wildcard expression to range expression;
    :param length: length of this wildcard expression;
    :param wildcard: wildcard expression waiting to be converted;
    :return: a list of size 2, range, start with start and end with end;
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
    range.append(range[0] + 2 ** (length - first_x) - 1)
    return range


def splitmatch(rule):
    """
    split match into 7 ranges according to 7 truples' meaning;
    :param rule: match expression waiting to be splited;
    :return: split rule;
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


def genFullRule():
    """

    :return:
    """
    splitfullrule = splitmatch("XXXXXXXX,XXXXXXXX,XXXXXXXX,XXXXXXXX,XXXXXXXX,XXXXXXXX,XXXXXXXX,XXXXXXXX,XXXXXXXX,XXXXXXXX,XXXXXXXX,XXXXXXXX,XXXXXXXX,XXXXXXXX,XXXXXXXX,XXXXXXXX")
    fullrule = list()
    for dims in splitfullrule:
        fullrule.append(wildcard2range(len(dims), dims))
    return fullrule


def wcruletorangerule(wcrules):
    """
    Full function to turn a wc rule into range rule;
    rangeruleset[ruleindex] is a set of range rule with same ruleindex:(inport, outport)
    rangeruleset is the final set of a single router file;
    :param wcrules: the whole set of rules of a single router file before dealing with;
    :return: rangeruleset;
    """
    sum = 0
    rangeruleset = dict()
    for ruleindex in wcrules:
        rangeruleset[ruleindex] = list()
        for singlematch in wcrules[ruleindex]:
            splitrule = splitmatch(singlematch)
            singlerangerule = list()
            for dims in splitrule:
                singlerangerule.append(wildcard2range(len(dims), dims))
            rangeruleset[ruleindex].append(singlerangerule)
        sum += len(rangeruleset[ruleindex])
    print sum
    return rangeruleset


def gentestrangerule(wcrules):
    rangeruleset = list()
    for ruleindex in wcrules:
        for singlematch in wcrules[ruleindex]:
            splitrule = splitmatch(singlematch)
            singlerangerule = list()
            for dims in splitrule:
                singlerangerule.append(wildcard2range(len(dims), dims))
            rangeruleset.append(singlerangerule)
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


