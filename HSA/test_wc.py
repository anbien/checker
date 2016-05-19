
from utils.wildcard import *
from headerspace.hs import *

if __name__ == "__main__":
    wc1 = wildcard_create_from_string("0x101111")
    wc2 = wildcard_create_from_string("1x10xx11")
    wc3 = wildcard_and(wc1, wc2)
    wc3 = wildcard_or(wc1, wc2)
    wc3 = wildcard_not(wc1)
    wc3 = wildcard_intersect(wc1, wc2)
    wc4 = wildcard_complement(wc1)
    wc5 = wildcard_diff(wc1, wc2)
    print wildcard_to_str(wc3)
    print wildcard_to_str(wc4)
