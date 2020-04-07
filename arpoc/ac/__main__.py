import json
import sys

import arpoc.ac as ac

if len(sys.argv) == 3:
    rule_txt = sys.argv[1]
    context = json.loads(sys.argv[2])
    ac.Rule
    rule_obj = ac.Rule(
        'test',
        'True',
        'Test incoming rule',
        [],
        rule_txt,
        'GRANT',
    )
    print(rule_obj.evaluate(context))
