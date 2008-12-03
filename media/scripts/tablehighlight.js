// turn on highlighting
function hi_cell(e) {
  var el;
  if (window.event && window.event.srcElement)
    el = window.event.srcElement;
  if (e && e.target)
    el = e.target;
  if (!el) return;

  el = ascendDOM(el, 'td');
  if (el == null) return;

  var parent_row = ascendDOM(el, 'tr');
  if (parent_row == null) return;

  var parent_table = ascendDOM(parent_row, 'table');
  if (parent_table == null) return;

  // row styling
  parent_row.className += ' hi';

}

// turn off highlighting
function lo_cell(e) {
  var el;
  if (window.event && window.event.srcElement)
    el = window.event.srcElement;
  if (e && e.target)
    el = e.target;
  if (!el) return;

  el = ascendDOM(el, 'td');
  if (el == null) return;

  var parent_row = ascendDOM(el, 'tr');
  if (el == null) return;

  var parent_table = ascendDOM(parent_row, 'table');
  if (el == null) return;

  // row de-styling
  parent_row.className = parent_row.className.replace(/\b ?hi\b/, '');

}

function addListeners()
{
    if (!document.getElementsByTagName) return;

    var allTables = document.getElementsByTagName('table');

    for(var i = 0; i < allTables.length; i++)
    {
        if(allTables[i].className.match('hilightrow'))
        {
            var allTD = allTables[i].getElementsByTagName('td');
            for (var x = 0; x < allTD.length; x++)
            {
                addEvent(allTD[x], 'mouseover', hi_cell, false);
                addEvent(allTD[x], 'mouseout', lo_cell, false);
            }
        }
    }
}

addEvent(window, 'load', addListeners, false);

