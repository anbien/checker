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
    Convert a indexed Rule set into predicates of each port;
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
    return IPoSpaces


def GenPolicyDir1(Irs):
    """
    Convert a indexed Rule set into predicates of each port;
    In a space - cut way;
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
    Set version of GenPolicyDir;
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
                    IPoSpaces[rule[IndexNum]] = set()
                    IPoSpaces[rule[IndexNum]].add(single)
                else:
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
    for index1 in range(routerNum * routerNum):  # for each port:
        router1 = index1 / routerNum
        port1 = index1 % routerNum
        for index2 in range((router1 + 1) * routerNum, routerNum * routerNum):
            # Noneset += 1
            router2 = index2 / routerNum
            port2 = index2 % routerNum
            Atom = IPS_list[router1][port1].__and__(IPS_list[router2][port2])
            # print (router1, port1, router2, port2)
            if Atom != None:
                atomPSList.append(Atom)
                # atomPSList.append((Atom, (router1, port1, router2, port2)))
                IPoSpaces_list[router1][port1] += (1 << numofaPS)
                IPoSpaces_list[router2][port2] += (1 << numofaPS)
                numofaPS += 1

    atomPSTuple = tuple(atomPSList)
    atomPSBitset = bitset('atomPSBitset', atomPSTuple)
    return (atomPSBitset, IPoSpaces_list)


def DecodePolicyAtom1(atomPSBitset, IPoSpaceA, index):
    atomset = atomPSBitset.fromint(IPoSpaceA).members()
    if atomset == ():
        IPoSpace = None
    else:
        flag = True
        for cube in atomset:
            if flag:
                IPoSpace = IPolicySpace(atomset[0].rects, index)
                flag = False
            else:
                for atomrect in cube.rects:
                    IPoSpace.rects.append(atomrect)
    return IPoSpace


def DecodePolicyAtom2(atomPSBitset, IPoSpaceA, index):
    atomset = atomPSBitset.fromint(IPoSpaceA).members()
    if atomset == ():
        IPoSpace = None
    else:
        flag = True
        for cube in atomset:
            if flag:
                IPoSpace = IPolicySpace(atomset[0].rects, index)
                flag = False
            else:
                IPoSpace = IPoSpace.__or__(cube)
    return IPoSpace

def TestGenPolicyIte(Irs, IPoSpaces):
    """
    Test the correctness of function "GenPolicyIte()"
    :param Irs:
    :param IPoSpaces:
    :return: Nothing
    # TODO: try unittest;
    """
    startflag = True
    for singleSpace in IPoSpaces.values():
        if startflag:
            TotalSpace = singleSpace
            startflag = False
        else:
            TotalSpace = TotalSpace.__or__(singleSpace)
    assert TotalSpace == IPolicySpace([HyperRect(deepcopy(Irs[-1][:IndexNum]))], 0)


def TestFunction():
    """
    ** Revise IndexNum to 2 when run this function!
    ** Revise DIM_POINT_MAX in pc also!
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


def TestConsistence(rule):
    rs = ReadCBRules(rule)
    IPSsD = GenPolicyIte(rs)
    IPSsI = GenPolicyDir1(rs)
    for IPSkey in IPSsD.keys():
        assert IPSsD[IPSkey] == IPSsI[IPSkey]
    print "Finish correctness test"


def TestTime(rule, rulenum):
    rs = ReadCBRules(rule)
    for i in range(5, rulenum, 5):
        print ""
        print "Rule Num: %d" % i
        CountRange(rs[-i:])
        time1 = time.time()
        IPSsI = GenPolicyIte(rs[-i:])
        time2 = time.time()
        print time2 - time1
        IPSsD1 = GenPolicyDir1(rs[-i:])
        time3 = time.time()
        print time3 - time2
        IPSsD2 = GenPolicyDir2(rs[-i:])
        time4 = time.time()
        print time4 - time3
    print "Finish Time Test"


def TestRealNetwork(routernum, path, rulenum):
    # 5 routers, in multi_rules/acl, r0~4
    Irs_list = list()
    for rnum in range(0, routernum):
        Irs_list.append(ReadCBRules(path + str(rnum) + "_" + str(rulenum)))

    (atomPSBitset, IPoSpaceA_list1) = GenPolicyAtom(Irs_list)
    IPoSpace_list1 = list()
    for rnum in range(routernum):
        IPospace = list()
        for pnum in range(routernum):
            IPospace.append(DecodePolicyAtom2(atomPSBitset, IPoSpaceA_list1[rnum][pnum], pnum))
        IPoSpace_list1.append(IPospace)

    IPoSpace_list2 = list()
    for rnum in range(routernum):
        IPoSpace_list2.append(GenPolicyIte(Irs_list[rnum]))

    for i in range(routernum):
        assert IPoSpace_list1[0][i] == IPoSpace_list2[0][i]
        print i
    print "Finish network test"


def TestSpeed(routernum, path, rulenum):
    """
    Test the speed of two function:
    :return:
    """
    print "==============================================================="
    print "Test with %d routers, each have %s rules;" % (routernum, rulenum)
    Irs_list = list()
    for rnum in range(0, routernum):
        Irs_list.append(ReadCBRules(path + str(rnum) + "_" + rulenum))

    time0 = time.time()
    (atomPSBitset, IPoSpaceA_list1) = GenPolicyAtom(Irs_list)
    time1 = time.time()
    print "Atom Pre-dealing time: %f" % (time1 - time0)
    time0 = time.time()
    IPoSpace_list2 = list()
    for rnum in range(routernum):
        IPoSpace_list2.append(GenPolicyIte(Irs_list[rnum]))
    time1 = time.time()
    print "Original Pre-dealing time: %f" % (time1 - time0)
    print "---------------------------------------------------------------"

    # Some statistics about the final result:
    print "Total %d atom policy space in atomPS set;" % atomPSBitset._len

    print "In Original PSA:"
    Rrectnum = list()
    for rnum in range(routernum):
        Prectnum = list()
        for pnum in range(routernum):
            Prectnum.append(len(IPoSpace_list2[rnum][pnum].rects))
        Rrectnum.append(Prectnum)
    for rnum in range(routernum):
        print "Router %d have these rect in each port:" % rnum
        print Rrectnum[rnum]
    print "---------------------------------------------------------------"

    # Test Policy Checking time:
    # Randomly choose some rules to intersect, union;
    print "Start Policy Checking time test;"
    testRoterNum = 3
    testNum = 10
    timeAtom = 0
    timeOri = 0
    for i in range(testNum): # 100 test case;
        raw = list()
        routerset = set()
        action = list()
        for j in range(testRoterNum):
            raw.append(random.randint(0, routernum * routernum - 1))
        RtrPort = list()
        for j in range(testRoterNum):
            router = raw[j] / routernum
            RtrPort.append((router, raw[j] % routernum))
            if router not in routerset:
                routerset.add(router)
                action.append(1) # 0 for and, 1 for or
            else:
                action.append(0)
        time0 = time.time()
        Atom = IPoSpaceA_list1[RtrPort[0][0]][RtrPort[0][1]]
        for j in range(1, testRoterNum):
            if action[j - 1]:
                Atom = Atom | IPoSpaceA_list1[RtrPort[j][0]][RtrPort[j][1]]
            else:
                Atom = Atom & IPoSpaceA_list1[RtrPort[j][0]][RtrPort[j][1]]
        AtomPS = DecodePolicyAtom1(atomPSBitset, Atom, 0)
        # AtomPS2 = DecodePolicyAtom2(atomPSBitset, Atom, 0)
        # assert AtomPS == AtomPS2
        time1 = time.time()
        timeAtom += (time1 - time0)
        time0 = time.time()
        Ori = IPoSpace_list2[RtrPort[0][0]][RtrPort[0][1]]
        for j in range(1, testRoterNum):
            if Ori is None:
                break
            else:
                if action[j - 1]:
                    Ori = Ori.__or__(IPoSpace_list2[RtrPort[j][0]][RtrPort[j][1]])
                else:
                    Ori = Ori.__and__(IPoSpace_list2[RtrPort[j][0]][RtrPort[j][1]])
        time1 = time.time()
        timeOri += (time1 - time0)
        # if Ori is None:
        #     assert Atom == 0
        # else:
        #     assert Ori == AtomPS
    print "Atom Time: %f" % timeAtom
    print "Original Time: %f" % timeOri
    print "==============================================================="


if __name__ == "__main__":
    # for i in range(5):
        # GenCBRules("../multi_rules/acl_50/r" + str(i) + "_50", 4)
    TestSpeed(5, "../multi_rules/acl_50/r", "50")
    TestSpeed(5, "../multi_rules/acl_100/r", "100")
    TestSpeed(5, "../multi_rules/acl_1K/r", "1K")
    # TestRealNetwork(5, "../multi_rules/acl_50/r", 50)
