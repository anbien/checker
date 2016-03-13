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
        self.nodenum = 2

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
                self.nodenum += 1
                self.nodelist[self.nextnode - 1] = (self.level, self.false, self.nextnode)

            elif bit == '0':
                #print '%d th level is %s'%(self.level, '0')
                self.nextnode += 1
                self.nodenum += 1
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
        self.nodenum += 1
        print self.nodelist

    def __op__(self, op, oper1, oper2):
        """

        :param op:
        :param oper1:
        :param oper2:
        :return:
        """
        if op in ('|', 'or'):
            return oper1 | oper2
        elif op in ('&', 'and'):
            return oper1 & oper2
        elif op in ('^', 'xor'):
            return oper1 ^ oper2
        else:
            raise Exception('unknown operator "{op}"'.format(op = op))

    def apply(self, op, bdd1, bdd2):
        """

        :param op:
        :param bdd1:
        :param bdd2:
        :return:
        """
        self.varnum = bdd1.varnum
        self.__apply__(op, bdd1, bdd2, 0, 0)

    def __apply__(self, op, bdd1, bdd2, n1, n2):
        """

        :param op:
        :param bdd1:
        :param bbd2:
        :return: truple
        """
        thisnode = self.nextnode
        print 'Generate %d node, with %d and %d th node of two bdd'%(thisnode, n1, n2)
        self.nextnode += 1
        bdd1node = bdd1.nodelist[n1]
        bdd2node = bdd2.nodelist[n2]
        print 'bdd1node:'
        print bdd1node
        print 'bdd2node:'
        print bdd2node
        if bdd1node[0] == bdd2node[0]:
            print 'Same level;'
            if len(bdd1node) == 2:
                self.nodelist[thisnode] = (self.varnum,
                                           self.__op__(op, bdd1node[1], bdd1node[1]))
            else:
                self.nodelist[thisnode] = (bdd1node[0],
                                           self.__apply__(op, bdd1, bdd2, bdd1node[1], bdd2node[1]),
                                           self.__apply__(op, bdd1, bdd2, bdd1node[2], bdd2node[2]))
        elif bdd1node[0] > bdd2node[0]:
            print 'Different level, 2 higher than 1;'
            if not bdd1node[2]:
                if not bdd1node[1]:
                    if op in ('&', 'and'):
                        print 'No need to cal deeper;'
                        self.nodelist[thisnode] = (self.varnum, False)
                    else:  #suppose we never use xor
                        print 'copy the rest of bdd2;'
                        self.nodelist[thisnode] = (bdd2node[0],
                                           self.__apply__(op, bdd1, bdd2, n1, bdd2node[1]),
                                           self.__apply__(op, bdd1, bdd2, n1, bdd2node[2]))
                    #TODO:still need to implement xor

                else:
                    if op in ('|', 'or'):
                        print 'No need to cal deeper;'
                        self.nodelist[thisnode] = (self.varnum, True)
                    else: #suppose we never use xor
                        #print 'copy the rest of bdd2'
                        #TODO: FIND A SMARTER WAY TO DO THE COPY
                        self.nodelist[thisnode] = (bdd2node[0],
                                           self.__apply__(op, bdd1, bdd2, n1, bdd2node[1]),
                                           self.__apply__(op, bdd1, bdd2, n1, bdd2node[2]))

            else:
                self.nodelist[thisnode] = (bdd2node[0],
                                           self.__apply__(op, bdd1, bdd2, n1, bdd2node[1]),
                                           self.__apply__(op, bdd1, bdd2, n1, bdd2node[2]))
        else:
            if len(bdd2node):
                if not bdd2node[1]:
                    if op in ('&', 'and'):
                        self.nodelist[thisnode] = (self.varnum, False)
                    else:  #suppose we never use xor
                        self.nodelist[thisnode] = (bdd1node[0],
                                                   self.__apply__(op, bdd1, bdd2, bdd1node[1], n2),
                                                   self.__apply__(op, bdd1, bdd2, bdd1node[2], n2))
                    #TODO:still need to implement xor

                else:
                    if op in ('|', 'or'):
                        self.nodelist[thisnode] = (self.varnum, True)
                    else: #suppose we never use xor
                        self.nodelist[thisnode] = (bdd1node[0],
                                                   self.__apply__(op, bdd1, bdd2, bdd1node[1], n2),
                                                   self.__apply__(op, bdd1, bdd2, bdd1node[2], n2))
                    #TODO:still need to implement xor

            else:
                self.nodelist[thisnode] = (bdd1node[0],
                                           self.__apply__(op, bdd1, bdd2, bdd1node[1], n2),
                                           self.__apply__(op, bdd1, bdd2, bdd1node[2], n2))

        return thisnode


bdd1 = BDD()
bdd2 = BDD()
bdd = BDD()

bdd1.construct('11X1')
bdd2.construct('111X')

bdd.apply('&', bdd1, bdd2)
pass