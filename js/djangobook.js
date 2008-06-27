// This function hides chapter topics.
function init() {
  var chapters = _elts_class(document, 'chapter');
  _foreach(function(ch) {
	     var el = ch.parentNode.nextSibling;
	     if (el &&  el.firstChild && el.firstChild.className != 'chapter') { 
	       el.style.display = 'none';
// 	       add_event(ch, 'mouseover',
// 			 function() { el.style.display = 'block'; },
// 			 false);
// 	       add_event(ch, 'mouseout',
// 			 function() { 
// 			   window.setTimeout(function() { 
// 					       el.style.display = 'none'; 
// 					     }, 1000);
// 			 },
// 			 false);
	     }
	   }, chapters);
}
