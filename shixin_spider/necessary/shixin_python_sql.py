#coding=utf-8
import  MySQLdb


def _getDBConnection():
    """ 建立连接并返回
    :return：DB Connection Object
    """
    return MySQLdb.connect(
            host = 'localhost',
            user = 'root',
            passwd = 'mysql2016',
            db = 'spider',
            charset = 'utf8'
    )
# end


def queryRequestFailID(num):
    """ 从表读取num个id,并删除该记录
    :param num: id数
    :return: IDList/[]
    """
    conn =  _getDBConnection()
    cur = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)

    sql = 'select sys_id from t_shixin_invalid where err_type in (1,2) and flag=1 limit {0}'.format(num)
    cur.execute(sql)
    ids = [int(item['sys_id']) for item in cur.fetchall()]

    if ids:
        sql = 'delete from t_shixin_invalid where sys_id in {0}'.format(str(tuple(ids)))
        cur.execute(sql)

    cur.close()
    conn.commit()
    conn.close()
    return ids
# end


def updateIDstatus(id_seq):
    """ 根据id列表或者tuple更新表
    :param id_seq: list or tuple
    :return: True or False
    """
    conn =  _getDBConnection()
    cur = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)

    if not isinstance(id_seq, (tuple,list)):
        raise ValueError(u'参数错误')

    sql = 'update t_shixin_invalid set flag=0 where sys_id in {0}'.format(str(tuple(id_seq)))

    cur.execute(sql)
    cur.close()
    conn.commit()
    conn.close()
# end


def queryErrUnknownID(num):
    """ 从表读取num个可能不存在内容的id
    :param num: id数
    :return: IDList/[]
    """
    conn =  _getDBConnection()
    cur = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)

    sql = 'select sys_id from t_shixin_invalid where err_type=3 and flag=1 limit {0}'.format(num)
    cur.execute(sql)
    id_seq = [int(item['sys_id']) for item in cur.fetchall()]

    cur.close()
    conn.close()
    return id_seq
# end


def deleteErrItems(id_seq):
    """ 从错误表中删除存在内容的id记录
    :param id_seq: list/tuple
    :return: None
    """
    conn =  _getDBConnection()
    cur = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)

    sql = 'delete from t_shixin_invalid  where sys_id in {0}'.format(str(tuple(id_seq)))
    cur.execute(sql)

    cur.close()
    conn.commit()
    conn.close()
# end


def queryLostID(start_id, end_id):
    """ 获得区间[start_id, end_Id]不在表中的记录的id
    :return: list/[]
    """
    sys_ids = list()
    conn = _getDBConnection()
    cur = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)

    tables = ('t_shixin_valid', 't_shixin_invalid')
    sql = 'select sys_id from {table} where sys_id between start_id and end_id'

    for table in tables:
        cur.execute(sql.format(table=table))
        for item in cur.fetchall():
            sys_ids.append(item['sys_id'])
    cur.close()
    conn.close()
    #3307986为当前数据的最小id, 4825018为最大id
    return list(set(range(start_id, end_id+1)) - set(sys_ids))
# end


if __name__ == '__main__':

    result = queryRequestFailID(200)
    # result = queryErrUnknownID(10)
    while result:
        result = queryRequestFailID(400)
        print result
