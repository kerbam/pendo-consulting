#!/bin/python
import csv, json, requests
metaArray = []
visitorSet = set()
with open ('/tmp/visitors.csv', 'rU') as csvfile:
    visitors = csv.reader(csvfile)
    for row in visitors:
        visitorSet.add(row[2])
for visitor in visitorSet:
    metaArray.append({'visitorId':visitor, "values":{"CUSTOM FIELD NAME HERE": True}})

def getRealVisitors(visitors):
    filter = "visitorId == \\\"%s\\\"" % '\\\" || visitorId == \\\"'.join(visitors)
    aggregation = '''{
    "request": {
        "pipeline": [
            {"source": {"visitors": null}},
            {"identified": "visitorId"},
            {"filter" : "%s"},
            {"select": {"visitorId": "visitorId"}}
        ],
        "requestId": "req3"
    }
}''' % filter
    return filter

import epdb;epdb.st()
url = "https://app.pendo.io/api/v1/metadata/visitor/custom/value"
headers = {'X-Pendo-Integration-Key': 'INTEGRATION KEY HERE',
           'content-type': 'application/json'
          }
meta = requests.patch(url, headers = headers, data = json.dumps(metaArray))


