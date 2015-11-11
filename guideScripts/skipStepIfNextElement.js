pendo.Sizzle('._pendo-guide_')[0].style['display'] = 'none';
//TODO wrap this in a try
//pendo.Sizzle('._pendo-backdrop_')[0].style['display'] = 'none';
(function() {
    // need to know:
    // -- this steps' index
    // get these as soon as the step renders, otherwise timing issues can give us the wrong step object
    var activeObj = getActiveGuide();
    var nextStep = activeObj.guide.steps[activeObj.stepIndex + 1];

pendo._.defer(function(){

    // Test next step's element to see if it is present
    // if it is, then move to that step

    var results = pendo.Sizzle(nextStep.elementPathRule);
    // this check may not be necessary, but for good measure
    if (activeObj.step.seenState == 'advanced' || activeObj.step.seenState == 'dismissed') {
      return;//Step already advanced, do nothing
    } else if (results.length == 0 || !pendo._.some(results, pendo.isElementVisible)) {
        pendo.Sizzle('._pendo-guide_')[0].style['display'] = 'block';
        //TODO wrap this in a try
        //pendo.Sizzle('._pendo-backdrop_')[0].style['display'] = 'block';
    } else {
        pendo.onGuideAdvanced(activeObj.step);
    }
});

})();

// TODO find out why pendo.guidDev version doesn't always work
// may be related to the previous version before timing fix
function getActiveGuide (){
    var currentStep = null, stepIdx = -1;
    var currentGuide = pendo._.find(pendo.guides, function(guide) { 
        return pendo._.find(guide.steps, function(step, idx){
            var id_str = "_pendo_g_"+step.id;
            if (pendo.Sizzle('#'+id_str).length > 0) {
                currentStep = step;
                stepIdx = idx;
                return true;
            }
            return false;
        });
    });

    if (!currentGuide) return null;

    return {
        guide: currentGuide,
        step: currentStep,
        stepIndex: stepIdx
    };
};
