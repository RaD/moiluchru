-- избавился от типов телефонов
alter table shop_phone drop column type_id;
drop table shop_phonetype;
