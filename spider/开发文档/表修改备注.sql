# 修改t_shixin_valid的索引
alter table t_shixin_valid drop index com_or_person; 
alter table t_shixin_valid add index `search`(`name`, `card_num`, `flag`);

# 修改t_shixin_invalid的索引
alter table t_shixin_invalid drop index re_err; 
alter table t_shixin_invalid add index `search`(`err_type`, `flag`);

# 备注
# 目前无法对被执行人数据进行分类[公司/个人]
alter table t_zhixing_valid add index `search`(`name`, `card_num`);
alter table t_zhixing_invalid add index `search`(`err_type`, `flag`);
# 运营商表通用一份


#2016-10-09
alter table t_shixin_valid drop index search;
alter table t_shixin_valid add index `search`(`name`, `card_num`, `area_name`, `flag`);