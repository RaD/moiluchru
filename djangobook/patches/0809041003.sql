-- добавление поля для модуля жалоб
alter table djangobook_claims add column email varchar(75) not null after url;
