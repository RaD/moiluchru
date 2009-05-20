-- начальные установки для django-robots
insert into `robots_rule` values (1,'*',null);
insert into `robots_rule_allowed` values (4,1,1);
insert into `robots_rule_disallowed` values (6,1,3),(5,1,2);
insert into `robots_rule_sites` values (5,1,1);
insert into `robots_url` values (1,'/'),(2,'/admin/'),(3,'/pics/');
