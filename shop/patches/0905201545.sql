-- добавил поле для регистрации даты/времени последнего изменения
alter table shop_item add column `last_modification` datetime not null after reg_date;
