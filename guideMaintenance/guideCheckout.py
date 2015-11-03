import os
import json
#curl 'https://app.pendo.io/api/s/<subscription>/guide?includeArchived=true' -H 'accept: application/json, text/plain, */*'  -H 'cookie: pendo.sess=<sessionid>'  > /tmp/guide.json

guides = json.load(open('/tmp/guide.json', 'rb'))
for guide in guides:
    #if guide['state'] == u'staged':
    if "Pendo" in guide['name']:
        path = guide['id']
        if not os.path.exists(path):
            os.makedirs(path)
        for step in guide['steps']:
            stepId = step['id']
            content = step.pop('content')
            with open(os.path.join(path, "%s.meta" % stepId), 'w') as temp_file:
                temp_file.write(json.dumps(step))
            with open(os.path.join(path, "%s.content" % stepId), 'w') as temp_file:
                temp_file.write(content.encode('utf8'))
            
