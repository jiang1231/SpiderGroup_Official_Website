#coding=utf-8
import json

def parseCallJson(seq,id_and_phone):

    # cert_id, phone, call_area,   call_date, call_time, call_cost, call_long,   other_phone, call_type,   land_type
    # certnum, phone, place ,      time,      time,      chargefee, period,      contnum,     becall,      conttype

    rows = list()
    field_seq = ('place', 'time', 'time', 'chargefee',
                'period', 'contnum', 'becall', 'conttype')

    for text in seq:
        try:
            results = json.loads(text, encoding='utf-8')['content']['realtimeListSearchRspBean']['calldetail']['calldetaillist']
        except (KeyError,ValueError, Exception)as error:
            print 'parse_json have key_error:',error
            continue
        if len(results) > 0:
            for i in results:
                row = id_and_phone + [i[x] for x in field_seq]
                try:
                    temp =  row[3].split(' ')       # '04-01 11:18:50' 对时间进行分割
                    row[3] = '2016-' + temp[0]
                    row[4] = temp[1]
                except Exception as ex:

                    print '对日期或时间分割失败'
                    print ex
                # try
                rows.append(row)
            # for
        else:
            continue
    # for
    return rows
# end


