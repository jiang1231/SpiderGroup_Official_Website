use spider;

# 政府机关联络方式表
drop table if exists `t_phone_book`;
create table `t_phone_book`(
  	`id` int unsigned primary key auto_increment comment 'id', 
    `alter_time` timestamp default current_timestamp on update current_timestamp,


    `province` varchar(64) not null comment 'province',
    `city` varchar(64) default null comment 'city',
    `sub_city` varchar(64) default null comment '区',
    `town_street` varchar(64) default null comment 'town/street',

    `department` varchar(128) not null comment '机关称呼',
    `tel_num` varchar(32) not null comment '电话号码',
 	unique key `unique_key` (`province`,`city`,`sub_city`,`town_street`,`department`,`tel_num`)

)engine = innodb default charset=utf8 auto_increment=1 comment='政府机关联络方式表';

# 导入数据
load data infile "/home/user/spider/data/t_phone_book.csv" into table `t_phone_book`
character set utf8
fields terminated by ',' optionally enclosed by '"'
lines terminated by '\r\n'
ignore 1 lines
(city, department, province, sub_city, tel_num, town_street);