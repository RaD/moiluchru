// Отображение формы подтверждения

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
  
function show_form(item_id, item_title) {
  var widget = $('widget_addtocart');
  if (! widget) return;

  var ajax_response = function(transport) {
    var xml = transport.responseXML.firstChild;
    check_result(true,
		 get_xml_item(xml, 'code'),
		 function() {
		   update_cart(get_xml_item(xml, 'cart_count'),
			       get_xml_item(xml, 'cart_price')); },
		 null);
  }
  
  var apply_func = function() {
    new Ajax.Request('/shop/add/',
		     { method: 'post',
		       parameters: { item_id: item_id,
				     item_count: $('widget_item_quantity').value },
		       onSuccess: ajax_response, onFailure: ajax_response });
    // скрываем
    widget.style.display = 'none';
  }

  var cancel_func = function() {
    // скрываем
    widget.style.display = 'none';
  }

  var onkeypress = function(e) {
    var pressed = 0;
    var we = null;
    if (window.event) we = window.event;
    else if (parent && parent.event) we = parent.event;
    if (we) { // IE & Opera & Konqueror
      //alert('pressed ' + we.keyCode);
      pressed = we.keyCode;
    } else if (e) { // NN
//       alert('which ' + e.which + 
// 	    ' modifiers ' + e.modifiers + 
// 	    ' keycode ' + e.keyCode + 
// 	    ' charCode ' + e.charCode + 
// 	    ' ctrlKey ' + e.ctrlKey);
      pressed = e.keyCode;
    }
    if (pressed == 27) {
      parent.document.onkeypress = null;
      cancel_func();
    }
    if (pressed == 13) {
      parent.document.onkeypress = null;
      apply_func();
    }
  }

  parent.document.onkeypress = function(e) { return onkeypress(e); }

  document.getElementsByTagName('BODY')[0].appendChild(widget);
  $('widget_apply').onclick = apply_func
  $('widget_cancel').onclick = cancel_func;
  widget.style.display = 'block';
  
  // позиционирование на середине экрана
  var gWidget = getGeometry(widget);
  widget.style.top = (self.innerHeight / 2 - gWidget.height / 2 + self.pageYOffset) + 'px';
  widget.style.left = (self.innerWidth / 2 - gWidget.width / 2) + 'px';

  $('widget_item_quantity').focus();
}

function update_cart(count, price) {
  $('cart_count').innerHTML = count;
  $('cart_price').innerHTML = price;
  $('clean_button').className = (count == 0) ? 'hide' : 'show';
  if ($('item_remains')) {
    // обновляем информацию о товаре, если находимся на соответствующей странице
    show_item_count_info(_attr($('item_remains'), 'item_id'));
  }
}

function clean_cart(url) {
  var ajax_response = function(transport) {
    var xml = transport.responseXML.firstChild;
    check_result(true,
		 get_xml_item(xml, 'code'),
		 function() { update_cart("0", "0.00");
			      if (url) 
				window.setTimeout(function() { 
						    document.location = url; }, 
						  3000); },
		 null);
  }
  new Ajax.Request('/shop/clean/', 
		   { method: 'post',
		     onSuccess: ajax_response, onFailure: ajax_response });
}

function show_item_count_info(item_id) {
  var ajax_response = function(transport) {
    var xml = transport.responseXML.firstChild;
    check_result(false,
		 get_xml_item(xml, 'code'),
		 function() { $('item_remains').innerHTML = get_xml_item(xml, 'remains');
			      window.status = 'Проверка наличия товара: OK'; },
		 function() { window.status = 'Проверка наличия товара: Ошибка'; });
  }

  var callback = function() {
    new Ajax.Request('/shop/count/',
		     { method: 'get', parameters: { item_id: item_id },
		       onSuccess: ajax_response, onFailure: ajax_response });
  }

  callback(); // для мгновенного обновления
  var pe = new PeriodicalExecuter(callback, 60);
}
