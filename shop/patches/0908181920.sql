-- добавил поле для транслитерации
alter table shop_category add column `slug` varchar(255) not null;
