# coding=utf-8
"""
By lichee

To use BDD MDD related algorithms to simplify routing table and ACLs

2016.3.5
"""
import pydot


class BDD(object):
    """Ordered binary decision diagram

    """

    def __init__(self):
        self.nodelist = dict()
        self.nextnode = 0
        # self.ordering = dict()
        self.nodenum = 0   # node number!
        self.varnum = 0    # var number!
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

        # print self.nodelist
        # print '\n'
        self.level = first + 1
        self.nextnode = 2

        for bit in s[first + 1:]:
            if bit == 'X':
                # print '%d th level is void. Switch to next level'%(self.level)
                pass

            elif bit == '1':
                # print '%d th level is %s'%(self.level, '1')
                self.nextnode += 1
                self.nodenum += 1
                self.nodelist[self.nextnode - 1] = (self.level, self.false, self.nextnode)

            elif bit == '0':
                # print '%d th level is %s'%(self.level, '0')
                self.nextnode += 1
                self.nodenum += 1
                self.nodelist[self.nextnode - 1] = (self.level, self.nextnode, self.false)

            else:
                print 'Invaild initial param'
                return False
            self.level += 1
            # print self.nodelist
            # print '\n'
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
        :param bdd2:
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

        #唯一性节点,唯一的value组和nodesnum的对应
        uniquevalue = dict()    #record unique node number  (false, -1) = 1

        #每个节点的value值:
        valueofnodes = dict()

        #需要被替换的节点
        nodeswitch = dict()

        #需要被删除的节点
        deadnode = set()

        for i in xrange(self.varnum + 1):
            nodesOnLevel[i] = list()
        for i in xrange(self.nodenum):
            nodesOnLevel[self.nodelist[i][0]].append(i)

        print self.nodelist
        print self.varnum
        print ''
        last = self.varnum
        nextvalue = 3
        falseflag = False
        trueflag = False
        #对于最后一层,由于不存在子节点相同的情况,所以只加入不重复的就好
        for j in xrange(len(nodesOnLevel[last])):
            if self.nodelist[nodesOnLevel[last][j]][1] is False:
                valueofnodes[nodesOnLevel[last][j]] = 1
                if falseflag is False:
                    falseflag = nodesOnLevel[last][j]
                    nodeswitch[nodesOnLevel[last][j]] = nodesOnLevel[last][j]
                    uniquevalue[1] = (1, falseflag)
                else:
                    nodeswitch[nodesOnLevel[last][j]] = falseflag
                    deadnode.add(nodesOnLevel[last][j])
            else:
                valueofnodes[nodesOnLevel[last][j]] = 2
                if trueflag is False:
                    trueflag = nodesOnLevel[last][j]
                    nodeswitch[nodesOnLevel[last][j]] = nodesOnLevel[last][j]
                    uniquevalue[2] = (2, trueflag)
                else:
                    nodeswitch[nodesOnLevel[last][j]] = trueflag
                    deadnode.add(nodesOnLevel[last][j])

        print 'After first level:'
        print uniquevalue
        print valueofnodes
        print nodeswitch
        print ''

        for i in xrange(self.varnum - 1, -1, -1):  #for each level except the lowest level:
            print 'Level %d;'%i
            for j in xrange(len(nodesOnLevel[i])):  #for each node on this level:
                nodenum = nodesOnLevel[i][j]
                print 'Identifying node %d'%nodenum
                print self.nodelist[nodenum]
                if (valueofnodes[self.nodelist[nodenum][1]] ==
                        valueofnodes[self.nodelist[nodenum][2]]):
                    print "Two child of this node have same value, so this node's value is:"
                    valueofnodes[nodenum] = valueofnodes[self.nodelist[nodenum][2]]
                    print valueofnodes[nodenum]
                    nodeswitch[nodenum] = nodeswitch[self.nodelist[nodenum][2]]
                    deadnode.add(nodenum)

                else:
                    valueofnodes[nodenum] = \
                        (uniquevalue[valueofnodes[self.nodelist[nodenum][1]]][0],
                         uniquevalue[valueofnodes[self.nodelist[nodenum][2]]][0])
                    print "Two child have different value, so new value is:"
                    print valueofnodes[nodenum]
                    if valueofnodes[nodenum] in uniquevalue:
                        print "There is already some nodes with this value:"
                        nodeswitch[nodenum] = uniquevalue[valueofnodes[nodenum]]
                        deadnode.add(nodenum)
                    else:
                        print "New value, with number %d"%nextvalue
                        uniquevalue[valueofnodes[nodenum]] = (nextvalue, nodenum)
                        nodeswitch[nodenum] = nodenum
                        nextvalue += 1

        print 'nodes on level:'
        print nodesOnLevel
        print 'num of nodes:'
        print uniquevalue
        print 'node list after reduce:'
        print nodeswitch
        print 'dead nodes:'
        print deadnode
        print ''

        for i in deadnode:
            self.nodelist.pop(i)
        print 'After cut, node list is:'
        print self.nodelist

        for i in self.nodelist:
            if self.nodelist[i][2] != -1:
                self.nodelist[i] = (self.nodelist[i][0], nodeswitch[self.nodelist[i][1]],
                                    nodeswitch[self.nodelist[i][2]])

        print 'After switch, node list is:'
        print self.nodelist

        nodeswitch.clear()
        count = 0
        for i in self.nodelist:
            nodeswitch[i] = count
            count += 1
        count = 0
        newnodelist = self.nodelist.copy()
        self.nodelist.clear()
        for i in newnodelist:
            if newnodelist[i][2] != -1:
                self.nodelist[count] = (newnodelist[i][0], nodeswitch[newnodelist[i][1]],
                                    nodeswitch[newnodelist[i][2]])
            else:
                self.nodelist[count] = newnodelist[i]
            count += 1
        print 'Final node list:'
        print self.nodelist
        self.nodenum = len(self.nodelist)

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
        graph = pydot.Dot(graph_type='digraph')
        subgraph = dict()
        skeleton = list()
        for i in xrange(self.varnum + 1):
            h = pydot.Subgraph('', rank='same')
            graph.add_subgraph(h)
            subgraph[i] = h
            u = '-{i}'.format(i=i)
            skeleton.append(u)
            nd = pydot.Node(name=u, label='level' + str(i), shape='none')
            h.add_node(nd)
        for i, u in enumerate(skeleton[:-1]):
            v = skeleton[i + 1]
            e = pydot.Edge(str(u), str(v), style='invis')
            graph.add_edge(e)
        for i in xrange(self.nodenum):
            if self.nodelist[i][2] != -1:
                node = pydot.Node(str(i))
            else:
                if self.nodelist[i][1] is False:
                    node = pydot.Node("False")
                else:
                    node = pydot.Node("True")
            graph.add_node(node)
            h = subgraph[self.nodelist[i][0]]
            h.add_node(node)

        for i in xrange(self.nodenum):
            if self.nodelist[i][2] != -1:
                if self.nodelist[self.nodelist[i][1]][2] == -1:
                    edge = pydot.Edge(str(i), str(self.nodelist[self.nodelist[i][1]][1]),
                                      label="0", style='dashed')
                else:
                    edge = pydot.Edge(str(i), str(self.nodelist[i][1]),
                                      label="0", style='dashed')
                graph.add_edge(edge)
                if self.nodelist[self.nodelist[i][2]][2] == -1:
                    edge = pydot.Edge(str(i), str(self.nodelist[self.nodelist[i][2]][1]),
                                      label="1", style='solid')
                else:
                    edge = pydot.Edge(str(i), str(self.nodelist[i][2]),
                                      label="1", style='solid')
                graph.add_edge(edge)
        graph.write_pdf('bdd.pdf')


bdd1 = BDD()
bdd2 = BDD()
bdd = BDD()

bdd1.construct('1110')
bdd2.construct('1111')

bdd.apply('|', bdd1, bdd2)
bdd.reduce()
bdd.dump('bdd.pdf')
