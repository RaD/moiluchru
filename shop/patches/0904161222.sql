alter table shop_item add column has_lamp tinyint(1) not null after is_present;
update shop_item set has_lamp=1;

commit;
