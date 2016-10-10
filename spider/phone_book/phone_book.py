#coding=utf-8
"""
Author: moyh
修改为从省开始查询
2016/9/6将协程并发去掉，改为顺序执行以避免过分的超时
"""
import random
import re
import sys
import time
import MySQLdb

sys.path.append('../')
import gevent
import pymongo
from lxml import etree

from threadpool import ThreadPool, makeRequests
from spider.public import userAgent, getIp, basicRequest
from copy import deepcopy
from gevent import monkey; monkey.patch_all()
from _mysql_exceptions import MySQLError

import configuration.root_node as config


_time_out = 6
_thread_num = 3
_host = 'http://www.cc10000.cn'
_paths = ('//body/div[2]/div[5]', '//body/div[4]', '//body/div/div[5]')
_position = ('province', 'city', 'sub_city', 'town_street')

_table_name = 't_phone_book'
_column_names = ('province', 'city', 'sub_city', 'town_street', 'department', 'tel_num')


def getDBConnection():
    return MySQLdb.connect(
        host = 'localhost',
        user = 'root',
        passwd = 'mysql2016',
        db = 'spider',
        charset = 'utf8',
        use_unicode = False  # 不用unicode
    )
# end


class PhoneBook(object):
    """政府部门联络方式-爬虫"""

    client = pymongo.MongoClient()
    spider_db = client.spider
    collection = spider_db.t_phone_book

    def __init__(self):
        self.headers = {
            'Referer': '',
            'User-Agent': userAgent(),
            'Host': 'www.cc10000.cn',
            'Connection': 'keep-alive',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'X-Forwarded-For': getIp(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        self.hrefs = list()

    def initItems(self):
        self.items = list()


    def getProvince(self):
        """ 获得所有省的对应的url
        :return:[[href, province_detail_name],[]...] """
        url = 'http://www.cc10000.cn/0/'
        options = {'method': 'get', 'url': url, 'headers': self.headers, 'timeout':_time_out}
        response = basicRequest(options, resend_times=4)
        selector = etree.HTML(response.text)
        content = etree.tounicode(selector.xpath('//body/div[6]')[0])
        href_and_name = re.findall('href="(/\d.*?)">(.*?)<', content)
        # 仅提取省,并将用详细省名代替简写省名
        seq =  [[i[0], config.ROOT_DETAIL_NAMES[config.ROOT_SHORT_NAMES.index(i[1])]] for i in href_and_name if i[1] in config.ROOT_SHORT_NAMES]
        self.hrefs.extend([index[0] for index in seq])
        return seq
    # end


    def requestURL(self, href):
        """ 请求URL
        :param href: URL
        :param name: 市名/区名
        :return: None """
        # print u'url is {url} , name is {name}'.format(url=url, name=name)
        href = _host + href if _host not in href else href
        options = {'method': 'get', 'url': href, 'headers': self.headers, 'timeout':_time_out}
        response = basicRequest(options, resend_times=4)
        return response
    # end


    def clawHrefs(self, text, name):
        """ 首先匹配出所有的href_name，省下仅提取市
        :param text: str/unicode
        :return: list [(href, department_name),()...]"""
        hrefs = re.findall('href="(/\d.*?)">(\W+)\d*<', text)  # (url,name)
        repeat_hrefs =[href for href in hrefs if href[0] in self.hrefs] # 过滤和首页重复项
        if repeat_hrefs:
            for i in repeat_hrefs:
                hrefs.remove(i)

        if name[-1] in config.ROOT_PROVINCE:
            province_detail_name = name[-1]
            city_names = self.getCityFromDB(province_detail_name)
            result = list()
            for city_name in city_names:
                for i in hrefs:
                    tmp_match = re.match(city_name, i[1].encode('utf-8'))
                    if tmp_match:
                        result.append(i)
                        break
            return result
        return hrefs
    # end


    def clawDetail(self, text, name):
        """ 逐一测试xpath路径,如果找到相应节点
        提取该节点中的部门名+phone，并返回下一级的所有链接href(如何存在)
        :param text: response.text(unicode)
        :param name: list (utf-8)
        :return: list """
        selector = etree.HTML(text)
        for path in _paths:
            node = selector.xpath(path)
            if not node:
                continue
            text = node[0].xpath('text()')   # 提取节点文本
            self.analyseRow(text, name)      # 在文本中提取部门名+phone
            return self.clawHrefs(etree.tounicode(node[0]), name)             # 返回下一级的href
    # end


    def analyseRow(self, text, name):
        """
        :param text: list
        :return: None """
        for tr in text:
            tr = tr.replace('\r\n', '')
            if tr != '':
                rows = tr.split()   # 分割每行的记录
                for row in rows:
                    # old_match: (\W+\w*\W+)(\d+)
                    result  =  re.search('(\W+\w{0,2}\W+\w{0,2}\W+)(\d+[/+-]*\d+)', row)  # 分割联系人/部门 + 联系方式
                    if len(row) < 7 or result is None:
                        continue

                    item = dict()
                    #　区分直辖市和省，直辖市要填充省名
                    temp = deepcopy(name)
                    if temp[0] in config.ROOT_CITY:
                        temp.insert(0, temp[0])
                    try:
                        for i, v in enumerate(temp):
                            item[_position[i]] = v
                    # 该网站存在分层异常
                    except IndexError:
                        continue
                    item['department']= result.group(1)
                    item['tel_num']= result.group(2)
                    self.items.append(item)
        # for
    # end


    def process(self, href, name):
        """
        :param href: 链接
        :param name:[] 第一次传入为详细的省名列表(demo:[广东省])
        :return: None """
        response  = self.requestURL(href)                            # 请求连接
        if not response:
            return
        else:
            href_and_name = self.clawDetail(response.text, deepcopy(name))   # 提取部门名+tel
            if href_and_name:
                # 减缓并发
                # time.sleep(random.uniform(5, 8))
                # objs = list()
                # for i in href_and_name:
                #     i_name = (deepcopy(name))
                #     i_name.append(i[1])
                #     objs.append(gevent.spawn(self.process, i[0], i_name))
                # gevent.joinall(objs)
                for i in href_and_name:
                    i_name = (deepcopy(name))
                    i_name.append(i[1])
                    self.process(i[0], i_name)
    # end


    def start(self):
        pool = ThreadPool(_thread_num)
        href_and_name = self.getProvince() # len =31
        #demo： params_seq = [(['/0/2/0/0/', ['广东省']], None)]
        params_seq = [([i[0], [i[1]]], None) for i in href_and_name]
        # params_seq = [(['/0/2/0/0/', ['广东省']], None)]
        for group in PhoneBook.splitGroups(params_seq, 3):
            self.initItems()
            requests = makeRequests(self.process, group)
            [pool.putRequest(req) for req in requests]
            pool.wait()
            self.saveItems()     # 存储
            time.sleep(random.uniform(2, 5))
        PhoneBook.client.close() # 关闭连接
    # end


    def saveItems(self):
        PhoneBook.collection.insert_many(self.items)
    # end


    @staticmethod
    def splitGroups(seq, step):
        """ :param seq：list
        :param step: int
        :return:lsit
        """
        index = 0
        seq_len =  len(seq)
        while index < seq_len:
            if index+step < seq_len:
                yield seq[index:index+step]
            else:
                yield seq[index:seq_len]
            index += step
    # end splitGroups


    def getCityFromDB(self, province_detail_name):
        """ 根据详细省名到数据库拿到对应的所有城市
        :param province_detail_name: 详细省名(utf-8)
        :return:None """
        conn = getDBConnection()
        cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

        sql = "select id from t_phone_address where areaname = '{0}'".format(province_detail_name)
        cur.execute(sql)
        result = cur.fetchall()
        try:
            if result:
                sql = "select shortname from t_phone_address where parentid = {0}".format(result[0]['id'])
                cur.execute(sql)
                city_names = [i['shortname']for i in cur.fetchall()]
                return city_names
            else:
                print 'ERROR,Not found {0} city'.format(province_detail_name)
        except Exception as ex:
            print ex
        finally:
            cur.close()
            conn.close()
    # end


    def checkSearchCity(self):
        """ 检查各省能否正确找到旗下对应的市
        :return: None """
        for i,v in enumerate(config.ROOT_DETAIL_NAMES):
            city_names = self.getCityFromDB(v)
            print 'no.{0}, province name.{1}, demo city.{2}'.format(i+1,v,city_names[0])


    def checkPosRoot(self):
        """ 验证首页是否可以获得全部的省
        :return: """
        result = self.getProvince()
        print len(result)
        for i in result:
            print i[1]
    # end


def phonebookSpiderAPI():
    phone = PhoneBook()
    phone.start()

if __name__ == '__main__':
    phonebookSpiderAPI()





