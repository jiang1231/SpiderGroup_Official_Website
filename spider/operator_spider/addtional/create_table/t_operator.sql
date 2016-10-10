use spider;

# 运营商-用户信息表
drop table if exists `t_operator_user`;
create table `t_operator_user`(

    `id` int unsigned primary key auto_increment comment 'id',
    `alter_time` timestamp default current_timestamp on update current_timestamp,

    `name` varchar(64) default null comment '姓名',
    `sex` varchar(8)  default null comment '性别',
    `address` varchar(128) default null comment '地址',
    `cert_type` varchar(32) default '身份证' comment '证件类型',
    `cert_num` varchar(32) default null comment '证件号码',

    `phone` varchar(32)  not null comment '手机号',
    `company` tinyint not null comment '手机号类型[联通1,移动2,电信3]',
    `province` varchar(128) not null comment '归属地-省',
    `city` varchar(128) not null comment '归属地-市',
    `product_name` varchar(64) not null comment '套餐',
    `level` varchar(32) not null comment '用户等级',
    `open_date` varchar(16) default null comment '入网时间/认证时间',
    `balance` varchar(16) default null comment '账户余额',
    
    `user_valid` tinyint default 1 comment '用户当前状态[有效期1,其他0]',
    
     unique key `unique_user`(`cert_num`, `phone`)

)engine=innodb default charset=utf8 auto_increment=1000 comment='运营商-用户信息表';


# 运营商-用户通话记录表
drop table if exists `t_operator_call`;
create table `t_operator_call`(

    `id` int unsigned primary key auto_increment,
    `alter_time` timestamp not null default current_timestamp comment '创建时间',
	
    `cert_num` varchar(32) default null comment '身份证号/指回t_operator_user.cert_num',
    `phone` varchar(32) not null comment '手机号/指回t_operator_user.phone',

    `call_area` varchar(128) not null comment '通话地点 ',
    `call_date` date not null comment '通话日期(年-月-日)',
    `call_time` time not null comment '通话时间(时:分:秒)',
    `call_cost` varchar(32) not null comment '通话费',
    `call_long` varchar(32) not null comment '通话时长',

    `other_phone` varchar(16) not null comment '对方号码 ',
    `call_type` tinyint not null comment '呼叫类型(主叫1,被叫2,其他3)',
    `land_type` tinyint not null comment '通话类型(本地通话1,省内通话2,其他3)',
    
    index `user` (`cert_num`,`phone`) comment '建立索引便于快速inner join',
    unique key `unique_call` (`phone`, `call_date`, `call_time`, `other_phone`)

)engine=innodb default charset=utf8 auto_increment=1000 comment='运营商-通话记录表';


# 运营商-短信记录表
drop table if exists `t_operator_note`;
create table `t_operator_note`(

    `id` int unsigned primary key auto_increment,
    `alter_time` timestamp not null default current_timestamp comment '创建时间',
    
    `cert_num` varchar(32) default null comment '身份证号/指回t_operator_user.cert_num',
    `phone` varchar(32) not null comment '手机号/指回t_operator_user.phone',

    `note_date` date not null comment '短信日期(年-月-日)',
    `note_time` time not null comment '短信时间(时:分:秒)',
    `note_cost` varchar(32) not null comment '短信费用',
    `business_type` varchar(16) not null comment '业务类型',
    `other_phone` varchar(16) not null comment '对方号码 ',

    index `user` (`cert_num`,`phone`) comment '建立索引便于快速inner join',
    unique key `unique_call` (`phone`, `note_date`, `note_time`, `other_phone`)

)engine=innodb default charset=utf8 auto_increment=1000 comment='运营商-短信记录表';


# 营运商-月账单记录表[先不要建,有问题]
drop table if exists `t_operator_charge`;
create table `t_operator_charge`(

    `id` int unsigned primary key auto_increment,
    `alter_time` timestamp not null default current_timestamp comment '创建时间',
    
    `cert_num` varchar(32) default null comment '身份证号/指回t_operator_user.cert_num',
    `phone` varchar(32) not null comment '手机号/指回t_operator_user.phone',

    `month` varchar(20) not null comment '月份',
    `charge` varchar(20) not null comment '费用',

    index `user` (`cert_num`,`phone`) comment '建立索引便于快速inner join'
#     unique key `unique_call` (`phone`, `note_time`, `other_phone`)

)engine=innodb default charset=utf8 auto_increment=1000 comment='营运商-月账单记录表';