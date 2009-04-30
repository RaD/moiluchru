
function update_cart(count, price) {
    $('#cart_count').html(count);
    $('#cart_price').html(price);
    if (count == 0)
	$('#clean_button').hide();
    else
	$('#clean_button').show();
}

function clean_cart(url) {
    $.post('/shop/clean/', {},
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
    if ($('#popup').hasClass('hide')) {
	// затеняем окно
	if(! $.browser.msie) {
	    $('#opaco').height($(document).height()).toggleClass('hide').fadeTo('slow', 0.7);
	} else {
	    $('#opaco').height($(document).height()).toggleClass('hide');
	}
	// выводим изображение и вешаем обработчик
	$('#popup').html($(this).html()).alignCenter().toggleClass('hide');
    } else {
	$('#opaco').fadeTo('slow', 0.0, 
			   function() {
			       $('#popup').toggleClass('hide');
			       $(this).toggleClass('hide')
			   });
    }
};

$.fn.extend({
    scrollTo: function(shift, speed, easing) {
	return this.each(function() {
	    $(this).animate({scrollTop: parseInt($(this).css('scrollTop') + shift)}, speed, easing);
	});
    }
});

function buy(id, count) {
    $('#loading').toggleClass('hide');
    $.post('/ajax/cart/add/',
	   { item: id, count: count },
	   function(json) {
	       if (json['code'] == 200) {
		   update_cart(json['cart_count'], json['cart_price']);
		   $(this).toggleZoom(); 
	       } else {
		   alert(json['code'] + ': ' + json['desc']);
	       }
	   }, 'json' );
}

var tID;
var POLL_TIMEOUT = 10000;
function jabber_init() {
    $('#jabber-client').toggleZoom();
    $('#message-window').bind('keypress',
                              function(e) {
				  var code = (e.keyCode ? e.keyCode : e.which);
				  if (code == 13) {
				      jabber_message($('#message-window'));
				  }
			      }
			     );
    $('#message-window').focus();
    tID = setTimeout(jabber_poll, POLL_TIMEOUT);
    return false;
}

function jabber_destroy() {
    clearTimeout(tID);
    $('jabber-client').toggleZoom(); 
    return false;
}

function jabber_message(input) {
    var chat = $('#chat-window');
    var loading = $('#loading');
    var params = {}
    var msgwin = $('#chat-window').offset();
    if (loading.hasClass('hide')) {
	loading.css({'top': parseInt(msgwin.top) + 'px', 'left': parseInt(msgwin.left) + 'px'}).toggleClass('hide');
    }
    params = { message: input.val() }
    $.post('/ajax/jabber/message/', params,
	   function(json) {
	       loading.toggleClass('hide');
	       if (json['code'] == 200) {
		   chat.html(chat.html() + '<div style="color: green;">Клиент: ' + input.val() + '</div>');
		   input.val('');
	       } else {
		   chat.html(chat.html() + '<div style="color: red;">Ошибка: [' + json['code'] + '] ' + json['desc'] + '</div>');
	       }
	       chat.scrollTo('100', 500);
	   }, 'json' );
}

function jabber_poll() {
    var chat = $('#chat-window');
    $.post('/ajax/jabber/poll/', {},
	   function(json) {
	       if (json['code'] == 200) {
		   $.each(json['messages'], function() { 
		       chat.html(chat.html() + '<div style="color: orange;">Консультант: ' + this + '</div>');
		       chat.scrollTo('100', 500);
		   });
		   tID = setTimeout(jabber_poll, POLL_TIMEOUT);
	       } else {
		   chat.html(chat.html() + '<div style="color: red;">Ошибка: [' + json['code'] + '] ' + json['desc'] + '</div>');
		   chat.scrollTo('100', 500);
	       }
	   }, 'json' );
}
