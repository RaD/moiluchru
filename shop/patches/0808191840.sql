-- создание полнотекстового индекса
alter table shop_item add fulltext index shop_item_text (`title`,`desc`);
alter table shop_producer add fulltext index shop_producer_text (`name`);
