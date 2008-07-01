// Отображение формы подтверждения

function show_form(item_id, item_title) {

  var apply_func = function() {
    new Ajax.Request('/shop/add/',
		     { method: 'post',
		       parameters: { item_id: item_id,
				     item_count: form.item_quantity.value },
		       onSuccess: function(transport) {
			 var response = transport.responseText || "нет ответа";
			 var xml = transport.responseXML;
			 update_cart(_elts(xml.firstChild, 'cart_count')[0].firstChild.nodeValue,
				     _elts(xml.firstChild, 'cart_price')[0].firstChild.nodeValue);
			 splashwidget.init('Успешно!', 2000);
		       },
		       onFailure: function(transport) {
			 window.status = 'Что-то сломалось :(';
			 var response = transport.responseText || "нет ответа";
			 splashwidget.init('Ошибка! ' + response, 20000);
		       }
		     });
    // уничтожаем объект
    form.parentNode.removeChild(form);
  }

  var cancel_func = function() {
    // уничтожаем объект
    form.parentNode.removeChild(form);
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
  }

  parent.document.onkeypress = function(e) { return onkeypress(e); }

  var form = _dom('form',
		  [ _dom('div',
			 [ _txt('Добавить в корзину') ],
			 [['class', 'title']]),
		    _dom('div',
			 [ _txt('Товар'),
			   _dom('span', _txt(item_title)) ], 
			 [['class', 'body']]),
		    _dom('div',
			 [ _txt('Количество'),
			   _dom('input', [], 
				[['type', 'text'],
				 ['value', '1'], // добавить валидатор
				 ['id', 'item_quantity'],
				 ['maxlength', '2']]) ],
			 [['class', 'body']]),
		    _dom('div',
			 [ _dom('button', _txt('Отправить'), 
				[['class', 'button'], 
				 ['onclick', apply_func]]),
			   _dom('span', _txt(' '), []), // место между кнопками
			   _dom('button', _txt('Отменить'),
				[['class', 'button'], 
				 ['onclick', cancel_func]]) ],
			 [['id', 'buttons'], ['class', 'body']]) ],
		  [['class', 'widget']]);
  document.getElementsByTagName('BODY')[0].appendChild(form);
  
  // позиционирование на середине экрана
  var gForm = getGeometry(form);
  form.style.top = (self.innerHeight / 2 - gForm.height / 2 + self.pageYOffset) + 'px';
  form.style.left = (self.innerWidth / 2 - gForm.width / 2) + 'px';

  form.item_quantity.focus();
//  form.style.display = 'block';
}

function update_cart(count, price) {
  $('cart_count').innerText = count;
  $('cart_price').innerText = price;
}

function clean_cart() {
  new Ajax.Request('/shop/clean/',
		   { method: 'post',
		     onSuccess: function(transport) {
		       var response = transport.responseText || "нет ответа";
		       update_cart("0", "0.00");
		       splashwidget.init('Успешно!', 2000);
		     },
		     onFailure: function(transport) {
		       window.status = 'Что-то сломалось :(';
		       var response = transport.responseText || "нет ответа";
		       splashwidget.init('Ошибка! ' + response, 20000);
		     }
		   });
}
