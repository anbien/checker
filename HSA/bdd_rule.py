from headerspace.tf import *
from parser.cisco_router_parser import cisco_router

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
    newrlue = False
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
                    bddrules[(inport, outport)] = set()
                bddrules[(inport, outport)].add(match)
    return bddrules

if __name__ == "__main__":
    cs = cisco_router(1)
    L = cs.hs_format["length"]
    tf = TF(L)
    tf.set_prefix_id("yozb_rtr")
    cs.read_arp_table_file("../data/Stanford_backbone/yozb_rtr_arp_table.txt")
    cs.read_mac_table_file("../data/Stanford_backbone/yozb_rtr_mac_table.txt")
    cs.read_config_file("../data/Stanford_backbone/yozb_rtr_config.txt")
    cs.read_spanning_tree_file("../data/Stanford_backbone/yozb_rtr_spanning_tree.txt")
    cs.read_route_file("../data/Stanford_backbone/yozb_rtr_route.txt")
    cs.optimize_forwarding_table()
    cs.generate_port_ids([])
    cs.generate_transfer_function(tf)
    tf.show_tf_in_file("show.txt")
    bddrules = constructbddrules("bdd_rule.txt")