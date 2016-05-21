# !/usr/bin/env python2
# coding: utf-8

from wctorang import *
from copy import deepcopy
from itertools import chain
from itertools import product
import pc
import random
import time
from bitsets import bitset

IndexNum = 5


class IPolicySpace(object):
    def __init__(self, rects, index):
        self.rects = rects
        self.index = index

    # is_equal
    def __eq__(self, value):
        return self.__le__(value) and value.__le__(self)

    # is_subset
    def __le__(self, value):
        for sr in self.rects:
            rects = (sr.__and__(vr) for vr in value.rects)
            if sum(r[0].volume for r in rects if r) != sr.volume:
                return False
        return True

    # is_intersect
    def __mul__(self, value):
        for vr in value.rects:
            for sr in self.rects:
                if vr.__mul__(sr):
                    return True
        return False

    # intersect
    def __and__(self, value):
        rects = list(chain.from_iterable(vr.__and__(sr)
            for vr in value.rects for sr in self.rects))
        return PolicySpace(rects) if rects else None

    # subtract
    def __sub__(self, value):
        # deepcopy once
        rects = list(chain.from_iterable(sr.__sub__(value.rects[0])
            for sr in self.rects))
        if not rects: return None
        # update inplace
        result = PolicySpace(rects)
        for vr in value.rects[1:]:
            result.sub_rect(vr)
            if not result.rects:
                return None
        return result

    # union
    def __or__(self, value):
        minuend, subtrahend = (self, value) \
                if len(self.rects) >= len(value.rects) else (value, self)
        srects = deepcopy(subtrahend.rects)
        # deepcopy once
        rects = list(chain.from_iterable(sr.__sub__(subtrahend.rects[0])
            for sr in minuend.rects))
        if not rects: return PolicySpace(srects)
        # update inplace
        result = PolicySpace(rects)
        for vr in subtrahend.rects[1:]:
            result.sub_rect(vr)
            if not result.rects: return PolicySpace(srects)
        result.rects.extend(srects)
        return result

    # intersect a rectangle (inplace)
    def and_rect(self, rect):
        rects = []
        for sr in self.rects:
            for sd, vd in zip(sr.dims, rect.dims):
                if sd[0] > vd[1] or sd[1] < vd[0]:
                    break
                if sd[0] < vd[0]: sd[0] = vd[0]
                if sd[1] > vd[1]: sd[1] = vd[1]
            else:
                rects.append(sr)
        self.rects = rects

    # subtract a rectangle (inplace)
    def sub_rect(self, rect):
        rects = []
        for sr in self.rects:
            relation = sr.__div__(rect)
            if relation is None:
                rects.append(sr)
            elif relation >= 0:
                rects.extend(HyperRect.clip(sr.dims, rect.dims, True))
        self.rects = rects

    # merge neibour rect together
    def merge_rect(self):
        return True

    # union a rectangle (inplace)
    def or_rect(self, rect):
        rects = []
        for i, sr in enumerate(self.rects):
            relation = sr.__div__(rect)
            if relation is None:
                rects.append(sr)
            elif relation == 0:
                rects.extend(HyperRect.clip(sr.dims, rect.dims, True))
            elif relation > 0:
                rects.extend(self.rects[i:])
                break
        else:
            rects.append(deepcopy(rect))
        self.rects = rects


def RuleLe(left, right):
    for sd, vd in zip(left, right):
        if sd[0] < vd[0] or sd[1] > vd[1]:
            return False
    return True


def GenPolicyIte(Irs):
    """

    :param Irs: Indexed Rule set;
    :return: Indexed PolicySpace dict;
    """
    IPoSpaces = dict()
    for singleRule in reversed(Irs):
        for IPoSpace in IPoSpaces.values():
            IPoSpace.sub_rect(HyperRect(deepcopy(singleRule[:IndexNum])))
        if singleRule[IndexNum] not in IPoSpaces.keys():
            IPoSpaces[singleRule[IndexNum]] = IPolicySpace([HyperRect(deepcopy(singleRule[:IndexNum]))], singleRule[IndexNum])
        else:
            IPoSpaces[singleRule[IndexNum]].or_rect(HyperRect(deepcopy(singleRule[:IndexNum])))

    startflag = True
    for singleSpace in IPoSpaces.values():
        if startflag:
            TotalSpace = singleSpace
            startflag = False
        else:
            TotalSpace = TotalSpace.__or__(singleSpace)
    assert TotalSpace == IPolicySpace([HyperRect(deepcopy(Irs[-1][:IndexNum]))], 0)
    return IPoSpaces


def GenPolicyDir1(Irs):
    """

    :param Irs:
    :return: Indexed PolicySpace dict;
    """
    IPoSpaces = dict()
    shadows = list()
    for dim in range(0, IndexNum):
        shadows.append(pc.shadow_rules(Irs, dim))
    segnum = list()
    for dim in range(0, IndexNum):
        assert len(shadows[dim]) % 2 == 0
        segnum.append(range(len(shadows[dim]) >> 1))
    for single in product(*segnum):
        atomRect = list()
        for dim in range(0, IndexNum):
            atomRect.append([shadows[dim][single[dim] << 1], shadows[dim][(single[dim] << 1) + 1]])
        for rule in Irs:
            if RuleLe(atomRect, rule[:IndexNum]):
                if rule[IndexNum] not in IPoSpaces.keys():
                    IPoSpaces[rule[IndexNum]] = IPolicySpace([HyperRect(deepcopy(atomRect))], rule[IndexNum])
                else:
                    IPoSpaces[rule[IndexNum]].rects.append(HyperRect(deepcopy(atomRect)))
                break
    return IPoSpaces


def GenPolicyDir2(Irs):   # set version
    """

    :param Irs:
    :return: Indexed PolicySpace dict;
    """
    IPoSpaces = dict()
    shadows = list()
    for dim in range(0, IndexNum):
        shadows.append(pc.shadow_rules(Irs, dim))
    segnum = list()
    for dim in range(0, IndexNum):
        assert len(shadows[dim]) % 2 == 0
        segnum.append(range(len(shadows[dim]) >> 1))
    for single in product(*segnum):
        atomRect = list()
        for dim in range(0, IndexNum):
            atomRect.append([shadows[dim][single[dim] << 1], shadows[dim][(single[dim] << 1) + 1]])
        for rule in Irs:
            if RuleLe(atomRect, rule[:IndexNum]):
                if rule[IndexNum] not in IPoSpaces.keys():
                    # IPoSpaces[rule[IndexNum]] = IPolicySpace([HyperRect(atomRect)], rule[IndexNum])
                    IPoSpaces[rule[IndexNum]] = set()
                    IPoSpaces[rule[IndexNum]].add(single)
                else:
                    # IPoSpaces[rule[IndexNum]].or_rect(HyperRect(atomRect))
                    IPoSpaces[rule[IndexNum]].add(single)
                break
    return IPoSpaces


def CountRange(Irs):
    shadows = list()
    for dim in range(0, IndexNum):
        shadows.append(pc.shadow_rules(Irs, dim))
    segnum = list()
    volum = 1
    dimlen = list()
    print "This rule set is split into:"
    for dim in range(0, IndexNum):
        assert len(shadows[dim]) % 2 == 0
        segnum.append(range(len(shadows[dim]) >> 1))
        volum = volum * (len(shadows[dim]) >> 1)
        dimlen.append((len(shadows[dim]) >> 1))
    print dimlen
    print "Total volume: %d"% volum


def GenCBRules(path, max):
    rs = pc.load_rules(path + ".txt")
    for sr in rs:
        sr[IndexNum] = random.randint(0, max)
    f = open(path + "ed.txt", 'w')
    for rule in rs:
        for dim in rule[:IndexNum]:
            f.write("%d %d " % (dim[0], dim[1]))
        f.write("%d \n" % rule[IndexNum])
    f.close()


def ReadCBRules(path):
    rs = list()
    f = open(path + "ed.txt", 'r')
    for line in f:
        rule = list()
        tokens = line.split()
        rule.append([int(tokens[0]), int(tokens[1])])
        rule.append([int(tokens[2]), int(tokens[3])])
        rule.append([int(tokens[4]), int(tokens[5])])
        rule.append([int(tokens[6]), int(tokens[7])])
        rule.append([int(tokens[8]), int(tokens[9])])
        rule.append(int(tokens[10]))
        rs.append(rule)
    f.close()
    return rs


def GenPolicyAtom(Irs_list):
    """

    :param Irs_list:
    :return:
    """
    routerNum = len(Irs_list)
    IPS_list = list()
    IPoSpaces_list = list()
    for i in range(routerNum):
        IPoSpaces_list.append([0] * routerNum)
        IPS_list.append(GenPolicyIte(Irs_list[i]))

    # generate atomic policy space list:
    atomPSList = list()
    numofaPS = 0
    Noneset = list()
    for index1 in range(routerNum * routerNum):  # for each port:
        router1 = index1 / routerNum
        port1 = index1 % routerNum
        for index2 in range((router1 + 1) * routerNum, routerNum * routerNum):
            # Noneset += 1
            router2 = index2 / routerNum
            port2 = index2 % routerNum
            Atom = IPS_list[router1][port1].__and__(IPS_list[router2][port2])
            print (router1, port1, router2, port2)
            if Atom != None:
                atomPSList.append((Atom, (router1, port1, router2, port2)))
                IPoSpaces_list[router1][port1] += (1 << numofaPS)
                IPoSpaces_list[router2][port2] += (1 << numofaPS)
                numofaPS += 1
            else:
                Noneset.append((router1, port1, router2, port2))

    atomPSTuple = tuple(atomPSList)
    atomPSBitset = bitset('atomPSBitset', atomPSTuple)
    # A = atomPSBitset.fromint(IPoSpaces_list[1][0]).bools()
    # print Noneset
    return (atomPSBitset, IPoSpaces_list)


def simpleTest():
    """
    ** Revise IndexNum to 5 when run this function!
    :return:
    """
    rs = [[[0, 1], [0, 1], 0],
          [[0, 2], [3, 4], 1],
          [[3, 4], [0, 1], 2],
          [[0, 3], [0, 1], 1],
          [[2, 4], [2, 2], 0],
          [[0, 2], [2, 3], 2],
          [[0, 4], [0, 4], 3]]
    IPSs = GenPolicyDir1(rs)
    IPSs = GenPolicyIte(rs)
    Irs_list = list()
    rs = [[[0, 4], [0, 2], 0],
          [[0, 4], [0, 4], 1]]
    Irs_list.append(rs)
    rs = [[[0, 2], [0, 4], 0],
          [[0, 4], [0, 4], 1]]
    Irs_list.append(rs)
    GenPolicyAtom(Irs_list)
    print "Finish Simple Test"


def correctnessTest():
    rs = ReadCBRules("../multi_rules/acl/r0_50")
    for i in range(5, 50, 5):
        print i
        time1 = time.time()
        IPSsD = GenPolicyIte(rs[-i:])
        time2 = time.time()
        print time2 - time1
        IPSsI = GenPolicyDir1(rs[-i:])
        time3 = time.time()
        print time3 - time2
        for IPSkey in IPSsD.keys():
            assert IPSsD[IPSkey] == IPSsI[IPSkey]
    print "Finish correctness test"


def timeTest():
    rs = ReadCBRules("../multi_rules/acl/r1_50")
    for i in range(5, 50, 5):
        print ""
        print i
        CountRange(rs[-i:])
        time1 = time.time()
        IPSsI = GenPolicyIte(rs[-i:])
        time2 = time.time()
        print time2 - time1
        IPSsD = GenPolicyDir1(rs[-i:])
        time3 = time.time()
        print time3 - time2
        IPSsD = GenPolicyDir2(rs[-i:])
        time4 = time.time()
        print time4 - time3
    print "Finish Time Test"


def networkTest(routernum):
    # 5 routers, in multi_rules/acl, r0~4
    Irs_list = list()
    for rnum in range(0, routernum):
        Irs_list.append(ReadCBRules("../multi_rules/acl/r" + str(rnum) + "_50"))

    (atomPSBitset, IPoSpaceA_list1) = GenPolicyAtom(Irs_list)
    IPoSpace_list1 = list()
    for rnum in range(routernum):
        IPospace = list()
        for pnum in range(routernum):
            atomset = atomPSBitset.fromint(IPoSpaceA_list1[rnum][pnum]).members()
            if atomset == ():
                IPospace.append(None)
            else:
                portPoSpace = IPolicySpace(atomset[0][0].rects, pnum)
                for cubes in atomset[1:]:
                    portPoSpace = portPoSpace.__or__(cubes[0])
                IPospace.append(portPoSpace)
        IPoSpace_list1.append(IPospace)

    IPoSpace_list2 = list()
    for rnum in range(routernum):
        IPoSpace_list2.append(GenPolicyIte(Irs_list[rnum]))

    # # count 5 routers each have how many rects:
    # Rcount = list()
    # for rnum in range(0, routernum):
    #     count = list()
    #     for pnum in range(0, routernum):
    #         count.append(len(R[rnum][pnum].rects))
    #     Rcount.append(count)

    for i in range(routernum):
        assert IPoSpace_list1[0][i] == IPoSpace_list2[0][i]
        print i
    print "Finish network test"


if __name__ == "__main__":
    # timeTest()
    # correctnessTest()
    networkTest(5)
    # testBitset()
    # simpleTest()
