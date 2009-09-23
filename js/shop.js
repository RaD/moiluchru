function update_cart(count, price) {
    $('#cart_count').html(count);
    $('#cart_price').html(price);
    if (count == 0)
	$('#clean_button').hide();
    else
	$('#clean_button').show();
}

function clean_cart(url) {
    $.post('/ajax/cart/clean/', {},
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

function buy(id, count) {
    $('#loading').toggleClass('hide');
    var params = { item: id, count: count }
    $.post('/ajax/cart/add/', params,
	   function(json) {
	       if (json['code'] == 200) {
		   update_cart(json['cart_count'], json['cart_price']);
		   $(this).toggleZoom(); 
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
    var popup = $('#popup');
    if (popup.hasClass('hide')) {
	// затеняем окно
	if(! $.browser.msie) {
	    $('#opaco').height($(document).height()).toggleClass('hide').fadeTo('slow', 0.7);
	} else {
	    $('#opaco').height($(document).height()).toggleClass('hide');
	}
	// отображаем
	popup.html($(this).html()).alignCenter().toggleClass('hide');
	// ставим обработчик клавиатуры
	$(document).bind('keypress',
                         function(e) {
			     var code = (e.keyCode ? e.keyCode : e.which);
			     if (code == 27) popup.toggleZoom();
			 }
			);
    } else {
	// снимаем обработчик клавиатуры
	$(document).unbind('keypress');
	$('#opaco').fadeTo('slow', 0.0, 
			   function() {
			       popup.toggleClass('hide');
			       $(this).toggleClass('hide');
			   });
    }
};

$.fn.extend({
    scrollTo: function(obj, speed, easing) {
	return this.each(function() {
	    var targetOffset = obj.offset().top;
	    $(this).animate({scrollTop: targetOffset}, speed, easing);
	});
    },
    idle: function(microsec) {
	var o = $(this);
	o.queue(function() {
	    return function() {
		setTimeout(function() { o.dequeue(); }, microsec);
	    };
	});
    },
    place: function(obj) {
	return this.each(function() {
	    //debugger;
	    var offset = $(this).offset();
	    obj.css({'position': 'absolute', 
		     'top': offset.top+$(this).height(),
		     'left': offset.left,
		     'opacity': 0.3}).toggleClass('hide').fadeIn();
	});
    }
});

var lamp_lock = false;

function show_lamp(name) {
    if (lamp_lock)
	return;
    lamp_lock = true;
    var th=$('#thumbnail'); 
    th.fadeOut('fast', function() {
	th.toggleClass('hide');
	var lamp = $('#'+name)
	lamp.fadeIn('fast');
	setTimeout(function() {return hide_lamp(name)}, 2000);
    }); 
}

function hide_lamp(name) {
    var lamp = $('#'+name)
    lamp.fadeOut('fast', function() {
	lamp.toggleClass('hide');
	var th=$('#thumbnail'); 
	th.fadeIn('fast');
	lamp_lock = false;
    }); 
}



var tID;
var POLL_TIMEOUT = 10000;
function jabber_init() {
    $('#jabber-client').toggleZoom();
    $('#message-window').bind('keypress',
                              function(e) {
				  var code = (e.keyCode ? e.keyCode : e.which);
				  if (code == 13) {
				      jabber_message();
				  }
			      }
			     );
    $('#message-window input[type="text"]').focus();
    tID = setTimeout(jabber_poll, POLL_TIMEOUT);
    return false;
}

function jabber_destroy() {
    clearTimeout(tID);
    $('jabber-client').toggleZoom(); 
    $.post('/ajax/jabber/message/', { system: '1', message: 'close connection'},
	   function(json) {}, 'json');
    return false;
}

function jabber_message() {
    var chat = $('#chat-window');
    var input = $('#message-window input');
    var loading = $('#loading');
    var msgwin = chat.offset();
    if (loading.hasClass('hide')) {
	loading.css({'top': parseInt(msgwin.top) + 'px', 'left': parseInt(msgwin.left) + 'px'}).toggleClass('hide');
    }
    input.attr('disabled', 'disabled');
    console.log(input.val());
    $.post('/ajax/jabber/message/', { message: input.val(), system: '0' },
	   function(json) {
	       loading.toggleClass('hide');
	       if (json['code'] == 200) {
		   $('#down').before('<div style="color: green;">Клиент: ' + input.val() + '</div>');
		   input.val('');
	       } else {
		   $('#down').before('<div style="color: red;">Ошибка: [' + json['code'] + '] ' + json['desc'] + '</div>');
	       }
	       input.attr('disabled', '');
	       $('#message-window').focus();
	       chat.scrollTo($('#down'), 500);
	   }, 'json' );
}

function jabber_poll() {
    var chat = $('#chat-window');
    $.post('/ajax/jabber/poll/', {},
	   function(json) {
	       if (json['code'] == 200) {
		   $.each(json['messages'], function() { 
		       $('#down').before('<div style="color: orange;">Консультант: ' + this + '</div>');
		       chat.scrollTo($('#down'), 500);
		   });
		   tID = setTimeout(jabber_poll, POLL_TIMEOUT);
	       } else {
		   $('#down').before('<div style="color: red;">Ошибка: [' + json['code'] + '] ' + json['desc'] + '</div>');
		   chat.scrollTo($('#down'), 500);
	       }
	   }, 'json' );
}


var IE6 = false /*@cc_on || @_jscript_version < 5.7 @*/;
var ADVICE_WAIT_TIMEOUT = 100 * 1000;
var ADVICE_HIDE_TIMEOUT = 5 * 1000;
var ADVICE_SLEEP_TIMEOUT = 60 * 1000;
var t_wait = t_hide = t_sleep = null;

function get_advice() {
    $.post('/ajax/advice/random/', {},
	   function(json) {
	       if (json['code'] == 200) {
		   var bot = $('#advicebot table');
		   if (! IE6) {
		       $('.title', bot).html(json['title']);
		       $('.desc', bot).html(json['desc']);
		   }
		   bot.slideDown('slow', function() {
		       t_hide = window.setTimeout(function() {
			   bot.slideUp("slow", function() { 
			       t_sleep = window.setTimeout(function() {
				   get_advice()
			       }, ADVICE_SLEEP_TIMEOUT);
			   });
		       }, ADVICE_HIDE_TIMEOUT);
		   });
	       }
	   }, 'json' );
}

$(document).ready(function() {
    // получить совет через ajax
    if (IE6) {
	get_advice();
    } else {
	t_wait = window.setTimeout(get_advice, ADVICE_WAIT_TIMEOUT);
    }
    // очистка поискового поля при первом тычке
    var search_field = $('form input[name="userinput"]');
    search_field.bind('focus',
		      function(e) {
			  search_field.val('');
			  search_field.unbind('focus');
		      });
    // очистка содержимого поля диапазонного виджета при первом тычке
    var min_max = $('.min_max_widget');
    min_max.each(
	function() {
	    var _this = $(this);
	    _this.bind('focus',
		       function(e) {
			   _this.val('');
			   _this.unbind('focus');
		       }
		      );
	}
    );

    // навигация
    $(document).bind('keyup', function(e) {
	var page_current = parseInt($('#current_page_number').text());
	var page_maximum = parseInt($('#maximum_page_number').text());
	if (e.ctrlKey) {
	    if (e.keyCode == 37 && page_current > 1) {
		document.location = $('#navigation_prev_page').attr('href');
	    }
	    if (e.keyCode == 39 && page_current < page_maximum) {
		document.location = $('#navigation_next_page').attr('href');
	    }
	}
	//console.log(e.ctrlKey, e.keyCode, page_current, page_maximum);
    });
});
