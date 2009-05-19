-- добавляем к таблице модели Color поле для кода цвета
alter table shop_color add column `code` varchar(6) not null;
