"""
By lichee

To use BDD MDD related algorithms to simplify routing table and ACLs

2016.3.5
"""
#import numpy as np

class BDD(object):
    """Ordered binary decision diagram

    """

    def __init__(self):
        self.s = ''
        self.nodelist = dict()
        self.nextnode = 0
        #self.ordering = dict()
        self.nodenum = 0   #node number!
        self.varnum = 0    #var number!
        self.level = 0
        self.false = 0
        self.true = 0

    def __len__(self):
        return self.nodenum

    def __delete__(self, instance):
        self.nodelist.clear()
        #self.ordering.clear()

    def construct(self, s):
        """

        :param s:  '00X00101'
        :return:
        """
        print 'Constructing, the string is %s'%s
        self.s = s
        self.varnum = s.__len__()
        first = -1
        for bit in s:
            if bit != 'X':
                first += 1
                #print first
                break
            first += 1

        if s[first] == '1':
            self.nodelist[0] = (first, 1, 2)
            self.nodelist[1] = (self.varnum, False)
            self.false = 1
        else:
            self.nodelist[0] = (first, 2, 1)
            self.nodelist[1] = (self.varnum, True)
            self.true = 1

        #print self.nodelist
        #print '\n'
        self.level = first + 1
        self.nextnode = 2

        for bit in s[first + 1:]:
            if bit == 'X':
                #print '%d th level is void. Switch to next level'%(self.level)
                pass

            elif bit == '1':
                #print '%d th level is %s'%(self.level, '1')
                self.nextnode += 1
                self.nodelist[self.nextnode - 1] = (self.level, self.false, self.nextnode)

            elif bit == '0':
                #print '%d th level is %s'%(self.level, '0')
                self.nextnode += 1
                self.nodelist[self.nextnode - 1] = (self.level, self.nextnode, self.false)

            else:
                print 'Invaild initial param'
                return False
            self.level += 1
            #print self.nodelist
            #print '\n'
        if self.true == 1:
            self.nodelist[self.nextnode] = (self.level, False)
            self.false = self.nextnode
        else:
            self.nodelist[self.nextnode] = (self.level, True)
            self.true = self.nextnode
        print self.nodelist

    def apply(self, op, bdd1, bdd2):
        """

        :param op:
        :param bdd1:
        :param bdd2:
        :return:
        """
        self.varnum = bdd1.varnum
        value = self.__apply__(op, bdd1, bdd2, 0, 0)
        self.nodelist[0] = value

    def __apply__(self, op, bdd1, bbd2, n1, n2):
        """

        :param op:
        :param bdd1:
        :param bbd2:
        :return: truple
        """
        stack = list()
        flag = list()
        stack.append((0, 0, 0))  #(nodenum, bdd1where, bdd2where)
        flag[0] = 0
        node_bdd1 = bdd1.nodelist[0]
        node_bdd2 = bdd2.nodelist[0]
        if node_bdd1[0] == node_bdd2[0]:
            stack.append((1, node_bdd1[2], node_bdd2[2]))
            stack.append((2, node_bdd1[1], node_bdd2[1]))

        while stack:

            print stack
            if flag[stack[-1][0]] == 2:
                stack.pop()



bdd1 = BDD()
bdd2 = BDD()
bdd = BDD()

bdd1.construct('11X1')
bdd2.construct('111X')

bdd.apply('&', bdd1, bdd2)