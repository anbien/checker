"""
Created by lichee


"""
from BDD import bdd
from BDD import bdd_rule
# from HSA.headerspace.tf import *
# from HSA.parser.cisco_router_parser import cisco_router


# cs = cisco_router(1)
# L = cs.hs_format["length"]
# tf = TF(L)
# tf.set_prefix_id("yozb_rtr")
# cs.read_arp_table_file("./data/Stanford_backbone/yozb_rtr_arp_table.txt")
# cs.read_mac_table_file("./data/Stanford_backbone/yozb_rtr_mac_table.txt")
# cs.read_config_file("./data/Stanford_backbone/yozb_rtr_config.txt")
# cs.read_spanning_tree_file("./data/Stanford_backbone/yozb_rtr_spanning_tree.txt")
# cs.read_route_file("./data/Stanford_backbone/yozb_rtr_route.txt")
# cs.optimize_forwarding_table()
# cs.generate_port_ids([])
# cs.generate_transfer_function(tf)
# tf.show_tf_in_file("show.txt")
# tf.write_bdd_rule("bdd_rule.txt")
bddrules = bdd_rule.constructbddrules("bdd_rule.txt")
bdd1 = bdd.BDD()
bdd2 = bdd.BDD()
bdd3 = bdd.BDD()
flag = False
rulesetnum = 0
for ruleset in bddrules.values():
    if len(ruleset) > 1:
        rulesetnum += 1
        print '\n'
        print "Start to apply ruleset %d:" % rulesetnum
        print "Total %d rules;" % len(ruleset)
        flag = True
        bdd1.construct(ruleset[0])
        bdd2.construct(ruleset[1])
        bdd3.clear()
        bdd3 = bdd3.apply_ite('|', bdd2, bdd1)
        bdd3.reduce()
        if len(ruleset) > 2:
            count = 0
            for rule in ruleset:
                print "\n%dth round;" % count
                count += 1
                if count < 2:
                    continue
                else:
                    bdd1.construct(rule)
                    bdd3 = bdd3.apply_ite('|', bdd1, bdd3)
                    bdd3.reduce()

    else:
        pass
