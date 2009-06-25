-- Создаём запись для администраторов.
INSERT INTO jabber_jidpool (nick, password, is_locked, created, last_used) VALUES 
       ('admins', 'top_secret', 1, now(), now());
