-- добавление поля для модуля жалоб
alter table djangobook_claims add column notify bool not null after email;
