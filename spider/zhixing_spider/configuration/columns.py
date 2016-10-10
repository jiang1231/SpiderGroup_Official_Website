#coding=utf-8

# 表名
TABEL_NAME_1 = 't_zhixing_valid'
TABLE_NAME_2 = 't_zhixing_invalid'

# 字典key对应也请求返回内容的key,value对应存储表的字段名
KEY_COLUMN = {
    'id': 'sys_id',
    'pname': 'name',
    'partyCardNum': 'card_num',
    'caseCode': 'case_code',
    'caseCreateTime': 'reg_date',
    'execCourtName': 'court_name',
    'execMoney': 'execute_money'
}
# COLUMN_VALID为表t_zhixing_valid对应的字段名
COLUMN_VALID = KEY_COLUMN.values()

# COLUMN_INVALID为表t_zhixing_invalid对应的字段名
COLUMN_INVALID = ('sys_id', 'err_type')