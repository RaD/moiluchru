alter table shop_item add column `tags` varchar(255) not null;
alter table shop_item drop index shop_item_text;
alter table shop_item add fulltext index shop_item_text (`title`,`desc`,`tags`);
