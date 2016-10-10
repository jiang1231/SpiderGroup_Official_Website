#coding=utf-8

import datetime

def getStrMonth(month): # 将月份转为两位的字符串

    month = str(month)
    month = month if len(month) == 2 else '0'+month
    return month
# end

def getMonthSeq():   # 获得近6个月的时间,格式:年+月(两位), demo：201607

    seq = list()
    today = datetime.date.today()
    year = today.year
    month = today.month + 1

    for i in range(6):
        if month-1 > 0:
            month -= 1
            year_month = str(year) + getStrMonth(month)
        else:
            year -= 1
            month = 12
            year_month = str(year) + getStrMonth(month)
        seq.append(year_month)
    # for
    seq.reverse()
    return seq
# end


def test(): # 调用测试

    date_seq = getMonthSeq()
    print date_seq
    # >> ['201602', '201603', '201604', '201605', '201606', '201607']

# end
