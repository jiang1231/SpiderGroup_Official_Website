#coding=utf-8
import MySQLdb

def getDbConnect():
    return MySQLdb.connect(host='localhost',user='root',passwd='mysql2016',db='spider',charset='utf8')
# end

def t_china_unicom_call_insert(rows):

    conn = getDbConnect()
    cur = conn.cursor()
    try:
        insert_sql = 'INSERT INTO t_china_unicom_call ' \
                     '(cert_id,' \
                     ' phone, call_area, call_date, call_time, call_cost, call_long, ' \
                     'other_phone, call_type, land_type) ' \
                     'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cur.executemany(insert_sql,rows)
        conn.commit()
    except Exception as ex:
        conn.rollback()
        print ex
        return dict(result=False, error='t_china_unicom_call_insert{0}'.format(ex))
    else:
        print '插入通话记录数据成功'
        return dict(result=True, error='t_china_unicom_call_insert{0}'.format('no error'))
    finally:
        cur.close()
        conn.close()
# end


def t_china_unicom_user_insert(row):    #_mysql_exceptions.IntegrityError

    conn = getDbConnect()
    cur = conn.cursor()

    try:
        insert_sql = 'INSERT INTO t_china_unicom_user ' \
                     '(login_name, password, ' \
                     'name, sex, address, cert_type, cert_id, ' \
                     'phone, home, brand, level, status, open_date, balance, puk_id) ' \
                     'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cur.execute(insert_sql,row)
        conn.commit()
    except Exception as ex:
        conn.rollback()
        print ex
        return dict(result=False, error='t_china_unicom_user_insert{0}'.format(ex))
    else:
        print '插入用户数据成功'
        return dict(result=True,error='t_china_unicom_user_insert{0}'.format('no error'))
    finally:
        cur.close()
        conn.close()
# end




