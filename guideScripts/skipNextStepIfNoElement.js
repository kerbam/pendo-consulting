//TODO wrap this in a try
// CSS for banner: ._pendo-guide-container_ { display: none;}

pendo.Sizzle('._pendo-guide_')[0].style['display'] = 'none';
pendo.Sizzle('._pendo-backdrop_')[0].style['display'] = 'none';

(function() {
    // need to know:
    // -- this steps' index
    // get these as soon as the step renders, otherwise timing issues can give us the wrong step object
    var guideId = "<%= guide.id %>";
    var stepId = "<%= step.id %>";
    var guide = pendo.findGuideById(guideId);
    var step = guide.findStepById(stepId);
    var nextStepIndex = pendo._.indexOf(guide.steps, step) + 1;
    var nextStep = guide.steps[nextStepIndex];

setTimeout(function (){

    // Test next step's element to see if it is present
    // if it's not, skip that step.

    var results = pendo.Sizzle(nextStep.elementPathRule);
    if (results.length == 0 || !pendo._.some(results, pendo.isElementVisible)) {
        // in this case we want to skip 2 steps forward
        pendo.log('advance 2 steps');
        pendo.onGuideAdvanced(nextStep);
    } else {
      pendo.log('advance 1 step');
      pendo.onGuideAdvanced(step);
    }
}, 1000);

})();
