alter table shop_item add column sort_price double;

update shop_item a, shop_price b,
       (select max(id) id from shop_price group by item_id) c
set a.sort_price=b.price_shop
where a.id=b.item_id and b.id=c.id;
