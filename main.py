"""
Created by lichee


"""
import time
import random
import sys
from itertools import product
from operator import mul

from HSA.headerspace.hs import *
from HSA.headerspace.tf import *
from HSA.parser.cisco_router_parser import cisco_router

from BDD import bdd
from BDD import bdd_rule
from PSA.policyspace import PolicySpace
from PSA.policyspace import HyperRect
from PSA import wctorang
from PSA import pc


SF_DIM_NUM = 5
SF_DIM_POINT_BITS = [32, 32, 16, 16, 8]
#SF_DIM_POINT_BITS = [8, 16, 16, 8, 32, 32, 16]
DIM_NUM = 5
DIM_POINT_BITS = [32, 32, 16, 16, 8]
UINT32_MAX, UINT16_MAX, UINT8_MAX = ((1 << i) - 1 for i in [32, 16, 8])
SF_DIM_POINT_MAX = [UINT8_MAX, UINT16_MAX, UINT16_MAX, UINT8_MAX, UINT32_MAX, UINT32_MAX, UINT16_MAX]

routername = ["bbra", "bbrb", "boza", "bozb",
              "coza", "cozb", "goza", "gozb",
              "poza", "pozb", "roza", "rozb",
              "soza", "sozb", "yoza", "yozb"]

def rule_le(left, right):
    for sd, vd in zip(left, right):
        if sd[0] < vd[0] or sd[1] > vd[1]:
            return False
    return True


def pre_deal():
    for router_ in routername:
        cs = cisco_router(1)
        L = cs.hs_format["length"]
        tf = TF(L)
        tf.set_prefix_id(router_ + "_rtr")
        cs.read_arp_table_file("./data/Stanford_backbone/" + router_ + "_rtr_arp_table.txt")
        cs.read_mac_table_file("./data/Stanford_backbone/" + router_ + "_rtr_mac_table.txt")
        cs.read_config_file("./data/Stanford_backbone/" + router_ + "_rtr_config.txt")
        cs.read_spanning_tree_file("./data/Stanford_backbone/" + router_ + "_rtr_spanning_tree.txt")
        cs.read_route_file("./data/Stanford_backbone/" + router_ + "_rtr_route.txt")
        cs.optimize_forwarding_table()
        cs.generate_port_ids([])
        cs.generate_transfer_function(tf)
        tf.write_bdd_rule("./stanford/" + router_ + "_bdd_rule.txt")


def predeal_atom(range_rule):
    atom_rule = list()
    for i in range(len(range_rule)):
        atom_rule.append(set())
    shadows = list()
    for dim in range(SF_DIM_NUM):
        shadows.append(pc.shadow_rules(range_rule, dim))
    segnum = list()
    for dim in range(SF_DIM_NUM):
        # assert len(shadows[dim]) % 2 == 0
        segnum.append(range(len(shadows[dim]) >> 1))
    for atom_index in product(*segnum):
        atom_rect = list()
        for dim in range(SF_DIM_NUM):
            atom_rect.append([shadows[dim][atom_index[dim] << 1], shadows[dim][(atom_index[dim] << 1) + 1]])
        for i in range(len(range_rule)):
            if rule_le(atom_rect, range_rule[i]):
                atom_rule[i].add(atom_index)
                break
        # print atom_index
    return atom_rule

#@profile
def predeal_atom2(range_rule):
    atom_rule = [0] * len(range_rule)
    shadows = list()
    segnum = list()
    base = list()

    for dim in range(SF_DIM_NUM):
        shadows.append(pc.shadow_rules(range_rule, dim))
        segnum.append(range(len(shadows[dim]) >> 1))
    print segnum

    for dim in range(SF_DIM_NUM - 1):
        # reduce(mul, (d[1] - d[0] + 1 for d in self.dims))
        base.append(reduce(mul, (len(segnum[d]) for d in range(dim, SF_DIM_NUM))))
    base.append(1)

    for atom_index in product(*segnum):
        atom_rect = list()
        atom = 0
        for dim in range(SF_DIM_NUM):
            atom_rect.append([shadows[dim][atom_index[dim] << 1], shadows[dim][(atom_index[dim] << 1) + 1]])
            atom += mul(atom_index[dim], base[dim])
        for i in range(len(range_rule)):
            if rule_le(atom_rect, range_rule[i]):
                atom_rule[i] += atom
                break
        # print atom_index
    return atom_rule

#@profile
def predeal_bdd(prefix_rules):
    BDDlist = list()
    for single_rule in prefix_rules:
        bdd1 = bdd.BDD()
        bdd1.construct(single_rule)
        BDDlist.append(bdd1)
        bdd1.clear()
    return BDDlist


#@profile
def predeal_wc(prefix_rules):
    wc_list = list()
    for single_rule in prefix_rules:
        wc_test = headerspace(16)
        wc_test = wildcard_create_from_string(single_rule)
        wc_list.append(wc_test)
    return wc_list


#@profile
def predeal_psa(range_rules):
    psa_list = list()
    for single_rule in range_rules:
        psa_test = PolicySpace([HyperRect(deepcopy(single_rule))])
        psa_list.append(psa_test)
    return psa_list


def pick01withpro(pro):
    x = random.uniform(0, 1)
    if x < pro:
        return 1
    else:
        return 0


#@profile
def test_simple_policy_intersect(router_, rulenum, testnum, pro):
    """

    :param router_: the router waiting to be tested;
    :param rulenum:
    :param testnum:
    :return:
    """
    testset = list()
    # bddrules = bdd_rule.constructbddrules("./stanford/" + router_ + "_bdd_rule.txt")
    prefix_rules = bdd_rule.conwcrules("./stanford/" + router_ + "_bdd_rule.txt")
    for i in range(testnum):
        testruleset = list()
        for j in range(rulenum):
            testruleset.append((random.randint(0, len(prefix_rules) - 1), pick01withpro(pro)))
            # 1 for or, 0 for and
        testset.append(testruleset)

    print "==============================================================================="
    print "Start the set operation test of router " + router_
    # print "This ruleset have %d rules in total" % len(prefix_rules)
    print "Test rule number: %d, test number: %d" % (rulenum, testnum)
    print "-----------------------------------------------------------------------"
    # Here start BDD
    print "BDD:"
    bdd1 = bdd.BDD()
    bdd2 = bdd.BDD()
    bdd3 = bdd.BDD()
    time1 = time.time()
    for single_rule in prefix_rules:
        bdd1.construct(single_rule)
        bdd1.clear()
    time2 = time.time()
    bdd_pre_time = time2 - time1
    print "Pre-dealing time: %f" % (time2 - time1)

    # In order to save the space, generate bdd every time to be added into final results;
    bdd_time = list()
    for i in range(testnum):
        bdd1.clear()
        bdd2.clear()
        bdd3.clear()
        time1 = time.time()
        bdd1.construct(prefix_rules[testset[i][0][0]])
        bdd2.construct(prefix_rules[testset[i][1][0]])
        if testset[i][0][1]:
            bdd3 = bdd3.apply_ite('|', bdd2, bdd1)
        else:
            bdd3 = bdd3.apply_ite('&', bdd2, bdd1)
        bdd3.reduce()
        totalnode = bdd3.nodenum
        maxnode = bdd3.nodenum
        for rule_action in testset[i][2:-1]:
            bdd1.construct(prefix_rules[rule_action[0]])
            if rule_action[1]:
                bdd3 = bdd3.apply_ite('|', bdd1, bdd3)
            else:
                bdd3 = bdd3.apply_ite('&', bdd1, bdd3)
            bdd3.reduce()
            totalnode += bdd3.nodenum
            if maxnode < bdd3.nodenum:
                maxnode = bdd3.nodenum
        time2 = time.time()
        bdd_time.append(time2 - time1)
        print "Average node num: %f" % (totalnode * 1.0 / len(prefix_rules))
        # print "Max node num: %d" % maxnode
    # print bdd_time
    print "Average time: %f" % ((sum(bdd_time) / len(bdd_time)) - bdd_pre_time * rulenum /
                               len(prefix_rules))
    # print "Original average time: %f" % (sum(bdd_time) / len(bdd_time))
    print "-----------------------------------------------------------------------"

    # Wildcard Expression
    print "wildcard:"
    wc_time = list()
    wc_test = headerspace(16)
    time1 = time.time()
    for single_rule in prefix_rules:
        wc_test = wildcard_create_from_string(single_rule)
    time2 = time.time()
    wc_pre_time = time2 - time1
    print "Pre-dealing time: %f" % (time2 - time1)
    # wc_list = predeal_wc(prefix_rules)

    for i in range(testnum):
        time1 = time.time()
        wc1 = headerspace(16)
        wc1.add_hs(wildcard_create_from_string(prefix_rules[testset[i][0][0]]))
        wc_max = wc1.hs_list.__len__()
        wc_num = wc_max
        for rule_action in testset[i][1:-1]:
            if rule_action[1]:
                wc1.add_hs(wildcard_create_from_string(prefix_rules[rule_action[0]]))
            else:
                wc1.intersect(wildcard_create_from_string(prefix_rules[rule_action[0]]))
            if wc1.hs_list:
                wc_num += len(wc1.hs_list)
                if wc_max < len(wc1.hs_list):
                    wc_max = len(wc1.hs_list)
        time2 = time.time()
        print "Average wc num: %f" % (wc_num * 1.0 / len(prefix_rules))
        # print "Max wc num %d" % wc_max
        wc_time.append(time2 - time1)
    # print wc_time
    print "Average time: %f" % ((sum(wc_time) / len(wc_time)) - wc_pre_time * rulenum /
                                len(prefix_rules))
    # print "Original average time: %f" % (sum(wc_time) / len(wc_time))
    print "-----------------------------------------------------------------------"

    # PSA test
    print "PSA:"
    psa_time = list()
    wcrules = wctorang.constructwcrule("./stanford/" + router_ + "_bdd_rule.txt")
    range_rule = wctorang.gentestrangerule(wcrules)

    time1 = time.time()
    pca_list = predeal_psa(range_rule)
    time2 = time.time()
    psa_pre_time = time2 - time1
    print "Pre-dealing time: %f" % (time2 - time1)

    for i in range(testnum):
        time1 = time.time()
        hyrectset = PolicySpace([HyperRect(deepcopy(range_rule[testset[i][0][0]]))])
        hr_num = len(hyrectset.rects)
        hr_max = hr_num
        for rule_action in testset[i][1:-1]:
            if rule_action[1]:
                hyrectset.or_rect(HyperRect(deepcopy(range_rule[rule_action[0]])))
            else:
                hyrectset.and_rect(HyperRect(deepcopy(range_rule[rule_action[0]])))
            hr_num += len(hyrectset.rects)
            if hr_max < len(hyrectset.rects):
                hr_max = len(hyrectset.rects)
        time2 = time.time()
        print "Average hyperrect num: %f" % (hr_num * 1.0 / len(range_rule))
        # print "Max: %d" % hr_max
        psa_time.append(time2 - time1)
    #nprint psa_time
    print "Average time: %f" % ((sum(psa_time) / len(psa_time)) - psa_pre_time * rulenum /
                                len(prefix_rules))
    # print "Original average time: %f" % (sum(psa_time) / len(psa_time))
    print "-----------------------------------------------------------------------"

    print "Atomic2:"
    time1 = time.time()
    atom2_rule = predeal_atom2(range_rule)
    time2 = time.time()
    print "Pre-dealing time: %f" % (time2 - time1)
    atomic_time = list()
    for i in range(testnum):
        time1 = time.time()
        result = atom2_rule[testset[i][0][0]]
        for rule_action in testset[i][1:-1]:
            if rule_action[1]:
                result |= atom2_rule[rule_action[0]]
            else:
                result &= atom2_rule[rule_action[0]]
        time2 = time.time()
        atomic_time.append(time2 - time1)
    # print atomic_time
    print "Average time: %f" % (sum(atomic_time) / len(atomic_time))


def test_bench_mark(filename, testnum, pro):
    """

    :param filename:
    :return:
    """
    range_rule = pc.load_rules("./multi_rules/" + filename)

    # rules = load_CB_rules("../multi_rules/acl_1K/r0_1K")
    for singlerule in range_rule:
        for dims in range(5):
            prefix = pc.range2prefix(singlerule[dims], DIM_POINT_BITS[dims])
            if len(prefix) > 1:
                print "aho"
    print ""

    prefix_rule = list()
    for singlerule in range_rule:
        new_rule = list()
        for dims in range(5):
            new_rule.append(pc.range2prefix(singlerule[dims], DIM_POINT_BITS[dims]))
        prefix_rule.append(pc.prefix2wc(new_rule))

    testset = list()

    for i in range(testnum):
        singletestset = list()
        for j in range(len(range_rule)):
            singletestset.append(pick01withpro(pro))
            # 1 for or, 0 for and
        testset.append(singletestset)

    print "==============================================================================="
    print "Start the set operation test of benchmark ruleset " + filename
    print "Test number: %d" % testnum
    print "-----------------------------------------------------------------------"
    # Here start BDD
    print "BDD:"
    bdd1 = bdd.BDD()
    bdd2 = bdd.BDD()
    bdd3 = bdd.BDD()
    time1 = time.time()
    for single_rule in prefix_rule:
        bdd1.construct(single_rule)
        bdd1.clear()
    time2 = time.time()
    bdd_pre_time = time2 - time1
    print "Pre-dealing time: %f" % (time2 - time1)

    # In order to save the space, generate bdd every time to be added into final results;
    bdd_time = list()
    for i in range(testnum):
        bdd1.clear()
        bdd2.clear()
        bdd3.clear()
        time1 = time.time()
        bdd1.construct(prefix_rule[0])
        bdd2.construct(prefix_rule[1])
        if testset[i][0]:
            bdd3 = bdd3.apply_ite('|', bdd2, bdd1)
        else:
            bdd3 = bdd3.apply_ite('&', bdd2, bdd1)
        bdd3.reduce()
        totalnode = bdd3.nodenum
        maxnode = bdd3.nodenum
        for j in range(2, len(prefix_rule)):
            bdd1.construct(prefix_rule[j])
            if testset[i][j]:
                bdd3 = bdd3.apply_ite('|', bdd1, bdd3)
            else:
                bdd3 = bdd3.apply_ite('&', bdd1, bdd3)
            bdd3.reduce()
            totalnode += bdd3.nodenum
            if maxnode < bdd3.nodenum:
                maxnode = bdd3.nodenum
        time2 = time.time()
        bdd_time.append(time2 - time1)
        print "Average node num: %f" % (totalnode * 1.0 / len(prefix_rule))
        print "Max node num: %d" % maxnode
    print bdd_time
    print "Average time: %f" % ((sum(bdd_time) / len(bdd_time)) - bdd_pre_time)
    print "Original average time: %f" % (sum(bdd_time) / len(bdd_time))
    print "-----------------------------------------------------------------------"

    # Wildcard Expression
    print "wildcard:"
    wc_time = list()
    wc_test = headerspace(13)
    time1 = time.time()
    for single_rule in prefix_rule:
        wc_test = wildcard_create_from_string(single_rule)
    time2 = time.time()
    wc_pre_time = time2 - time1
    print "Pre-dealing time: %f" % (time2 - time1)
    # wc_list = predeal_wc(prefix_rules)

    for i in range(testnum):
        time1 = time.time()
        wc1 = headerspace(13)
        wc1.add_hs(wildcard_create_from_string(prefix_rule[0]))
        wc_max = wc1.hs_list.__len__()
        wc_num = wc_max
        for j in range(1, len(prefix_rule)):
            if testset[i][j]:
                wc1.add_hs(wildcard_create_from_string(prefix_rule[j]))
            else:
                wc1.intersect(wildcard_create_from_string(prefix_rule[j]))
            if wc1.hs_list:
                wc_num += len(wc1.hs_list)
                if wc_max < len(wc1.hs_list):
                    wc_max = len(wc1.hs_list)
        time2 = time.time()
        print "Average wc num: %f" % (wc_num * 1.0 / len(prefix_rule))
        print "Max wc num %d" % wc_max
        wc_time.append(time2 - time1)
    print wc_time
    print "Average time: %f" % ((sum(wc_time) / len(wc_time)) - wc_pre_time)
    print "Original average time: %f" % (sum(wc_time) / len(wc_time))
    print "-----------------------------------------------------------------------"

    # PSA test
    print "PSA:"
    psa_time = list()

    time1 = time.time()
    pca_list = predeal_psa(range_rule)
    time2 = time.time()
    psa_pre_time = time2 - time1
    print "Pre-dealing time: %f" % (time2 - time1)

    for i in range(testnum):
        time1 = time.time()
        hyrectset = PolicySpace([HyperRect(deepcopy(range_rule[0]))])
        hr_num = len(hyrectset.rects)
        hr_max = hr_num
        for j in range(1, len(range_rule)):
            if testset[i][j]:
                hyrectset.or_rect(HyperRect(deepcopy(range_rule[j])))
            else:
                hyrectset.and_rect(HyperRect(deepcopy(range_rule[j])))
            hr_num += len(hyrectset.rects)
            if hr_max < len(hyrectset.rects):
                hr_max = len(hyrectset.rects)
        time2 = time.time()
        print "Average hyperrect num: %f" % (hr_num * 1.0 / len(range_rule))
        print "Max: %d" % hr_max
        psa_time.append(time2 - time1)
    print psa_time
    print "Average time: %f" % ((sum(psa_time) / len(psa_time)) - psa_pre_time)
    print "Original average time: %f" % (sum(psa_time) / len(psa_time))
    print "-----------------------------------------------------------------------"

    print "Atomic2:"
    time1 = time.time()
    atom2_rule = predeal_atom2(range_rule)
    time2 = time.time()
    print "Pre-dealing time: %f" % (time2 - time1)
    atomic_time = list()
    for i in range(testnum):
        time1 = time.time()
        result = atom2_rule[0]
        for j in range(1, len(range_rule)):
            if testset[i][j]:
                result |= atom2_rule[j]
            else:
                result &= atom2_rule[j]
        time2 = time.time()
        atomic_time.append(time2 - time1)
    # print atomic_time
    print "Average time: %f" % (sum(atomic_time) / len(atomic_time))


# wcrules = wctorang.constructwcrule("./stanford/bbra_bdd_rule.txt")
# range_rule = wctorang.gentestrangerule(wcrules)
# for i in [50, 100, 200, 400, 600, 800, 990]:
#     segnum = list()
#     for dim in range(SF_DIM_NUM):
#         segnum.append(len(pc.shadow_rules(range_rule[:i], dim)) >> 1)
#     volume = reduce(mul, (segnum[d] for d in range(len(segnum))))
#     print "%d rules, volume: %d" % (i, volume)
#     time1 = time.time()
#     atom3_rule = predeal_atom2(range_rule[:i])
#     time2 = time.time()
#     print "pre-dealing time: %f" % (time2 - time1)

# test_simple_policy_intersect("bbra", 200, 5)
# test_simple_policy_intersect("bbrb", 200, 5)
# test_simple_policy_intersect("boza", 200, 5)
# test_simple_policy_intersect("bozb", 200, 5)
# test_simple_policy_intersect("goza", 200, 5)
# test_simple_policy_intersect("gozb", 200, 5)
# test_simple_policy_intersect("poza", 200, 5)
# test_simple_policy_intersect("pozb", 200, 5)
# test_simple_policy_intersect("roza", 200, 5)
# test_simple_policy_intersect("rozb", 200, 5)

# prefix_rules = bdd_rule.conwcrules("./stanford/bbra_bdd_rule.txt")
# predeal_bdd(prefix_rules)
# print "bdd done"
# predeal_wc(prefix_rules)
# print "wc done"
# wcrules = wctorang.constructwcrule("./stanford/bbra_bdd_rule.txt")
# range_rule = wctorang.gentestrangerule(wcrules)
# predeal_atom2(range_rule)
#
# predeal_psa(range_rule)

#test_simple_policy_intersect("bbra", 50, 1, 0)
test_bench_mark("acl_100/r0_100.txt", 1, 0.5)

