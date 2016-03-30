//Usage:
//
//HTML:
//<div class="_pendo_consult_guide_progress_bar"><div class="inner_progress_bar" style="width:30%;"></div></div>
//
//CSS:
//._pendo_consult_guide_progress_bar{
//    clear: both;
//    margin: 0;
//    padding: 0;
//    height: 3px;
//    background-color: #9ccaec; }
//
//  .inner_progress_bar {
//  height: 3px;
//  padding: 0 4px;
//  margin: 0;
//  background-color: #4378a0;
//  border: 0;
//  box-shadow: none;
//  display: block;
//  position: relative;
//}
//  .inner_progress_bar:hover:after {
//  background: #333;
//  background: rgba(0, 0, 0, 0.8);
//  border-radius: 5px;
//  top: -38px; /*height of this element + top and bottom padding + height of :before*/
//  color: #fff;
//  content: attr(data-progress);
//  right: -23px; /*50% width + padding*/
//  padding: 6px;
//  position: absolute;
//  z-index: 98;
//  width: 40px;
//  height: 20px;
//  text-align: center;
//  }
//  .inner_progress_bar:hover:before {
//  border: solid;
//  border-color: #333 transparent;
//  border-width: 6px 6px 0 6px;
//  top: -6px;
//  content: "";
//  right: -5px;
//  position: absolute;
//  z-index: 99;
//  }

pendo._.defer(function() {
  try {
    var guide = pendo.guideDev.getActiveGuide(),
        barInner = pendo.Sizzle("._pendo_consult_guide_progress_bar .inner_progress_bar")[0];
    barInner.style['width'] = '' + ((guide.stepIndex + 1) / guide.guide.steps.length * 100) + '%';
    barInner.setAttribute( "data-progress", '' + ((guide.stepIndex + 1) / guide.guide.steps.length * 100).toFixed(0) + '%');
  } catch (e) {}
});
