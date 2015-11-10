#!/usr/bin/env python
#

import argparse
import logging
import sys
import os
import json
import requests


def getSubscription():
    user = os.environ.get('PENDO_USER')
    subscription = os.environ.get('PENDO_SUBSCRIPTION')
    assert user
    assert subscription
    url = "https://app.pendo.io/api/s/%s/user/%s/setting/impersonate.subscription" % (subscription, user)
    headers = {'cookie': 'pendo.sess=%s' % getSessionId() }
    impersonate = requests.get(url, headers = headers )
    return json.loads(impersonate.content)['value']

def getSessionId():
    sessionId = os.environ.get('PENDO_SESS')
    assert sessionId
    return sessionId

def getGuides(subscription):
    url = "https://app.pendo.io/api/s/%s/guide?includeArchived=true" % subscription
    headers = {'cookie': 'pendo.sess=%s' % getSessionId(),
               'accept': 'application/json, text/plain, */*'
              }
    guides = requests.get(url, headers = headers )
    return guides.content

def getStepUrl(guideId, stepId):
    subscription = getSubscription()
    rootUrl = 'https://app.pendo.io/api/s/%s/guide/' % subscription
    url = "%s%s/step/%s" % (rootUrl, guideId, stepId)
    return url

def getStepContent(guideId, stepId):
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


#guides = json.load(open('./guide.json', 'rb'))


def guideCheckout(guideId):
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


# Gather our code in a main() function
def main(args, loglevel):
  logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

  # TODO Replace this with your actual code.
  print "Hello there."
  logging.info("You passed an argument.")
  logging.debug("Your Argument: %s" % args.action)
  import epdb; epdb.st()
  if args.action == "checkout" or args.action == "co":
      guideCheckout(args.guide)
  elif args.action == "checkin" or args.action == "ci":
      guideCheckout(args.guide)
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
                      metavar = "DESTRUCTIVE")
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
