-- Добавлено поле для скидки
alter table shop_order add column `discount` integer unsigned not null after totalprice;
