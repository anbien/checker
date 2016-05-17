# By Lichee
# A simple implementation of atomic PSA

from wctorang import *

def atomic_PSA(hyrectset):
    """

    :param hyrectset:
    :return:
    """
    # atomicRect = set()
    singleAtomicRect = list()
    for hyRect in hyrectset:
        singleAtomic = set()
        singleAtomic.add(hyRect)
        fullrule = genFullRule()
        fullrule = HyperRect(fullrule)
        singleAtomic.add(fullrule.__sub__(hyRect))
        singleAtomicRect.append(singleAtomic)


if __name__ == "__main__":
    # test of atomicPSA
    wcrules = constructwcrule("../bdd_rule.txt")
    rangerule = wcruletorangerule(wcrules)
    hyrectset = dict()
    for ruleindex in rangerule:
        hyrectset[ruleindex] = list()
        for rule in rangerule[ruleindex]:
            hyrectset[ruleindex].append(HyperRect(rule))
        atomic_PSA(hyrectset[ruleindex])



