#coding=utf-8


# t_operator_user 用户记录表
# t_operator_call 通话记录表
# t_operator_note 短信记录表
result = {

    't_operator_user':[
    {'province': u'\u5e7f\u4e1c', 'city': u'\u6df1\u5733', 'password': '251314', 'name': u'\u83ab\u827a\u534e', 'level': u'\u65e0\u7b49\u7ea7', 'company': 1, 'cert_type': u'18\u4f4d\u8eab\u4efd\u8bc1', 'sex': u'\u7537', 'phone': '13267175437',
     'address': u'\u5e7f\u4e1c\u7701\u6df1\u5733\u5e02\u5b9d\u5b89\u533a\u897f\u4e61\u8857\u9053\u897f\u4e61\u94f6\u7530\u65b0\u6751\u4e09\u6392\u516d\u53f7\uff08\u5de5\u4f5c\u65e5\u8bf7\u60e0\u76ca\u5546\u5e97\u4ee3\u6536\uff09', 'user_valid': 1, 
     'open_date': u'2016\u5e7407\u670804\u65e5', 'balance': u'62.58', 'product_name': u'(OCS)\u6d41\u91cf\u65e5\u79df\u5361(0.19\u5143\u7248)', 'cert_num': u'4409****3451'}
     ],
    #时间（年月日） 呼叫类型（本地通话1,省内通话2,其他3） 通话金额  时间（时分秒） 通话时长 对方号码
    't_operator_call':[
    {'call_date': u'2016-09-16', 'land_type': 2, 'call_cost': u'1.45', 'call_time': u'21:43:19', 'call_long': u'4\u520655\u79d2', 'phone': '13267175437', 'other_phone': u'15016631215', 'call_area': u'\u6df1\u5733', 'call_type': 1, 'cert_num': u'4409****3451'},
    {'call_date': u'2016-09-16', 'land_type': 1, 'call_cost': u'0.00', 'call_time': u'13:24:14', 'call_long': u'7\u79d2', 'phone': '13267175437', 'other_phone': u'008615107141786', 'call_area': u'\u6df1\u5733', 'call_type': 2, 'cert_num': u'4409****3451'},
    {'call_date': u'2016-08-13', 'land_type': 1, 'call_cost': u'0.00', 'call_time': u'10:35:56', 'call_long': u'14\u79d2', 'phone': '13267175437', 'other_phone': u'008615776452135', 'call_area': u'\u6df1\u5733', 'call_type': 1, 'cert_num': u'4409****3451'},
    {'call_date': u'2016-08-08', 'land_type': 2, 'call_cost': u'0.00', 'call_time': u'17:58:05', 'call_long': u'7\u79d2', 'phone': '13267175437', 'other_phone': u'008618016717843', 'call_area': u'\u6df1\u5733', 'call_type': 2, 'cert_num': u'4409****3451'},
    {'call_date': u'2016-07-03', 'land_type': 1, 'call_cost': u'0.19', 'call_time': u'19:12:35', 'call_long': u'53\u79d2', 'phone': '13267175437', 'other_phone': u'13510450540', 'call_area': u'\u6df1\u5733', 'call_type': 1, 'cert_num': u'4409****3451'},
    {'call_date': u'2016-07-20', 'land_type': 2, 'call_cost': u'0.00', 'call_time': u'18:51:04', 'call_long': u'20\u79d2', 'phone': '13267175437', 'other_phone': u'008675588698827', 'call_area': u'\u6df1\u5733', 'call_type': 2, 'cert_num': u'4409****3451'},
    {'call_date': u'2016-06-19', 'land_type': 1, 'call_cost': u'0.19', 'call_time': u'21:20:57', 'call_long': u'9\u79d2', 'phone': '13267175437', 'other_phone': u'13682640328', 'call_area': u'\u6df1\u5733', 'call_type': 1, 'cert_num': u'4409****3451'},
    {'call_date': u'2016-06-19', 'land_type': 2, 'call_cost': u'1.16', 'call_time': u'20:21:17', 'call_long': u'3\u520657\u79d2', 'phone': '13267175437', 'other_phone': u'15016631215', 'call_area': u'\u6df1\u5733', 'call_type': 2, 'cert_num': u'4409****3451'},
    {'call_date': u'2016-05-11', 'land_type': 1, 'call_cost': u'2.32', 'call_time': u'13:52:35', 'call_long': u'7\u520611\u79d2', 'phone': '13267175437', 'other_phone': u'15016631215', 'call_area': u'\u6df1\u5733', 'call_type': 1, 'cert_num': u'4409****3451'},
    {'call_date': u'2016-05-11', 'land_type': 2, 'call_cost': u'0.29', 'call_time': u'13:51:59', 'call_long': u'11\u79d2', 'phone': '13267175437', 'other_phone': u'15016631215', 'call_area': u'\u6df1\u5733', 'call_type': 2, 'cert_num': u'4409****3451'},
    {'call_date': u'2016-04-05', 'land_type': 1, 'call_cost': u'0.00', 'call_time': u'15:24:01', 'call_long': u'7\u520630\u79d2', 'phone': '13267175437', 'other_phone': u'008613929536903', 'call_area': u'\u6df1\u5733', 'call_type': 1, 'cert_num': u'4409****3451'},
    {'call_date': u'2016-04-05', 'land_type': 2, 'call_cost': u'0.29', 'call_time': u'15:02:17', 'call_long': u'23\u79d2', 'phone': '13267175437', 'other_phone': u'15016631215', 'call_area': u'\u6df1\u5733', 'call_type': 1, 'cert_num': u'4409****3451'},
    ] * 20,
    't_operator_note':  [
#时间 手机号码 短信费用 业务类型对方号码
    {'cert_num': u'4409****3451', 'phone': '13267175437', 'note_date': u'2016-09-03', 'note_time': u'22:43:23' , 'note_cost': u'0.1', 'business_type': u'国内短信', 'other_phone': '10086'},
    {'cert_num': u'4409****3451', 'phone': '13267175437', 'note_date': u'2016-08-03', 'note_time': u'22:43:23' , 'note_cost': u'0.1', 'business_type': u'国内短信', 'other_phone': '10086'},
    {'cert_num': u'4409****3451', 'phone': '13267175437', 'note_date': u'2016-07-03', 'note_time': u'22:43:23' , 'note_cost': u'0.1', 'business_type': u'国内短信', 'other_phone': '10086'},
    {'cert_num': u'4409****3451', 'phone': '13267175437', 'note_date': u'2016-06-03', 'note_time': u'22:43:23' , 'note_cost': u'0.1', 'business_type': u'国内短信', 'other_phone': '10086'},
    {'cert_num': u'4409****3451', 'phone': '13267175437', 'note_date': u'2016-05-03', 'note_time': u'22:43:23' , 'note_cost': u'0.1', 'business_type': u'国内短信', 'other_phone': '10086'},
    {'cert_num': u'4409****3451', 'phone': '13267175437', 'note_date': u'2016-04-03', 'note_time': u'22:43:23' , 'note_cost': u'0.1', 'business_type': u'国内短信', 'other_phone': '10086'}
] * 20
}





if __name__ == '__main__':
    for k, v in result['t_operator_call'][0].items():
        print k, v
