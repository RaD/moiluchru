-- убираем дубликаты изображений
update shop_item set image='itempics/OS-2U.jpg' where id in (445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456);
update shop_item set image='itempics/OS-S3U.jpg' where id in (458, 459, 460, 461, 462, 463, 464);
update shop_item set image='itempics/OS-4U.jpg' where id in (466);
update shop_item set image='itempics/OS-4A.jpg' where id in (467, 469, 470);
update shop_item set image='itempics/OS-9.jpg' where id in (472, 473, 474, 475, 476, 477, 478);
