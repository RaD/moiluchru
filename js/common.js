Array.prototype.eachfor = function(f) {
  for (var i=0; i<this.length; i++) {
    f(this[i], i);
  }
}

function add_event(el, event, f, capture) {
  el.addEventListener && el.addEventListener(event, f, capture);
  el.attachEvent && el.attachEvent('on'+event, f, capture);
}

function flat_insert(where, content) {
  if (content != null) {
    if (content instanceof Array)
      _foreach(function(x) { flat_insert(where, x); }, content);
    else
      where.appendChild(content);
  }
}

function set_attrs(obj, attrs) {
  if (attrs) {
    _foreach(function(x) {
	       switch(x[0]) {
	       case 'class': obj.className = x[1]; break;
	       case 'id': obj.id = x[1]; break;
	       case 'src': obj.src = x[1]; break;
	       case 'title': obj.title = x[1]; break;
	       case 'type': obj.type = x[1]; break;
	       case 'name': obj.name = x[1]; break;
	       case 'value': obj.value = x[1]; break;
	       case 'onclick': obj.onclick = x[1]; break;
	       }
	     }, attrs);
  }
}

function _txt(content) {
  return document.createTextNode((content == null) ? '' : content);
}

function _dom(tagname, content, attrs) {
  var element = document.createElement(tagname);
  flat_insert(element, content);
  set_attrs(element, attrs);
  return element;
}

function _map(callback, obj) {
  var result = [];
  for(var i = 0; i < obj.length; ++i)
    result.push(callback(obj[i]));
  return result;
}

function _foreach(callback, obj) {
  for(var i = 0; i < obj.length; ++i)
    callback(obj[i],i);
}

function _index(callback, obj) {
  for(var i = 0; i < obj.length; ++i)
    if(callback(obj[i])) return i;
  return -1;
}

function _find(callback, obj) {
  for(var i = 0; i < obj.length; ++i)
    if(callback(obj[i])) return obj[i];
  return false;
}

function _find_index(callback, obj) {
  for( var i = 0; i < obj.length; ++i )
    if( callback( obj[i] ) )
      return { object: obj[i],
               index: i };
  return false;
}

function _filter(callback, obj) {
    var result = [];
    for(var i = 0; i < obj.length; ++i)
        if(callback(obj[i])) result.push(obj[i]);
    return result;
}

function _attr(obj, attr) {
  if ( obj.attributes ) {
    try {
      return obj.getAttribute( attr );
    } catch ( exception ) {
      if ( exception.kind == 'string' )
        alert( '_attr: obj is ' + obj.tagName + ', ' + exception );
    }
  }
  return null;
}

function _elts(obj, name) {
  return obj.getElementsByTagName(name);
}

function _elts_class(el, className) {
  var children = _elts(el, '*') || document.all;
  var elements = new Array();

  for (var i=0; i<children.length; i++) {
    var child = children[i];
    var classNames = child.className.split(' ');
    for (var j=0; j<classNames.length; j++) {
      if (classNames[j] == className) {
	elements.push(child);
	break;
      }
    }
  }
  return elements;
}

function _table(table, content, attrs) {
  if(table == null)
    table = document.createElement('TABLE');
  if(table.tBodies[0] == null)
    table.appendChild(document.createElement('TBODY'));
  flat_insert(table.tBodies[0], content);
  set_attrs(table, attrs);
  return table;
}

function _th(content, attrs) {
    var th = document.createElement('TH');
    flat_insert(th, content);
    set_attrs(th, attrs);
    return th;
}

function _tr(tr, content, attrs) {
    if (!tr) tr = document.createElement('TR');
    flat_insert(tr, content);
    set_attrs(tr, attrs);
    return tr;
}

function _td(content, attrs) {
    var td = document.createElement('TD');
    flat_insert(td, content);
    set_attrs(td, attrs);
    return td;
}

function getGeometry(obj) {
  var top = obj.offsetTop;
  var left = obj. offsetLeft;
  var parent = obj.offsetParent;
  while (parent) {
    top += parent.offsetTop;
    left += parent.offsetLeft;
    parent = parent.offsetParent;
  }
  return { top: top,
	   left: left,
	   width: obj.offsetWidth,
	   height: obj.offsetHeight };
}

var splashwidget = {

  init: function(msg, millisecs) {
    this.widget = _dom('div', _txt(msg), 
		       [['class', 'splashwidget']]);
    document.getElementsByTagName('BODY')[0].appendChild(this.widget);
    this.widget.style.top = (20 + self.pageYOffset) + 'px';
    this.widget.style.left = '20px';
    this.show(millisecs);
  },

  show: function(millisecs) {
    var widget = this.widget;
    window.setTimeout(function() {
			widget.parentNode.removeChild(widget); 
		      }, millisecs);
  }
}

// получение значения тэга из объекта
function get_xml_item(obj, tag_name) {
  return _elts(obj, tag_name)[0].firstChild.nodeValue;
}

function check_result(show_splash, code, success_func, failure_func) {
  if (code == '200') {
    if (success_func) { success_func(); }
  } else {
    if (failure_func) { failure_func(); }
  }
  switch (code) {
  case '200': result = 'Успешно'; break;
  case '201': result = 'Неудачно: Недостаточно товара на складе...'; break;
  default: result = 'Неудачно: ['+code+'] '+get_xml_item(xml, 'desc');
  }
  if (show_splash) { splashwidget.init(result, 2000); }
}
