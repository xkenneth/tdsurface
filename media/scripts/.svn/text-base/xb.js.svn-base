function addEvent(elm, evType, fn, useCapture)
// cross-browser event handling for IE5+, NS6+ and Mozilla
// By Scott Andrew
{
  if (elm.addEventListener) {
    elm.addEventListener(evType, fn, useCapture);
    return true;
  } else if (elm.attachEvent) {
    var r = elm.attachEvent('on' + evType, fn);
    return r;
  } else {
    elm['on' + evType] = fn;
  }
}

// climb up the tree to the supplied tag.
function ascendDOM(e, target) {
  while (e.nodeName.toLowerCase() != target &&
      e.nodeName.toLowerCase() != 'html')
    e = e.parentNode;

  return (e.nodeName.toLowerCase() == 'html') ? null : e;
}
