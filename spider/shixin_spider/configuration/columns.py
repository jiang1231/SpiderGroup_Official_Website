#coding=utf-8

# 表名
TABEL_NAME_1 = 't_shixin_valid'
TABLE_NAME_2 = 't_shixin_invalid'

# 字典key对应也请求返回内容的key,value对应存储表的字段名
KEY_CONVERT_VALID = {
    'id': 'sys_id',
    'iname': 'name',
    'age': 'age',
    'sexy': 'sex',
    'cardNum':'card_num',
    'businessEntity': 'business_entity',
    'areaName': 'area_name',
    'caseCode': 'case_code',
    'regDate': 'reg_date',
    'publishDate': 'publish_date',
    'gistId': 'gist_id',
    'courtName': 'court_name',
    'gistUnit': 'gist_unit',
    'duty': 'duty',
    'performance': 'performance',
    'disruptTypeName': 'disrupt_type_name',
    'partyTypeName': 'party_type_name'
}

# COLUMN_VALID为表t_shixin_valid对应的字段名
COLUMN_VALID = KEY_CONVERT_VALID.values()
COLUMN_VALID.append('flag')

# COLUMN_INVALID为表t_shixin_invalid对应的字段名
KEY_CONVERT_INVALID = ('sys_id', 'err_type')


