"""
Created by lichee


"""
import bdd


# test of BDD
bdd1 = bdd.BDD()
bdd2 = bdd.BDD()
bdd3 = bdd.BDD()

bdd1.construct('1110')
bdd2.construct('1111')

bdd3.apply('|', bdd1, bdd2)
bdd3.reduce()
bdd3.dump('bdd.png')
