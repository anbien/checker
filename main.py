"""
Created by lichee


"""
import time

from HSA.headerspace.tf import *
from HSA.parser.cisco_router_parser import cisco_router
from BDD import bdd
from BDD import bdd_rule
from PSA.policyspace import PolicySpace
from PSA.policyspace import HyperRect
from PSA import wctorang

def pre_deal(router):
    cs = cisco_router(1)
    L = cs.hs_format["length"]
    tf = TF(L)
    tf.set_prefix_id(router + "_rtr")
    cs.read_arp_table_file("./data/Stanford_backbone/" + router + "_rtr_arp_table.txt")
    cs.read_mac_table_file("./data/Stanford_backbone/" + router + "_rtr_mac_table.txt")
    cs.read_config_file("./data/Stanford_backbone/" + router + "_rtr_config.txt")
    cs.read_spanning_tree_file("./data/Stanford_backbone/" + router + "_rtr_spanning_tree.txt")
    cs.read_route_file("./data/Stanford_backbone/" + router + "_rtr_route.txt")
    cs.optimize_forwarding_table()
    cs.generate_port_ids([])
    return [cs, tf]

routername = ["bbra", "bbrb", "boza", "bozb",
              "coza", "cozb", "goza", "gozb",
              "poza", "pozb", "roza", "rozb",
              "soza", "sozb", "yoza", "yozb"]
bddlog = open("./BDD.log", "w")
bddlog.write("===================================================")
bddlog.close()

for router in routername:
    # pre dealing
    cs_tf = pre_deal(router)

    # HSA
    print "Now test with router " + router
    time1 = time.time()
    print "HSA Time: "
    cs_tf[0].generate_transfer_function(cs_tf[1])
    time2 = time.time()
    print time2 - time1
    cs_tf[1].write_bdd_rule("bdd_rule.txt")

    # Here start BDD
    print "\nBDD Time: "
    bddrules = bdd_rule.constructbddrules("bdd_rule.txt")
    bdd1 = bdd.BDD()
    bdd2 = bdd.BDD()
    bdd3 = bdd.BDD()
    flag = False
    bddlog = open("./BDD.log", "a+")
    bddlog.write("\nNow router : " + router)
    rulesetnum = 0
    time1 = time.time()
    for ruleset in bddrules.values():
        if len(ruleset) > 1:
            rulesetnum += 1
            bddlog.write("\n")
            bddlog.write("Start to apply ruleset %d:" % rulesetnum)
            bddlog.write("Total %d rules;" % len(ruleset))
            flag = True
            bdd1.construct(ruleset[0])
            bdd2.construct(ruleset[1])
            bdd3.clear()
            bdd3 = bdd3.apply_ite('|', bdd2, bdd1)
            bdd3.reduce()
            if len(ruleset) > 2:
                count = 0
                for rule in ruleset:
                    count += 1
                    if count < 2:
                        continue
                    else:
                        bdd1.construct(rule)
                        bdd3 = bdd3.apply_ite('|', bdd1, bdd3, bddlog)
                        bdd3.reduce(bddlog)
    bddlog.close()
    time2 = time.time()
    print time2 - time1

    # PSA time
    print "\nPSA Time: "
    wcrules = wctorang.constructwcrule("./bdd_rule.txt")
    time1 = time.time()
    rangerule = wctorang.wcruletorangerule(wcrules)
    hyrectset = dict()
    for ruleindex in rangerule:
        hyrectset[ruleindex] = PolicySpace([HyperRect(rangerule[ruleindex][0])])
        for rule in rangerule[ruleindex][1:]:  # rangerule[] is a policy
            hyrectset[ruleindex].or_rect(HyperRect(rule))
    time2 = time.time()
    print time2 - time1
    print ""


