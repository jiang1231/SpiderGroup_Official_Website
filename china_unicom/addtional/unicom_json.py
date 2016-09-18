#coding=utf-8
import json

def parseUserJson(text, part_info):
    #login_name, password, name,   sex,    address, cert_type, cert_id,
    # phone,     home,       brand, level,  status, open_date, balance, puk_id,

    # 从接口来， 从接口来， custname, custsex, certaddr,certtype, 前拿,
    # usernumber,certaddr,   brand, custlvl, 外层取，前拿,       前拿，   外层

    result = json.loads(text, encoding='utf-8')['result']

    try:
        status = result['usercirclestatus']
    except KeyError:
        status = u'页面无明确提示'

    puk_id = result['pukcode']
    mydetail =  result['MyDetail']

    return (
        part_info['user_name'], part_info['password'], mydetail['custname'], mydetail['custsex'],
        mydetail['certaddr'], mydetail['certtype'], part_info['cert_id'], mydetail['usernumber'],
        part_info['home'], mydetail['brand'], mydetail['custlvl'], status, part_info['open_date'], part_info['balance'], puk_id
    )
# end



def parseCallJson(seq):

    # cert_id, phone, call_area,   call_date, call_time, call_cost, call_long,   other_phone, call_type,   land_type
    # certnum, phone,homeareaName,calldate,  calltime,  totalfee,  calllonghour,  other_num,  calltypeName,landtype

    rows = list()
    field_seq = ('homeareaName', 'calldate', 'calltime', 'totalfee',
                'calllonghour', 'othernum', 'calltypeName', 'landtype')

    for text in seq:
        try:
            result = json.loads(text, encoding='utf-8')
        except (KeyError,ValueError,Exception):
            continue
        if 'errorMessage' in result.keys(): # 没有数据
            continue
        else:
            certId_and_phone = [result['userInfo']['certnum'], result['userInfo']['usernumber']]
            results = result['pageMap']['result']   # results is a list which contains lots of dict
            for i in results:
                row = certId_and_phone + [i[x] for x in field_seq]
                rows.append(row)
            # for
    # for
    return rows
# end
