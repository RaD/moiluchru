// jQuery.noConflict();
// jQuery(document).ready(
//     function() {
// 	var t_offset = jQuery("#thumbnail").offset()
// 	var t_height = jQuery("#thumbnail").height()
// 	jQuery("#item-info-widget").css("top", t_offset.top + t_height - 50)
//                                    .css("left", t_offset.left - 10)
//                                    .show();
//     }
// );

// Отображение формы подтверждения

function show_form(item_id, item_title) {
    var widget = jQuery('#widget-addtocart');
    if (! widget) return;
    
  var apply_func = function() {
    jQuery.post('/shop/add/',
		{ item: item_id,
		  count: jQuery("#widget_item_quantity").val() },
		function(json) {
		  if (json['code'] == 200) {
		    update_cart(json['cart_count'], json['cart_price']);
		  } else {
		    alert(json['code'] + ': ' + json['desc']);
		  }
		}, 'json' );
    // скрываем
    widget.hide();
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
  jQuery("#widget_apply").click(apply_func);
  jQuery("#widget_cancel").click(cancel_func);
  widget.show();
    
    // позиционирование на середине экрана
    widget.css("top", (self.innerHeight / 2 - widget.height() / 2 + self.pageYOffset) + 'px');
    widget.css("left", (self.innerWidth / 2 - widget.width() / 2) + 'px');
    
    jQuery("widget_item_quantity").focus();
}

function update_cart(count, price) {
  jQuery("#cart_count").html(count);
  jQuery("#cart_price").html(price);
  if (count == 0)
    jQuery("#clean_button").hide();
  else
    jQuery("#clean_button").show();
}

function clean_cart(url) {
  jQuery.post('/shop/clean/', {},
	      function(json) {
		if (json['code'] == 200) {
		  update_cart("0", "0.00");
		  if (url) 
		    window.setTimeout(function() { 
					document.location = url; }, 
				      3000); 
		} else {
		  alert(json['code'] + ': ' + json['desc']);
		}
	      }, 'json' );
}

$.fn.alignCenter = function() {
    var marginLeft = - $(this).width()/2 + 'px';
    var marginTop = - $(this).height()/2 + 'px';
    return $(this).css({'margin-left':marginLeft, 'margin-top':marginTop});
};

$.fn.toggleZoom = function() {
    if ($('#zoom').hasClass('hide')) {
	// создаём объекты
	$('<div id="opaco" class="hide"></div>').appendTo('body');
	$('<div id="popup" class="hide"></div>').appendTo('body');
	// затеняем окно
	if(! $.browser.msie) {
	    $('#opaco').height($(document).height()).toggleClass('hide').fadeTo('slow', 0.7);
	} else {
	    $('#opaco').height($(document).height()).toggleClass('hide');
	}
	// выводим изображение и вешаем обработчик
	$('#popup').html($(this).html()).alignCenter().toggleClass('hide');
	$('#popup').bind('click', function(e) {$(this).toggleZoom();});
    } else {
	$('#popup').remove();
	$('#opaco').remove();
    }
};

