-- Создаём запись для администраторов.
INSERT INTO jabber_jidpool (nick, password, is_locked, created, last_used) VALUES 
       ('admins', 'top_secret', 1, now(), now()),
       ('ml0002', 'sha1$6d8d4$f5fc0fd06c6cd257f2ea624887ae194ee792bb65', 0, now(), now()),
       ('ml0003', 'sha1$77deb$f5f70982ac0fd7fb5251cf6005fe52af411b9a5f', 0, now(), now()),
       ('ml0004', 'sha1$37a96$bbbaf92e8b4cd40daf5b44adddb87c0acda167b7', 0, now(), now()),
       ('ml0005', 'sha1$d46ae$dc81fc278305b68cb6dc914289df9bdeee4254a2', 0, now(), now()),
       ('ml0006', 'sha1$09dfb$7e461f6928fe4e1954d541f8d8e02bb83d80f588', 0, now(), now());
