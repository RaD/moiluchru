// Отображение формы подтверждения

function show_form(item_id, item_title) {

  var apply_func = function() {
    new Ajax.Request('/shop/add/',
		     { method: 'post',
		       parameters: 
		       { ctx_left: context_left,
			 selected: context_error,
			 ctx_right: context_right,
			 comment: textarea.value },
		       onSuccess: function(transport) {
			 var response = transport.responseText || "нет ответа";
			 splashwidget.init('Успешно!', 2000);
		       },
		       onFailure: function() {
			 window.status = 'Что-то сломалось :(';
			 splashwidget.init('Ошибка!', 2000);
		       }
		     });
    // уничтожаем объект
    form.parentNode.removeChild(form);
  }

  var cancel_func = function() {
    // уничтожаем объект
    form.parentNode.removeChild(form);
  }
  
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
				 ['id', 'item_quantity'],
				 ['maxlength', '2']]) ],
			 [['class', 'body']]),
		    _dom('div',
			 [ _dom('button', _txt('Отправить'), 
				[['onclick', apply_func]]),
			   _dom('span', _txt(' '), []), // место между кнопками
			   _dom('button', _txt('Отменить'),
				[['onclick', cancel_func]]) ],
			 [['class', 'body']]) ],
		  [['class', 'widget']]);
    document.getElementsByTagName('BODY')[0].appendChild(form);

    // позиционирование на середине экрана
    var gForm = getGeometry(form);
    form.style.top = (self.innerHeight / 2 - gForm.height / 2 + self.pageYOffset) + 'px';
    form.style.left = (self.innerWidth / 2 - gForm.width / 2) + 'px';
}
