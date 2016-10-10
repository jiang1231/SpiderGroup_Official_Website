use spider;

# 个人基本信息表
drop table if exists `t_credit_person_record`;
create table `t_credit_person_record`(
  
  `id` int unsigned primary key auto_increment,
 
  `report_id` varchar(32) not null comment '报告id',
  `query_time` varchar(32) not null comment '查询时间',
  `report_time` varchar(32) not null comment '报告时间',

  `name` varchar(32) not null comment '姓名',
  `id_type` varchar(16) not null comment '证件类型',
  `id_card` varchar(32) not null comment '证件号码',
  `marriage` varchar(8) not null comment '婚姻状况',

   unique index `report` (`report_id`)

) engine=innodb default charset=utf8 auto_increment=1000 comment='个人基本信息表';



# 机构/个人查询记录明细表
drop table if exists `t_credit_query_record`;
create table `t_credit_query_record`(
  `id` int unsigned primary key auto_increment,
 
  `query_id` smallint not null comment '查询序号',
  `query_type` enum('0','1') comment '0代表个人查询,1代表机构查询',
  `query_time` date not null comment '查询时间',
  `query_operator` varchar(128) not null comment '查询操作员',
  `query_reason` varchar(128) not null comment '查询原因'

)engine=innodb default charset=utf8 auto_increment=1000 comment='机构/个人查询记录明细表';



# 信用卡账户明细表
drop table if exists `t_credit_card_record`;
create table `t_credit_card_record`(
  `id` int unsigned primary key auto_increment,

  `release_date` varchar(32) not null comment '发行日期',
  `bank` varchar(32) not null comment '发行银行',
  `crad_type` varchar(32) not null comment '银行卡类型',
  `account_type` varchar(16) not null comment '账户类型',
  `due_date` varchar(32) not null comment '统计日期(截止日期)',
  `credit_amount` int unsigned not null comment '信用额度',
  `used_amount` int unsigned not null comment '已用额度'

)engine=innodb default charset=utf8 auto_increment=1000 comment='信用卡账户明细表';



