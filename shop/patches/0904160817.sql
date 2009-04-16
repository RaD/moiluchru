create table shop_size as select * from shop_lamp;

alter table shop_lamp drop column diameter;
alter table shop_lamp drop column height;
alter table shop_lamp drop column length;
alter table shop_lamp drop column width;
alter table shop_lamp drop column brow;

alter table shop_size drop column socle_id;
alter table shop_size drop column watt;
alter table shop_size drop column `count`;
alter table shop_size drop column voltage;

commit;
