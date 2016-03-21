"""
Created by lichee


"""
import bdd


# test of BDD
bdd1 = bdd.BDD()
bdd2 = bdd.BDD()
bdd3 = bdd.BDD()

bdd1.construct('1111X')
bdd2.construct('11X1X')
bdd3.apply('|', bdd1, bdd2)
bdd3.reduce()
bdd3.dump('bdd3.png')
bdd2.dump('bdd2.png')
bdd1.dump('bdd1.png')
