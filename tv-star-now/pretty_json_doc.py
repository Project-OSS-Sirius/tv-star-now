#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json

for line in sys.stdin:
    jsonDict = json.loads(line.strip())
    prettyJson = json.dumps(jsonDict, ensure_ascii=False, indent=2)
    sys.stdout.write("{}\n".format(prettyJson))

