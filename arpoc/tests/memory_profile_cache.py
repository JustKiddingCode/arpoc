from pympler import asizeof

import arpoc.cache
import arpoc.utils

import hashlib
import random
import string

import time

c = arpoc.cache.Cache()

def fake_cache_entry():
    # three attributes: key, data, timestamp
    # data: state, valid_until, userinfo, scopes
    
    # key is hexdigest of sha256 hash
    key_origin =  ''.join([random.choice(string.ascii_letters) for n in range(500)])
    key = hashlib.sha256(key_origin.encode()).hexdigest()

    # data
    state = ''.join([random.choice(string.ascii_letters) for n in range(20)])
    scopes = ''.join([random.choice(string.ascii_letters) for n in range(30)])
    valid_until = arpoc.utils.now() + 500

    # make random userinfo
    claims = random.randint(1,50)
    userinfo = dict() 
    for i in range(claims):
        claim = ''.join([random.choice(string.ascii_letters) for n in range(10)])
        claim_value_size = random.randint(10,200)
        claim_value = ''.join([random.choice(string.ascii_letters) for n in range(claim_value_size)])
        userinfo[claim] = claim_value

    data = { 'state' : state, 'valid_until' : valid_until, 'userinfo' : userinfo, 'scopes' : scopes }

    valid = arpoc.utils.now() + 500

    return (key, data, valid)

for i in range(10001):
    c.put(*fake_cache_entry())
    if i % 1000 == 0:
        print(i)
        print(asizeof.asizeof(c))

#import pprint
#pprint.pprint(c.data)





