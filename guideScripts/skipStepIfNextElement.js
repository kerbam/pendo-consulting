pendo.Sizzle('._pendo-guide_')[0].style['display'] = 'none';
// Only for lightboxes
//pendo.Sizzle('._pendo-backdrop_')[0].style['display'] = 'none';
pendo._.defer(function (){

    // Test next step's element to see if it is present
    // if it's not, skip that step.

    var activeObj = pendo.guideDev.getActiveGuide() 
    var nextStep = activeObj.guide.steps[activeObj.stepIndex + 1];

    var results = pendo.Sizzle(nextStep.elementPathRule);
    if (results.length == 0 || !pendo._.some(results, pendo.isElementVisible)) {
        // in this case we want:
        // 
        // - to show this guide + backdrop
        // - rig up the advance method to complete the guide

        pendo.Sizzle('._pendo-guide_')[0].style['display'] = 'block';
        // Only for lightboxes
        //pendo.Sizzle('._pendo-backdrop_')[0].style['display'] = 'block';

    } else {
        pendo.onGuideAdvanced(activeObj.step);
    }
});
