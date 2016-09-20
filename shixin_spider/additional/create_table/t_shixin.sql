use spider;

# 失信被执行人-有效id记录表
drop table if exists `t_shixin_valid`;
create table `t_shixin_valid` (

  `id` int unsigned primary key auto_increment comment 'id',
  `alter_time` timestamp default current_timestamp on update current_timestamp,

  `sys_id` int unsigned not null comment '查询id',
  `name` varchar(128) not null comment '个人姓名/公司名',
  `age` varchar(8) default null comment '年龄',
  `sex` varchar(8) default null comment '性别',
  `card_num` varchar(64) not null comment '身份证号/公司编号',
  `business_entity` varchar(64) default null comment '公司法人',

  `area_name` varchar(64) not null comment '地区',
  `case_code` varchar(128) not null comment '案号',
  `reg_date` varchar(128) not null comment '立案时间',
  `publish_date` varchar(128) not null comment '发布时间',
  `gist_id` varchar(128) not null comment '执行依据文号',
  `court_name` varchar(128) not null comment '执行法院',
  `gist_unit` varchar(128) not null comment '做出执行依据单位',
  `duty` text not null comment '生效法律文书确定的义务',
  `performance` varchar(128) default null comment '被执行人的履行情况',
  `disrupt_type_name` varchar(128) default null comment '失信被执行人行为具体情形',

  `party_type_name` varchar(128)  default null comment '含义未知字段',
  `flag` tinyint not null comment '0代表个人, 1代表公司',

  key `search`(`name`, `card_num`, `flag`),
  unique key `unique_id`(`sys_id`)

) engine=innodb default charset=utf8 auto_increment=1000 comment='失信被执行人-有效id表';


# 失信被执行人-无效id记录表
drop table if exists `t_shixin_invalid`;
create table `t_shixin_invalid`(
  `id` int unsigned primary key auto_increment comment 'id', 
  `alter_time` timestamp default current_timestamp on update current_timestamp,

  `sys_id` int unsigned not null comment '查询id',
  `err_type` tinyint not null comment '1表示请求失败,2表示超时,3表示未知错误',
  `flag` tinyint default 1 comment '1表示未处理,0表示已处理',

  key `search`(`err_type`, `flag`),
  unique key `unique_id` (`sys_id`)

)engine = innodb default charset=utf8 auto_increment=1 comment='失信被执行人-无效id表';