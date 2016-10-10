#coding=utf-8
import datetime

def _getStrMonth(month): # 将月份转为两位的字符串

    month = str(month)
    month = month if len(month) == 2 else '0'+month
    return month
# end


def getMonthSeq():   # 获得近6个月的时间

    seq = list()
    today = datetime.date.today()
    year = today.year
    month = today.month + 1

    for i in range(6):
        if month-1 > 0:
            month -= 1
            year_month = str(year) + '-' + _getStrMonth(month)
        else:
            year -= 1
            month = 12
            year_month = str(year) + '-' + _getStrMonth(month)

        seq.append(year_month)

    return seq
# end

if __name__ == '__main__':
    print getMonthSeq()
