#!/usr/bin/env python
#

import argparse
import logging
import sys
import os
import json
import requests
from pprint import pprint

def getSubscription():
    user = os.environ.get('PENDO_USER')
    subscription = os.environ.get('PENDO_SUBSCRIPTION')
    assert user
    assert subscription
    url = "https://pendo-io.appspot.com/api/s/%s/user/%s/setting/impersonate.subscription" % (subscription, user)
    headers = {'cookie': 'pendo.sess=%s' % getSessionId() }
    impersonate = requests.get(url, headers = headers )
    impersonateSubscription = json.loads(impersonate.content)['value']
    # if we are internal
    if not impersonateSubscription:
        impersonateSubscription = subscription
    return impersonateSubscription

def getSessionId():
    sessionId = os.environ.get('PENDO_SESS')
    assert sessionId
    return sessionId

def getGuides(subscription):
    url = "https://pendo-io.appspot.com/api/s/%s/guide?includeArchived=true" % subscription
    headers = {'cookie': 'pendo.sess=%s' % getSessionId(),
               'accept': 'application/json, text/plain, */*'
              }
    guides = requests.get(url, headers = headers )
    return guides.content

def getGuideUrl(guideId):
    subscription = getSubscription()
    rootUrl = 'https://pendo-io.appspot.com/api/s/%s/guide/' % subscription
    url = "%s%s" % (rootUrl, guideId)
    return url

def getGuideMeta(guideId):
    url = getGuideUrl(guideId)
    headers = {'cookie': 'pendo.sess=%s' % getSessionId() }
    guide = requests.get(url, headers = headers )
    # TODO check response code and raise error
    return guide.content

def putGuideMeta(guideId, json):
    url = getGuideUrl(guideId)
    headers = {'cookie': 'pendo.sess=%s' % getSessionId(),
               'Content-Type':'application/json'
              }
    guide = requests.put(url, headers = headers, data = json )
    # TODO check response code and raise error
    return guide.status_code

def getStepUrl(guideId, stepId):
    subscription = getSubscription()
    rootUrl = 'https://pendo-io.appspot.com/api/s/%s/guide/' % subscription
    url = "%s%s/step/%s" % (rootUrl, guideId, stepId)
    return url

def getStepContent(guideId, stepId):
    #TODO implement simple cache and only use getGuides() to load
    url = getStepUrl(guideId, stepId)
    headers = {'cookie': 'pendo.sess=%s' % getSessionId() }
    step = requests.get(url, headers = headers )
    # TODO check response code and raise error
    return step.content

def putStepContent(guideId, stepId, json):
    url = getStepUrl(guideId, stepId)
    headers = {'cookie': 'pendo.sess=%s' % getSessionId(),
               'Content-Type':'application/json'
              }
    step = requests.put(url, headers = headers, data = json )
    # TODO check response code and raise error
    return step.status_code

#http://code.activestate.com/recipes/576644-diff-two-dictionaries/
def dict_diff(d1, d2, NO_KEY='<KEYNOTFOUND>'):
    a = d1.keys()
    b = d2.keys()
    both = []
    for e in a:
        if e in b:
            both.append(e)
    diff = {k:(d1[k], d2[k]) for k in both if d1[k] != d2[k]}
    diff.update({k:(d1[k], NO_KEY) for k in list(set(d1.keys()) - set(both))})
    diff.update({k:(NO_KEY, d2[k]) for k in list(set(d2.keys()) - set(both))})
    return diff

def guideCheckout(guideId, jsonFilename):
    if jsonFilename:
        jsonFile = open(jsonFilename, 'r')
        guides = json.load(jsonFile)
    else:
        guides = json.loads(getGuides(getSubscription()))
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
                with open(os.path.join(path, "%02d-%s.meta" % (stepnum, stepId)), 'w') as temp_file:
                    temp_file.write(json.dumps(step))
                with open(os.path.join(path, "%02d-%s.html" % (stepnum, stepId)), 'w') as temp_file:
                    temp_file.write(content.encode('utf8'))
            guide.pop('steps', None)
            with open(os.path.join(path, "guide.meta"), 'w') as temp_file:
                temp_file.write(json.dumps(guide))

        elif not guideId:
            print "ignoring guide %s name = %s" % (guide['id'], guide['name'])

    if foundOne == False:
        print "warning: never found guide matching ID %s" % guideId

def guideUpload(guideId, destructive = False):
    #TODO verify regexUrlRule isn't editable, ignore for now
    skipKeys = set(['regexUrlRule', 'dismissedCount', 'uniqueDisplayedCount', 'displayedCount', 'advancedCount', 'totalDuration', 'lastUpdatedAt', 'lastUpdatedByUser'])
    # WARNING: breaks on extra files in this directory
    rootDir = '.'
    for dirName, subdirList, fileList in os.walk(rootDir):
        if guideId:
            if not dirName[2:] == guideId:
                continue
        for fname in fileList:
            if fname.endswith(".html"):
                step_id = fname[:-5][3:]   # drop step number and ".html"
                content = getStepContent(dirName[2:], step_id)
                upstreamStep = json.loads(content)
                # WARNING assumption that every html file will have a corresponding meta
                localStep = json.load(open("%s/%s.meta" %(dirName, fname[:-5]), 'rb'))  # use stepnum from the original filename
                localStepContent = open("%s/%s" %(dirName, fname), 'rb')
                localStep[u'content'] = localStepContent.read().decode('utf8')
                strippedUpstreamStep = dict(upstreamStep)
                for key in skipKeys.intersection(set(strippedUpstreamStep.keys())):
                    strippedUpstreamStep.pop(key)
                for key in skipKeys.intersection(set(localStep.keys())):
                    localStep.pop(key)
                stepDiff = dict_diff(localStep,strippedUpstreamStep)
                if userVerify(stepDiff):
                    # take upstreamStep and update only the colliding values (localStep already stripped above)
                    upstreamStep.update(localStep)
                    #TODO switch these to log
                    print "updating content for guide %s -> %s" % (localStep['guideId'], fname)
                    pprint(stepDiff)
                    if destructive:
                        print putStepContent(dirName[2:], step_id, json.dumps(upstreamStep))
                    else:
                        print "- non-destructive mode: no changes actually uploaded."
            elif fname == "guide.meta":
                upstreamGuideMeta = json.loads(getGuideMeta(dirName[2:]))
                guideMeta = json.load(open("%s/%s" %(dirName, fname), 'rb'))
                strippedUpstreamGuideMeta = dict(upstreamGuideMeta)
                for key in skipKeys.intersection(set(guideMeta.keys())):
                    strippedUpstreamGuideMeta.pop(key)
                # TODO don't compare steps right now, but likely could use this to update in one fell swoop
                strippedUpstreamGuideMeta.pop('stateHistory')
                strippedUpstreamGuideMeta.pop('steps')
                # stateHistory is actually local after the first action
                if guideMeta.has_key('stateHistory'):
                    guideMeta.pop('stateHistory')
                for key in skipKeys.intersection(set(guideMeta.keys())):
                    guideMeta.pop(key)
                metaDiff = dict_diff(guideMeta,strippedUpstreamGuideMeta)
                if userVerify(metaDiff):
                    upstreamGuideMeta.update(guideMeta)
                    #TODO switch these to log
                    print "updating meta for guide %s" % guideMeta['id']
                    pprint(metaDiff)
                    if destructive:
                        print putGuideMeta(dirName[2:], json.dumps(guideMeta))
                        #pass
                    else:
                        print "- non-destructive mode: no changes actually uploaded."

def userVerify(stepDiff):
    if stepDiff:
    # Display Difference
    # Collect and Return User Acknowledgement
        return True
    else:
        return False

# Gather our code in a main() function
def main(args, loglevel):
  logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

  if args.action == "down" or args.action == "d":
      guideCheckout(args.guide, args.json)
  elif args.action == "up" or args.action == "u":
      guideUpload(args.guide, args.y)
  else:
    print "unrecognized action"

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
                                    description = "Does a thing to some stuff.",
                                    epilog = "As an alternative to the commandline, params can be placed in a file, one per line, and specified on the commandline like '%(prog)s @params.conf'.",
                                    fromfile_prefix_chars = '@' )
  parser.add_argument(
                      "action",
                      help = "Specify checkout or checkin action",
                      metavar = "ACTION")
  parser.add_argument(
                      "--guide", '-g',
                      help = "Guide to checkout or checkin",
                      metavar = "GUIDE")
  parser.add_argument(
                      "-v",
                      "--verbose",
                      help="increase output verbosity",
                      action="store_true")
  parser.add_argument(
                      "-y",
                      help = "Enter destructive mode",
                      action="store_true")
  parser.add_argument(
                      "--json",
                      help = "Use JSON input",
                      )
  #parser.add_argument(
  #                    "-a",
  #                    help = "Checkout All Guides",
  #                    metavar = "ALL")
  args = parser.parse_args()

  if args.verbose:
    loglevel = logging.DEBUG
  else:
    loglevel = logging.INFO

  main(args, loglevel)
