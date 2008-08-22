--
-- Table structure for table `shop_category`
--

DROP TABLE IF EXISTS `shop_category`;
CREATE TABLE `shop_category` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(30) collate utf8_unicode_ci NOT NULL,
  `parent_id` int(11) default NULL,
  PRIMARY KEY  (`id`),
  KEY `shop_category_parent_id` (`parent_id`)
) ENGINE=MyISAM AUTO_INCREMENT=26 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `shop_category`
--

LOCK TABLES `shop_category` WRITE;
/*!40000 ALTER TABLE `shop_category` DISABLE KEYS */;
INSERT INTO `shop_category` VALUES (1,'Электроника',NULL),(2,'Видеокамеры',1),(3,'Аксессуары',2),(4,'Бытовая техника',NULL),(5,'Климатическое оборудование',NULL),(6,'Мебель',NULL),(7,'Инструмент',NULL),(8,'Музыкальные центры',1),(9,'Акустика',1),(10,'Спорт',NULL),(11,'Кондиционеры',5),(12,'Увлажнители',5),(13,'Ионизаторы',5),(14,'Посудомоечные машины',4),(15,'Холодильники',4),(16,'Печи',4),(17,'Стиральные машины',4),(18,'Водонагреватели',5),(19,'Для офиса',6),(20,'Для дома',6),(21,'Для дачи',6),(22,'Телефоны',1),(23,'Сотовые',22),(24,'Стационарные',22),(25,'Радио',22);
/*!40000 ALTER TABLE `shop_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shop_color`
--

DROP TABLE IF EXISTS `shop_color`;
CREATE TABLE `shop_color` (
  `id` int(11) NOT NULL auto_increment,
  `title` varchar(60) collate utf8_unicode_ci NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=9 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `shop_color`
--

LOCK TABLES `shop_color` WRITE;
/*!40000 ALTER TABLE `shop_color` DISABLE KEYS */;
INSERT INTO `shop_color` VALUES (1,'Красный'),(2,'Зелёный'),(3,'Синий'),(4,'Белый'),(5,'Чёрный'),(6,'Серебристый'),(7,'Серый'),(8,'Коричневый');
/*!40000 ALTER TABLE `shop_color` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shop_country`
--

DROP TABLE IF EXISTS `shop_country`;
CREATE TABLE `shop_country` (
  `id` int(11) NOT NULL auto_increment,
  `title` varchar(60) collate utf8_unicode_ci NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=8 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `shop_country`
--

LOCK TABLES `shop_country` WRITE;
/*!40000 ALTER TABLE `shop_country` DISABLE KEYS */;
INSERT INTO `shop_country` VALUES (1,'Российская Федерация'),(2,'Соединённые Штаты Америки'),(3,'Япония'),(4,'Германия'),(5,'Южная Корея'),(6,'Финляндия'),(7,'Китайская Народная Республика');
/*!40000 ALTER TABLE `shop_country` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shop_howto`
--

DROP TABLE IF EXISTS `shop_howto`;
CREATE TABLE `shop_howto` (
  `id` int(11) NOT NULL auto_increment,
  `key` varchar(32) collate utf8_unicode_ci NOT NULL,
  `title` varchar(32) collate utf8_unicode_ci NOT NULL,
  `text` longtext collate utf8_unicode_ci NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `shop_howto`
--

LOCK TABLES `shop_howto` WRITE;
/*!40000 ALTER TABLE `shop_howto` DISABLE KEYS */;
INSERT INTO `shop_howto` VALUES (1,'dostavka','Доставка','Мы доставляем товары с 8до 22 часов, ежедневно.'),(2,'contact','Контактная информация','Мы находимся по адресу ....\r\nТелефон ...\r\nКарта проезда ...'),(3,'choice','Как выбрать товар','Товар можно выбрать двумя способами:\r\n1. Поискать его.\r\n2. Выбрать в соответствующей категории.'),(4,'order','Как заказать выбранные товары','В правом верхнем углу...');
/*!40000 ALTER TABLE `shop_howto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shop_item`
--

DROP TABLE IF EXISTS `shop_item`;
CREATE TABLE `shop_item` (
  `id` int(11) NOT NULL auto_increment,
  `title` varchar(60) collate utf8_unicode_ci NOT NULL,
  `desc` longtext collate utf8_unicode_ci NOT NULL,
  `category_id` int(11) NOT NULL,
  `producer_id` int(11) NOT NULL,
  `price` double NOT NULL,
  `color_id` int(11) NOT NULL,
  `count` int(10) unsigned NOT NULL,
  `reserved` int(10) unsigned NOT NULL default '0',
  `reg_date` datetime NOT NULL,
  `image` varchar(100) collate utf8_unicode_ci NOT NULL,
  `buys` int(11) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `shop_item_category_id` (`category_id`),
  KEY `shop_item_producer_id` (`producer_id`),
  KEY `shop_item_color_id` (`color_id`),
  FULLTEXT KEY `shop_item_text` (`title`,`desc`)
) ENGINE=MyISAM AUTO_INCREMENT=48 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `shop_item`
--

LOCK TABLES `shop_item` WRITE;
/*!40000 ALTER TABLE `shop_item` DISABLE KEYS */;
INSERT INTO `shop_item` VALUES (1,'Samsung VP-W60','Общие характеристики:\r\n  Тип видеокамеры: Video8, аналоговая\r\nОбъектив:\r\nZoom оптический / цифровой	22x / 500x\r\n 	 \r\nДополнительная информация\r\nМинимальная освещенность	0.3 люкс\r\nМаксимальное время работы от аккумулятора	2 ч\r\nРазмеры (ШхВхГ)	174x104x101 мм\r\nВес	650 г\r\nСнята с производства	да\r\n\r\nМатрица\r\nКоличество матриц	1\r\nМатрица	0.32 Мпикс',2,1,4500,6,0,0,'2008-06-22 19:20:58','itempics/samsung_vp-w60.jpeg',0),(2,'Sony HDR-HC96','Отличная камера среднего ценового диапазона.\r\n\r\nУ неё есть много прикольных возможностей -- например, режим 16х9.',2,2,9600,6,6,5,'2008-06-22 19:21:54','itempics/sony_hc96e_.jpg',0),(3,'Nokia 5310','телефончег',23,6,6700,3,5,0,'2008-07-16 18:46:49','itempics/nokia_5310.jpeg',7),(4,'Nokia 6300','phone',23,6,11000,6,10,0,'2008-07-16 18:47:18','itempics/nokia_6300.jpeg',8),(5,'Nokia 6233','phone',23,6,8900,5,17,0,'2008-07-16 18:47:42','itempics/nokia_6233.jpeg',1),(6,'Nokia 3110','phone',23,6,2400,6,5,0,'2008-07-16 18:48:17','itempics/nokia_3310.jpeg',0),(7,'Siemens M50','phone',23,5,3400,4,14,0,'2008-07-16 18:48:52','itempics/siemens_m50.jpeg',4),(8,'LG KE970 Shine','phone',23,4,7490,6,19,0,'2008-07-16 18:49:22','itempics/lg_ke970_shine.jpeg',0),(9,'Sony-Ericsson P1i','phome',23,2,11198,5,12,0,'2008-07-16 18:50:35','itempics/sony-ericsson_p1i.jpeg',0),(10,'iPhone One','phone',23,7,16400,6,13,0,'2008-07-16 18:51:13','itempics/iphone_.jpeg',0),(11,'iPhone 3G','phone',23,7,24000,6,4,0,'2008-07-16 18:51:56','itempics/iphone.jpeg',0),(12,'Samsung VP-D101i','Камера',2,1,5230,6,15,0,'2008-08-12 18:03:56','itempics/samsung_vp-d101i.jpeg',0),(13,'General Electric 1887','Общие характеристики\r\nКомплектация	база, трубка\r\n 	 \r\nРабочая частота	1880-1900 МГц\r\n 	 \r\nСтандарт	DECT',25,8,1450,5,17,0,'2008-08-21 23:31:38','itempics/general_electric_1887.jpeg',5),(14,'Senao SN-568','Общие характеристики\r\nКомплектация	база\r\n 	 \r\nРабочая частота	240-390 МГц\r\n 	 \r\nСтандарт DECT	нет\r\n 	 \r\nРадиус действия в помещении	30000 м',25,9,33750,5,8,0,'2008-08-21 23:34:23','itempics/senao_sn-568.jpeg',3),(15,'Panasonic KX-TCA355','Общие характеристики\r\nКомплектация	трубка\r\n 	 \r\nРабочая частота	1880-1900 МГц\r\n 	 \r\nСтандарт	DECT',25,3,7184,5,43,0,'2008-08-21 23:35:43','itempics/panasonic_kx-tca355.jpeg',0),(16,'Siemens Gigaset S645','Общие характеристики\r\nКомплектация	база, трубка\r\n 	 \r\nРабочая частота	1880-1900 МГц\r\n 	 \r\nСтандарт	DECT/GAP\r\n 	 \r\nРадиус действия в помещении / на открытой местности	50 / 300 м',25,5,4000,6,55,0,'2008-08-21 23:40:29','itempics/siemens_gigaset_s645.jpeg',0),(17,'Philips ID 9371','Общие характеристики\r\nКомплектация	база, трубка\r\n 	 \r\nРабочая частота	1880-1900 МГц\r\n 	 \r\nСтандарт	DECT/GAP',25,10,3940,5,55,0,'2008-08-21 23:42:08','itempics/philips_id_9371.jpeg',0),(18,'Motorola D802','Общие характеристики\r\nКомплектация	база, две трубки\r\n 	 \r\nРабочая частота	1880-1900 МГц\r\n 	 \r\nСтандарт	DECT/GAP\r\n 	 \r\nРадиус действия в помещении / на открытой местности	50 / 300 м',25,11,3243,4,19,0,'2008-08-21 23:43:44','itempics/motorola_d802.jpeg',0),(19,'Motorola D811','Общие характеристики\r\nКомплектация	база, трубка\r\n 	 \r\nРабочая частота	1880-1900 МГц\r\n 	 \r\nСтандарт	DECT/GAP\r\n 	 \r\nРадиус действия в помещении / на открытой местности	50 / 300 м',25,11,3150,5,23,0,'2008-08-21 23:44:47','itempics/motorola_d811.jpeg',0),(20,'Siemens Gigaset C450','Общие характеристики\r\nКомплектация	база, трубка\r\n 	 \r\nРабочая частота	1880-1900 МГц\r\n 	 \r\nСтандарт	DECT/GAP\r\n 	 \r\nРадиус действия в помещении / на открытой местности	50 / 300 м',25,5,1631,7,43,0,'2008-08-21 23:46:18','itempics/siemens_gigaset_c450.jpeg',0),(21,'Sony CMT-DH5BT','Основные характеристики\r\nТип	микросистема\r\n 	 \r\nОсновной блок	одноблочная система\r\n 	 \r\nОформление акустических систем	черный\r\n 	 \r\nОформление основного блока 	черный',8,2,10769,5,35,0,'2008-08-21 23:55:41','itempics/sony_cmt-dh5bt.jpeg',0),(22,'Panasonic SC-VK960EE-K','Основные характеристики\r\nТип	минисистема\r\n 	 \r\nОсновной блок	одноблочная система\r\n 	 \r\nОформление акустических систем	черный\r\n 	 \r\nОформление основного блока 	черный\r\n 	 \r\nДекодеры	Dolby Digital, Dolby Pro Logic II, DTS',8,3,13500,5,22,0,'2008-08-21 23:56:55','itempics/panasonic_sc-vk960ee-k.jpeg',0),(23,'Supra SMK-22X','Основные характеристики\r\nТип	микросистема\r\n 	 \r\nОсновной блок	одноблочная система\r\n 	 \r\nОформление акустических систем	под дерево\r\n 	 \r\nОформление основного блока 	серебристый/хром/титан\r\n 	 \r\nДекодеры	Dolby Digital, DTS',8,12,2675,6,12,0,'2008-08-21 23:58:12','itempics/supra_smk-22x.jpeg',0),(24,'JVC NX-G3','Основные характеристики\r\nТип	минисистема\r\n 	 \r\nОсновной блок	одноблочная система\r\n 	 \r\nОформление акустических систем	черный\r\n 	 \r\nОформление основного блока 	черный\r\n 	 \r\nДекодеры	Dolby Digital, DTS',8,13,20000,5,5,0,'2008-08-21 23:59:43','itempics/jvc_nx-g3.jpeg',0),(25,'Sony CMT-EH15','Основные характеристики\r\nТип	микросистема\r\n 	 \r\nОсновной блок	одноблочная система\r\n 	 \r\nОформление акустических систем	под дерево\r\n 	 \r\nОформление основного блока 	серебристый/хром/титан',8,2,3245,6,76,0,'2008-08-22 00:00:55','itempics/sony_cmt-eh15.jpeg',0),(26,'Hyundai H-MS2303','Основные характеристики\r\nТип	минисистема\r\n 	 \r\nОсновной блок	одноблочная система\r\n 	 \r\nОформление акустических систем	черный\r\n 	 \r\nОформление основного блока 	черный',8,14,1899,5,43,0,'2008-08-22 00:02:37','itempics/huindai_h-ms2303.jpeg',18),(27,'Yamaha NS-8900','Основные параметры\r\nТип	напольная, пассивная, фазоинверторного типа\r\n 	 \r\nАкустическое излучение	монополярная\r\n 	 \r\nНазначение	фронтальный громкоговоритель\r\n 	 \r\nСостав комплекта	2 громкоговорителя',9,15,10890,5,20,0,'2008-08-22 00:05:43','itempics/yamaha_ns-8900.jpeg',0),(28,'JBL L880','Основные параметры\r\nТип	напольная, пассивная, фазоинверторного типа\r\n 	 \r\nАкустическое излучение	монополярная\r\n 	 \r\nНазначение	фронтальный громкоговоритель',9,16,22506,5,20,0,'2008-08-22 00:07:38','itempics/jbl_l880.jpeg',20),(29,'Yamaha NS-555','Основные параметры\r\nТип	напольная, пассивная, фазоинверторного типа\r\n 	 \r\nСостав комплекта	2 громкоговорителя',9,15,14017,5,20,0,'2008-08-22 00:08:38','itempics/yamaha_ns-555.jpeg',0),(30,'Martin Logan Spire','Основные параметры\r\nТип	напольная, пассивная\r\n 	 \r\nНазначение	фронтальный громкоговоритель\r\n 	 \r\nСостав комплекта	1 громкоговоритель',9,17,325001,7,5,0,'2008-08-22 00:10:01','itempics/martin_logan_spire.jpeg',0),(31,'T+A Criterion TR 450','Основные параметры\r\nТип	полочная, пассивная\r\n 	 \r\nАкустическое излучение	монополярная',9,18,61605,8,5,0,'2008-08-22 00:11:34','itempics/ta_criterion_tr_450.jpeg',0),(32,'KEF KUBE 2','Основные параметры\r\nТип	напольная, активная, с пассивным излучателем\r\n 	 \r\nАкустическое излучение	монополярная\r\n 	 \r\nНазначение	сабвуфер\r\n 	 \r\nСостав комплекта	1 громкоговоритель',9,19,21320,5,5,0,'2008-08-22 00:12:44','itempics/kef_kube_2.jpeg',0),(33,'Sony HDR-SR11E','Общие характеристики\r\nТип видеокамеры	HDD AVCHD, цифровая\r\n 	 \r\nТип носителя	жесткий диск\r\n 	 \r\nЕмкость жесткого диска	60 Гб\r\n 	 \r\nПоддержка видео высокого разрешения (Full HD)	есть\r\n 	 \r\nМаксимальное разрешение видеосъемки	1920x1080\r\n 	 \r\nШирокоформатный режим видео	есть',2,2,36960,6,10,0,'2008-08-22 00:15:01','itempics/sony_hdr-sr11e.jpeg',0),(34,'Canon FS100','Общие характеристики\r\nТип видеокамеры	Flash, цифровая\r\n 	 \r\nТип носителя	перезаписываемая память (Flash)\r\n 	 \r\nРежим ночной съемки	есть\r\n 	 \r\nШирокоформатный режим видео	есть',2,20,12250,6,10,0,'2008-08-22 00:16:08','itempics/canon_fs100.jpeg',0),(35,'Panasonic SDR-SW20','Общие характеристики\r\nТип видеокамеры	Flash, цифровая\r\n 	 \r\nТип носителя	перезаписываемая память (Flash)\r\n 	 \r\nШирокоформатный режим видео	есть',2,3,11425,1,10,0,'2008-08-22 00:17:32','itempics/panasonic_sdr-sw20.jpeg',0),(36,'Sanyo Xacti VPC-CG9','Общие характеристики\r\nТип видеокамеры	Flash, цифровая\r\n 	 \r\nТип носителя	перезаписываемая память (Flash)\r\n 	 \r\nМаксимальное разрешение видеосъемки	640x480',2,21,8750,5,10,0,'2008-08-22 00:18:52','itempics/sanyo_xacti_vpr-cg9.jpeg',0),(37,'Direc VC 1790','Общие характеристики\r\nТип видеокамеры	Flash, цифровая\r\n 	 \r\nТип носителя	перезаписываемая память (Flash)\r\n 	 \r\nМаксимальное разрешение видеосъемки	640x480',2,22,20000,5,10,0,'2008-08-22 00:20:01','itempics/direc_vc_1790.jpeg',0),(38,'Sony DCR-SR72E','Общие характеристики\r\nТип видеокамеры	HDD, цифровая\r\n 	 \r\nТип носителя	жесткий диск\r\n 	 \r\nЕмкость жесткого диска	60 Гб\r\n 	 \r\nРежим ночной съемки	есть\r\n 	 \r\nШирокоформатный режим видео	есть',2,2,20000,6,10,0,'2008-08-22 00:20:52','itempics/sony_dcr-sr72e.jpeg',0),(39,'Noname MC UV 49mm','Защитный ультрафиолетовый фильтр. Прозрачный фильтр, поглощающий ультрафиолетовые лучи без увеличения экспозиции...',3,23,248,6,150,0,'2008-08-22 00:25:29','itempics/noname_mc_uv_29mm.jpeg',0),(40,'Sony VCL-D1746','Для DSC-W120,W115,W110,W125,W130,W150,W170 телеобъектив',3,2,2880,6,10,0,'2008-08-22 00:27:44','itempics/sony_vcl-d1746.jpeg',0),(41,'Sony VCL-DH0758','Описание в стадии разработки',3,2,4740,5,10,0,'2008-08-22 00:30:07','itempics/sony_vcl-dh0758.jpeg',0),(42,'SONY BC-TR1','Портативное, удобное зарядное устройство из 1 блока, идеально для поездок \r\n\r\nСовместим с батареями InfoLITHIUM A \r\n\r\nПеременный ток: 100-240 В 50/60 Гц \r\n\r\nПриблизительный вес: 65 г',3,2,1112,7,10,0,'2008-08-22 00:31:14','itempics/sony_bc-tra_b1.jpeg',0),(43,'Sony ECM-HQP1','Микрофон объемного звука для разъема активного интерфейса # Прямое подсоединение к разъему активного интерфейса (Active Interface Shoe), нет необходимости во внешней батарее или кабелях # 180-градусное улавливание звука # Поддерживает 3 различных режима: 4-канальный, широкополосное стереозвучание и стерео # Питание и управление с помощью видеокамеры # Размер: прибл. 32,0 x 74,2 x 65,9 мм Вес: прибл. 50 г',3,2,4498,5,5,0,'2008-08-22 00:32:43','itempics/sony_ecm-hqp1.jpeg',0),(44,'Panasonic KX-TS2362','Общие характеристики\r\nАвтоответчик	нет\r\n 	 \r\nДисплей	есть\r\n 	 \r\nСпикерфон	нет\r\n 	 \r\nОрганайзер	часы',24,3,1030,7,50,0,'2008-08-22 00:34:59','itempics/panasonic_kx-ts2362.jpeg',0),(45,'General Electric 9259','Общие характеристики\r\nАвтоответчик	нет\r\n 	 \r\nДисплей	нет\r\n 	 \r\nСпикерфон	нет',24,8,495,5,120,0,'2008-08-22 00:35:59','itempics/general_electric_9259.jpeg',0),(46,'Orion OC-19FR04R','Общие характеристики\r\nАвтоответчик	нет\r\n 	 \r\nДисплей	нет\r\n 	 \r\nСпикерфон	нет',24,24,500,8,50,0,'2008-08-22 00:37:32','itempics/orion_oc-19r04r.jpeg',0),(47,'Plantronics T20','Общие характеристики\r\nАвтоответчик	нет\r\n 	 \r\nДисплей	нет\r\n 	 \r\nСпикерфон	нет',24,25,3950,5,20,0,'2008-08-22 00:38:38','itempics/plantronics_t20.jpeg',0);
/*!40000 ALTER TABLE `shop_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shop_producer`
--

DROP TABLE IF EXISTS `shop_producer`;
CREATE TABLE `shop_producer` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(30) collate utf8_unicode_ci NOT NULL,
  `country_id` int(11) NOT NULL,
  `buys` int(11) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `shop_producer_country_id` (`country_id`),
  FULLTEXT KEY `shop_producer_text` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=26 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `shop_producer`
--

LOCK TABLES `shop_producer` WRITE;
/*!40000 ALTER TABLE `shop_producer` DISABLE KEYS */;
INSERT INTO `shop_producer` VALUES (1,'Samsung Corp.',5,0),(2,'Sony Corp.',3,0),(3,'Panasonic',3,0),(4,'LG',5,0),(5,'Siemens',4,4),(6,'Nokia',6,16),(7,'Apple',2,0),(8,'General Electric',2,1),(9,'Senao',3,0),(10,'Philips',4,0),(11,'Motorola',2,0),(12,'Supra',3,0),(13,'JVC',3,0),(14,'Hyundai',5,0),(15,'Yamaha',3,0),(16,'JBL',3,0),(17,'Martin Logan',2,0),(18,'T+A',2,0),(19,'KEF',2,0),(20,'Canon',3,0),(21,'Sanyo',5,0),(22,'Direc',2,0),(23,'Noname',7,0),(24,'Orion',7,0),(25,'Plantronics',3,0);
/*!40000 ALTER TABLE `shop_producer` ENABLE KEYS */;
UNLOCK TABLES;

