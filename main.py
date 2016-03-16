# coding=utf-8
"""
By lichee

To use BDD MDD related algorithms to simplify routing table and ACLs

2016.3.5
"""
#import numpy as np
import pydot


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

    def __len(self):
        return self.nodenum

    def __delete(self, instance):
        self.nodelist.clear()
        #self.ordering.clear()

    def construct(self, s):
        """

        :param s:  '00X00101'
        :return:
        """
        #print 'Constructing, the string is %s'%s
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
            self.nodelist[1] = (self.varnum, False, -1)
            self.false = 1
        else:
            self.nodelist[0] = (first, 2, 1)
            self.nodelist[1] = (self.varnum, True, -1)
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
            self.nodelist[self.nextnode] = (self.level, False, -1)
            self.false = self.nextnode
        else:
            self.nodelist[self.nextnode] = (self.level, True, -1)
            self.true = self.nextnode
        self.nodenum += 1
        print self.nodelist


    def __op(self, op, oper1, oper2):
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
        self.__apply(op, bdd1, bdd2, 0, 0)


    def __apply(self, op, bdd1, bdd2, n1, n2):
        """

        :param op:
        :param bdd1:
        :param bbd2:
        :return: truple
        """
        thisnode = self.nextnode
        #print 'Generate %d node, with %d and %d th node of two bdd'%(thisnode, n1, n2)
        self.nextnode += 1
        bdd1node = bdd1.nodelist[n1]
        bdd2node = bdd2.nodelist[n2]
        #print 'bdd1node:'
        #print bdd1node
        #print 'bdd2node:'
        #print bdd2node
        if bdd1node[0] == bdd2node[0]:
            #print 'Same level;'
            if bdd1node[2] == -1:
                self.nodelist[thisnode] = (self.varnum,
                                           self.__op(op, bdd1node[1], bdd2node[1]),
                                           -1)
            else:
                self.nodelist[thisnode] = (bdd1node[0],
                                           self.__apply(op, bdd1, bdd2, bdd1node[1], bdd2node[1]),
                                           self.__apply(op, bdd1, bdd2, bdd1node[2], bdd2node[2]))
        elif bdd1node[0] > bdd2node[0]:
            #print 'Different level, 2 higher than 1;'
            if bdd1node[2] == -1:
                if not bdd1node[1]:  #bdd1's node is false
                    if op in ('&', 'and'):
                        #print 'No need to cal deeper;'
                        self.nodelist[thisnode] = (self.varnum, False, -1)
                    else:  #suppose we never use xor
                        #print 'copy the rest of bdd2;'
                        self.nodelist[thisnode] = (bdd2node[0],
                                           self.__apply(op, bdd1, bdd2, n1, bdd2node[1]),
                                           self.__apply(op, bdd1, bdd2, n1, bdd2node[2]))
                    #TODO:still need to implement xor

                else:  #bdd2's node is true
                    if op in ('|', 'or'):
                        #print 'No need to cal deeper;'
                        self.nodelist[thisnode] = (self.varnum, True, -1)
                    else: #suppose we never use xor
                        #print 'copy the rest of bdd2'
                        #TODO: FIND A SMARTER WAY TO DO THE COPY
                        self.nodelist[thisnode] = (bdd2node[0],
                                           self.__apply(op, bdd1, bdd2, n1, bdd2node[1]),
                                           self.__apply(op, bdd1, bdd2, n1, bdd2node[2]))

            else:
                self.nodelist[thisnode] = (bdd2node[0],
                                           self.__apply(op, bdd1, bdd2, n1, bdd2node[1]),
                                           self.__apply(op, bdd1, bdd2, n1, bdd2node[2]))
        else:
            if bdd2node[2] == -1:
                if not bdd2node[1]:  #bdd2's node is false
                    if op in ('&', 'and'):
                        self.nodelist[thisnode] = (self.varnum, False, -1)
                    else:  #suppose we never use xor
                        self.nodelist[thisnode] = (bdd1node[0],
                                                   self.__apply(op, bdd1, bdd2, bdd1node[1], n2),
                                                   self.__apply(op, bdd1, bdd2, bdd1node[2], n2))
                    #TODO:still need to implement xor

                else: #bdd2's node is true
                    if op in ('|', 'or'):
                        self.nodelist[thisnode] = (self.varnum, True, -1)
                    else: #suppose we never use xor
                        self.nodelist[thisnode] = (bdd1node[0],
                                                   self.__apply(op, bdd1, bdd2, bdd1node[1], n2),
                                                   self.__apply(op, bdd1, bdd2, bdd1node[2], n2))
                    #TODO:still need to implement xor

            else:
                self.nodelist[thisnode] = (bdd1node[0],
                                           self.__apply(op, bdd1, bdd2, bdd1node[1], n2),
                                           self.__apply(op, bdd1, bdd2, bdd1node[2], n2))

        self.nodenum = self.nextnode
        return thisnode


    def reduce(self):
        """

        :return:
        """
        print 'Total %d nodes before reduce, they are:'%self.nodenum
        #记录每层的节点 nodesOnlevel[i][j] 第i层的第j个节点
        nodesOnLevel = dict()  #record nodes number on the same level

        #唯一性节点,唯一的value与nodesnumber对应
        uniquevalue = dict()    #record unique node number  (false, -1) = 1

        #每个节点的value值:
        valueofnodes = dict()

        #需要被替换的节点
        nodeswitch = dict()   #replace some node

        deadnode = set()
        for i in xrange(self.varnum + 1):
            nodesOnLevel[i] = list()
        for i in xrange(self.nodenum):
            nodesOnLevel[self.nodelist[i][0]].append(i)

        print self.nodelist
        print self.varnum
        print ''
        last = self.varnum
        nextvalue = 1

        #对于最后一层,由于不存在子节点相同的情况,所以只加入不重复的就好
        for j in xrange(len(nodesOnLevel[last])):
            if self.nodelist[nodesOnLevel[last][j]][1:3] in uniquevalue:
                nodeswitch[nodesOnLevel[last][j]] = uniquevalue[self.nodelist[nodesOnLevel[last][j]][1:3]]
                deadnode.add(nodesOnLevel[last][j])
                valueofnodes[nodesOnLevel[last][j]] = uniquevalue[self.nodelist[nodesOnLevel[last][j]][1:3]]
            else:
                uniquevalue[self.nodelist[nodesOnLevel[last][j]][1:3]] = nodesOnLevel[last][j]
                nodeswitch[nodesOnLevel[last][j]] = nodesOnLevel[last][j]
                valueofnodes[nodesOnLevel[last][j]] = nextvalue
                nextvalue += 1

        print 'After first level:'
        print uniquevalue
        print valueofnodes
        print ''

        for i in xrange(self.varnum - 1, -1, -1):  #for each level except the lowest level:
            print 'Level %d;'%i
            for j in xrange(len(nodesOnLevel[i])):  #for each node on this level:
                print 'Identifying node %d'%nodesOnLevel[i][j]
                print self.nodelist[nodesOnLevel[i][j]]
                if (valueofnodes[self.nodelist[nodesOnLevel[i][j]][1]] ==
                        valueofnodes[self.nodelist[nodesOnLevel[i][j]][2]]):
                    valueofnodes[nodesOnLevel[i][j]] = valueofnodes[self.nodelist[nodesOnLevel[i][j]][2]]
                    nodeswitch[nodesOnLevel[i][j]] = nodeswitch[self.nodelist[nodesOnLevel[i][j]][2]]
                    deadnode.add(nodesOnLevel[i][j])
                else:
                    valueofnodes[nodesOnLevel[i][j]] = (valueofnodes[self.nodelist[nodesOnLevel[i][j]][1]],
                                                        valueofnodes[self.nodelist[nodesOnLevel[i][j]][2]])
                    if valueofnodes[nodesOnLevel[i][j]] in uniquevalue:
                        nodeswitch[nodesOnLevel[i][j]] = uniquevalue[valueofnodes[nodesOnLevel[i][j]]]
                        deadnode.add(nodesOnLevel[i][j])
                    else:
                        uniquevalue[valueofnodes[nodesOnLevel[i][j]]] = nodesOnLevel[i][j]

        print 'nodes on level:'
        print nodesOnLevel
        print 'num of nodes:'
        print uniquevalue
        print 'node list after reduce:'
        print nodeswitch
        print 'dead nodes:'
        print deadnode
        print ''
        count = 0
        for i in xrange(self.nodenum):
            if i in deadnode:
                pass
            else:
                nodeswitch[i] = count
                count += 1

        #重新生成节点
        newnodelist = self.nodelist.copy()
        for i in xrange(self.nodenum):
            if self.nodelist[i][2] != -1:
                newnodelist[i] = (self.nodelist[i][0], nodeswitch[self.nodelist[i][1]], nodeswitch[self.nodelist[i][2]])
        print newnodelist
        for i in deadnode:
            newnodelist.pop(i)
        print newnodelist
        self.nodenum = len(newnodelist)
        self.nodelist.clear()
        print newnodelist
        count = 0
        for i in newnodelist.values():
            self.nodelist[count] = i
            count += 1
        print self.nodelist

    def dump(self, filename, filetype = None, **kw):
        """
        Write BDDs to 'filename'.

        At present we only support pdf and png
        :param filename:
        :param filetype:
        :param kw:
        :return:
        """
        if filetype is None:
            name = filename.lower()
            if name.endswith('.pdf'):
                filetype = 'pdf'
            elif name.endswith('.png'):
                filetype = 'png'
            else:
                raise Exception(
                    'cannot infer file type '
                    'from extension')
        if filetype in ('pdf', 'png'):
            self._dump_figure(filename, filetype, **kw)
        else:
            raise Exception(
                'unknown file type "{t}"'.format(
                    t=filetype))

    def _dump_figure(self, filename, filetype, **kw):
        """

        :param filename:
        :param filetype:
        :param kw:
        :return:
        """
        print self.nodenum
        print filename
        print filetype

        graph = pydot.Dot(graph_type = 'digraph')
        for i in xrange(self.nodenum):
            node = pydot.Node(str(i))
            graph.add_node(node)
        for i in xrange(self.nodenum):
            if self.nodelist[i][2] != -1:
                graph.add_edge(pydot.Edge(str(i), str(self.nodelist[i][1])))
                graph.add_edge(pydot.Edge(str(i), str(self.nodelist[i][2])))
        graph.write_pdf('bdd.pdf')


bdd1 = BDD()
bdd2 = BDD()
bdd = BDD()

bdd1.construct('11101')
bdd2.construct('11111')

bdd.apply('|', bdd1, bdd2)
bdd.reduce()
bdd.dump('bdd.pdf')
