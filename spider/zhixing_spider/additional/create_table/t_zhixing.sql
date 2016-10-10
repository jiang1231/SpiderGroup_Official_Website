use spider;

# 执行-有效id记录表
drop table if exists `t_zhixing_valid`;
create table `t_zhixing_valid`(
	`id` int unsigned primary key auto_increment comment 'id', 
 	`alter_time` timestamp default current_timestamp on update current_timestamp,

	`sys_id` int unsigned not null comment '查询id',
	`name` varchar(128) not null comment '个人姓名/公司名',
	`card_num` varchar(64) not null comment '身份证号/公司编号',

	`case_code` varchar(128) not null comment '案号',       			
	`reg_date`  varchar(128) not null comment '立案时间',   			
	`court_name` varchar(128) not null comment '执行法院',  			
	`execute_money` varchar(64) default null comment '金额',     	   

	unique key `unique_id` (`sys_id`),
  index `search`(`name`, `card_num`)

)engine = innodb default charset=utf8 auto_increment=1 comment='执行-有效id的记录';



# 执行-无效id记录表
drop table if exists `t_zhixing_invalid`;
create table `t_zhixing_invalid`(
	`id` int unsigned primary key auto_increment comment 'id', 
	`alter_time` timestamp default current_timestamp on update current_timestamp,

	`sys_id` int unsigned not null comment '查询id',
	`err_type` tinyint not null comment '1表示请求失败,2表示超时,3表示未知错误',
	`flag` tinyint default 1 comment '1表示未处理,0表示已处理',

	unique key `unique_id` (`sys_id`),
  index `search`(`err_type`, `flag`)

)engine = innodb default charset=utf8 auto_increment=1 comment='执行-无效id的记录';




