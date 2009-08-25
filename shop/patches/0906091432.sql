-- разрешил не указывать курьера
alter table shop_orderstatuschange modify column `courier_id` integer;

-- добавил тестовое значение
insert into shop_orderstatus (title) values ('тестирование');
