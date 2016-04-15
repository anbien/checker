# By Lichee
# For checker project
# This file contains the self-made function to transfer wildcard expression into ranges;

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

def cisco_router_format():
    format = {}
    format["vlan_pos"] = 0
    format["ip_src_pos"] = 2
    format["ip_dst_pos"] = 6
    format["ip_proto_pos"] = 10
    format["transport_src_pos"] = 11
    format["transport_dst_pos"] = 13
    format["transport_ctrl_pos"] = 15
    format["vlan_len"] = 2
    format["ip_src_len"] = 4
    format["ip_dst_len"] = 4
    format["ip_proto_len"] = 1
    format["transport_src_len"] = 2
    format["transport_dst_len"] = 2
    format["transport_ctrl_len"] = 1
    format["length"] = 16
    return format

def splitmatch(rule):
    """

    :param rule:
    :return:
    """
    splitrule = dict()
    tokens = rule.split(',')
    splitrule['tran_ctrl'] = tokens[0]
    splitrule['tran_dst'] = tokens[1] + tokens[2]
    splitrule['tran_src'] = tokens[3] + tokens[4]
    splitrule['ip_pro'] = tokens[5]
    splitrule['ip_dst'] = tokens[6] + tokens[7] + tokens[8] + tokens[9]
    splitrule['ip_src'] = tokens[10] + tokens[11] + tokens[12] + tokens[13]
    splitrule['vlan'] = tokens[14] + tokens[15]
    return splitrule


def wildcard2range(length, wildcard):
    """

    :param length:
    :param wildcard:
    :return:
    """
    ranges = list()

    return ranges


def wcruletorangerule(wcrules):
    """

    :return:
    """
    rangerule = dict()
    for ruleset in wcrules:
        rangerule[ruleset] = list()
        for rule in wcrules[ruleset]:
            splitrule = splitmatch(rule)
            print splitrule
            for value in splitrule.values():


if __name__ == "__main__":

    # test of wc to range
    wcrules = constructwcrule("../bdd_rule.txt")



