"""
Created by lichee


"""
import bdd
from config_parser import cisco_router_parser

h = cisco_router_parser.cisco_router(1)
# test of BDD
bdd1 = bdd.BDD()
bdd2 = bdd.BDD()
bdd3 = bdd.BDD()

bdd1.construct('1111X101')
bdd2.construct('11X1X111')
bdd3.apply('|', bdd1, bdd2)
bdd3.reduce()
bdd3.dump('bdd3.png')
bdd2.dump('bdd2.png')
bdd1.dump('bdd1.png')
