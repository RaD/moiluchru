jQuery.noConflict();
jQuery(document).ready(
    function() {
	var c_offset = jQuery("#image-container").offset()
	var c_width = jQuery("#image-container").width()
	var f_height = jQuery("#item-info-widget").height()
	jQuery("#item-info-widget").css("top", c_offset.top + 180 - f_height).css("left", c_offset.left - 60).show();
    }
);

// Отображение формы подтверждения

function show_form(item_id, item_title) {
    var widget = jQuery('#widget-addtocart');
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
    
    var cancel_func = function() {
	// скрываем
	widget.hide();
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
	    // сделать правильную обработку для оперы
	    parent.document.onkeypress = null;
	    apply_func();
	}
    }
    
    parent.document.onkeypress = function(e) { return onkeypress(e); }
    
    jQuery("body").append(widget);
    jQuery("#widget_apply").click(function() {
	new Ajax.Request('/shop/add/',
			 { method: 'post',
			   parameters: { item_id: item_id,
					 item_count: $('widget_item_quantity').value },
			   onSuccess: ajax_response, onFailure: ajax_response });
	// скрываем
	widget.hide();
    });
    jQuery("#widget_cancel").click(function() {
	widget.hide();
    });
    widget.show();
    
    // позиционирование на середине экрана
    widget.css("top", (self.innerHeight / 2 - widget.height() / 2 + self.pageYOffset) + 'px');
    widget.css("left", (self.innerWidth / 2 - widget.width() / 2) + 'px');
    
    jQuery("widget_item_quantity").focus();
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

