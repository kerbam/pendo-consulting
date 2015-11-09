import sys

import os
import json
#curl 'https://app.pendo.io/api/s/<subscription>/guide?includeArchived=true' -H 'accept: application/json, text/plain, */*'  -H 'cookie: pendo.sess=<sessionid>'  > /tmp/guide.json

guides = json.load(open('/tmp/guide.json', 'rb'))

guideId = False

if len(sys.argv) > 1:
    guideId = sys.argv[1]

foundOne = False

for guide in guides:
    checkout = False
    if guideId == "ALL":
        checkout = True
    elif guide['id'] == guideId:
        checkout = True
    if checkout:
        foundOne = True
        print "processing guide %s name = %s" % (guide['id'], guide['name'])
        path = guide['id']
        if not os.path.exists(path):
            os.makedirs(path)
        stepnum = 0
        for step in guide['steps']:
            stepnum = stepnum + 1
            stepId = step['id']
            content = step.pop('content')
            with open(os.path.join(path, "s-%04d-%s.meta" % (stepnum, stepId)), 'w') as temp_file:
                temp_file.write(json.dumps(step))
            with open(os.path.join(path, "s-%04d-%s.html" % (stepnum, stepId)), 'w') as temp_file:
                temp_file.write(content.encode('utf8'))
        guide.pop('steps', None)
        with open(os.path.join(path, "guide.meta"), 'w') as temp_file:
            temp_file.write(json.dumps(guide))
        
    elif not guideId:
        print "ignoring guide %s name = %s" % (guide['id'], guide['name'])

if foundOne == False:
    print "warning: never found guide matching ID %s" % guideId
