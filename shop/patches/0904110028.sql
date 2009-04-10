-- создание полнотекстового индекса
alter table shop_item add fulltext index shop_item_text (`title`,`desc`);
alter table text_text add fulltext index text_text_text (`text`);
