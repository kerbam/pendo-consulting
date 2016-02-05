//TODO wrap this in a try
pendo.Sizzle('._pendo-guide_')[0].style['display'] = 'none';
pendo.Sizzle('._pendo-backdrop_')[0].style['display'] = 'none';
(function() {
    // need to know:
    // -- this steps' index
    // get these as soon as the step renders, otherwise timing issues can give us the wrong step object
    var activeObj = pendo.guideDev.getActiveGuide();
    var nextStep = activeObj.guide.steps[activeObj.stepIndex + 1];

setTimeout(function (){

    // Test next step's element to see if it is present
    // if it's not, skip that step.

    var results = pendo.Sizzle(nextStep.elementPathRule);
    // this check may not be necessary, but for good measure
    if (activeObj.step.seenState == 'advanced' || activeObj.step.seenState == 'dismissed') {
      return;//Step already advanced, do nothing
    } else if (results.length == 0 || !pendo._.some(results, pendo.isElementVisible)) {
        // in this case we want to skip 2 steps forward
        pendo.log('advance 2 steps');
        pendo.onGuideAdvanced({steps: 2});
    } else {
      pendo.log('advance 1 step');
      pendo.onGuideAdvanced(activeObj.step);
    }
}, 1000);

})();
