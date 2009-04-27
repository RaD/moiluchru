
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
	$('#popup').toggleClass('hide');
	$('#opaco').toggleClass('hide');
    }
};

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

function jabber_message(action, input) {
    var chat = $('#chat-window');
    var loading = $('#loading');
    var params = {}
    loading.toggleClass('hide');
    switch(action) {
    case 'connect':
	chat.html('<div style="color: orange;">Система: подключение...</div>');
	params = { action: action, message: 'not used' }
	break;
    case 'send':
	params = { action: action, message: input.val() }
	break;
    }
    $.post('/ajax/jabber/message/', params,
	   function(json) {
	       loading.toggleClass('hide');
	       if (json['code'] == 200) {
		   switch(action) {
		   case 'connect':
		       chat.html(chat.html() + '<div style="color: orange;">Система: соединение установлено...</div>');
		       break;
		   case 'send':
		       chat.html(chat.html() + '<div style="color: green;">Клиент: ' + input.val() + '</div>');
		       input.val('');
		       break;
		   }
	       } else {
		   switch(action) {
		       case 'connect':
		       chat.html(chat.html() + '<div style="color: orange;">Система: соединение не установлено...</div>');
		       break;
		   }
		   chat.html(chat.html() + '<div style="color: red;">Ошибка: ' + json['code'] + ': ' + json['desc'] + '</div>');
	       }
	   }, 'json' );
}

