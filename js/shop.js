var BrowserDetect = {
    init: function () {
	this.browser = this.searchString(this.dataBrowser) || "An unknown browser";
	this.version = this.searchVersion(navigator.userAgent)
	    || this.searchVersion(navigator.appVersion)
	    || "an unknown version";
	this.OS = this.searchString(this.dataOS) || "an unknown OS";
    },
    searchString: function (data) {
	for (var i=0;i<data.length;i++)	{
	    var dataString = data[i].string;
	    var dataProp = data[i].prop;
	    this.versionSearchString = data[i].versionSearch || data[i].identity;
	    if (dataString) {
		if (dataString.indexOf(data[i].subString) != -1)
		    return data[i].identity;
	    }
	    else if (dataProp)
		return data[i].identity;
	}
    },
    searchVersion: function (dataString) {
	var index = dataString.indexOf(this.versionSearchString);
	if (index == -1) return;
	return parseFloat(dataString.substring(index+this.versionSearchString.length+1));
    },
    dataBrowser: [
	{
	    string: navigator.userAgent,
	    subString: "Chrome",
	    identity: "Chrome"
	},
	{ 	string: navigator.userAgent,
		subString: "OmniWeb",
		versionSearch: "OmniWeb/",
		identity: "OmniWeb"
	},
	{
	    string: navigator.vendor,
	    subString: "Apple",
	    identity: "Safari",
	    versionSearch: "Version"
	},
	{
	    prop: window.opera,
	    identity: "Opera"
	},
	{
	    string: navigator.vendor,
	    subString: "iCab",
	    identity: "iCab"
	},
	{
	    string: navigator.vendor,
	    subString: "KDE",
	    identity: "Konqueror"
	},
	{
	    string: navigator.userAgent,
	    subString: "Firefox",
	    identity: "Firefox"
	},
	{
	    string: navigator.vendor,
	    subString: "Camino",
	    identity: "Camino"
	},
	{		// for newer Netscapes (6+)
	    string: navigator.userAgent,
	    subString: "Netscape",
	    identity: "Netscape"
	},
	{
	    string: navigator.userAgent,
	    subString: "MSIE",
	    identity: "Explorer",
	    versionSearch: "MSIE"
	},
	{
	    string: navigator.userAgent,
	    subString: "Gecko",
	    identity: "Mozilla",
	    versionSearch: "rv"
	},
	{ 		// for older Netscapes (4-)
	    string: navigator.userAgent,
	    subString: "Mozilla",
	    identity: "Netscape",
	    versionSearch: "Mozilla"
	}
    ],
    dataOS : [
	{
	    string: navigator.platform,
	    subString: "Win",
	    identity: "Windows"
	},
	{
	    string: navigator.platform,
	    subString: "Mac",
	    identity: "Mac"
	},
	{
	    string: navigator.userAgent,
	    subString: "iPhone",
	    identity: "iPhone/iPod"
	},
	{
	    string: navigator.platform,
	    subString: "Linux",
	    identity: "Linux"
	}
    ]
};
BrowserDetect.init();

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
    $.post('/ajax/jabber/message/', { system: 'close connection'},
	   function(json) {}, 'json');
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
    input[0].disabled = true;
    params = { message: input.val() }
    $.post('/ajax/jabber/message/', params,
	   function(json) {
	       loading.toggleClass('hide');
	       if (json['code'] == 200) {
		   $('#down').before('<div style="color: green;">Клиент: ' + input.val() + '</div>');
		   input.val('');
	       } else {
		   $('#down').before('<div style="color: red;">Ошибка: [' + json['code'] + '] ' + json['desc'] + '</div>');
	       }
	       input[0].disabled = false;
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

var ADVICE_HIDE_TIMEOUT = 6 * 1000;

function get_advice() {
    $.post('/ajax/advice/random/', {},
	   function(json) {
	       if (json['code'] == 200) {
		   $('#advicetext > .title').html(json['title']);
		   $('#advicetext > .desc').html(json['desc']);
	       }
	   }, 'json' );
}

function hide_advice(o) {
    o.slideUp("slow", function() { 
	o.hide();
	get_advice();
    });
}

$(document).ready(function() {
    // получить совет через ajax
    if (($.browser.msie && parseInt(BrowserDetect.version) < 7) ||
	($.browser.opera && parseInt(BrowserDetect.version) < 9) ||
	($.browser.mozilla && parseInt(BrowserDetect.version) < 3)) {
	// нифига не делать, пусть обновляются
    } else {
	get_advice();
    }

    // настроить советника
    $('#advicebot').bind('click',
			 function(e) {
			     var o = $('#advicetext')
			     if ( o.is(':hidden') ) {
				 o.slideDown("slow", function() { 
				     window.setTimeout(function() {
					 hide_advice(o);
				     }, ADVICE_HIDE_TIMEOUT);
				 });
			     }
			 });
});
