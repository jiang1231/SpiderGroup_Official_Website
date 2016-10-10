#coding=utf-8
"""
Author: moyh
Date:   2016/9/7
alter:  集合多个几口版本
"""
import re
import json
import time

from math import ceil
import gevent
from lxml import etree
from requests.utils import dict_from_cookiejar

import spider.public.db_config as DB
import configuration.columns as config
from spider.public import userAgent, basicRequest,\
    getIp, recogImage, makeDirs, clawLog, returnResult


class ShiXinSpider(object):
    """失信人记录spider"""
    def __init__(self, name, card_num):
        self.headers = {
            'Referer': '',
            'X-Forwarded-For': getIp(),
            'User-Agent':  userAgent(),
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'shixin.court.gov.cn',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        self.cookies = dict()           # 全局cookies
        self.name = name                # 个人姓名/公司名
        self.card_num = card_num        # 身份证号/企业号
        self.id_seq = list()            # 查询结果id序列
        self.valid_items = list()       # 有效记录
        self.invalid_items = list()     # 无效记录
    # end


    def getCookies(self):
        """ 获取cookies
        :return: dict obj/False
        """
        def visitSys():
            url = 'http://shixin.court.gov.cn/'
            options = {'method': 'get', 'url':url, 'headers': self.headers}
            response = basicRequest(options)
            if response:
                self.cookies.update(dict_from_cookiejar(response.cookies))
                # invoke next process
                return getSessionID()
            else:
                return False
        # def

        def getSessionID():
            url = 'http://shixin.court.gov.cn/image.jsp'
            self.headers['Referer'] = 'http://shixin.court.gov.cn/'
            options = {'method': 'get', 'url': url, 'cookies': self.cookies, 'headers': self.headers}
            response = basicRequest(options)
            if response:
                self.cookies.update(dict_from_cookiejar(response.cookies))
                #invoke next process
                return getONEAPM_AI()
            else:
                return False
        # def

        def getONEAPM_AI():
            url = 'http://shixin.court.gov.cn/visit.do'
            self.headers['Referer'] = 'http://shixin.court.gov.cn/'
            options = {'method': 'get', 'url': url, 'cookies': self.cookies, 'headers': self.headers}
            response = basicRequest(options)
            if response:
                self.cookies.update(dict_from_cookiejar(response.cookies))
                return self.cookies
            else:
                return False
        # def
        return visitSys()
    # end updateCookies

    def getCode(self, re_num=2):
        """ 获取验证码
        :return: 识别结果/False
        """
        result = time.ctime().split()
        url =   'http://shixin.court.gov.cn/image.jsp?' \
                'date={0}%20{1}%20{2}%20{3}%20{4}%20GMT' \
                '+0800%20(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)'\
                .format(result[0],result[1],result[2],result[4],result[3])

        self.headers['Accept'] = 'image/webp,image/*,*/*;q=0.8'
        self.headers['Referer'] = 'http://shixin.court.gov.cn/'
        options = {'method': 'get', 'url': url, 'cookies': self.cookies, 'headers': self.headers}
        response = basicRequest(options)
        if response and len(response.text):
            self.cookies.update(dict_from_cookiejar(response.cookies))
            pw_code = recogImage(response.content)
            if pw_code:
                return pw_code
            else:
                re_num -= 1
                return self.getCode( re_num) if re_num > 0 else False
        else:
            re_num -= 1
            return self.getCode( re_num) if re_num > 0 else False
    # end

    def searchByCardNumAndName(self, pw_code, re_num=2):
        """ 通过身份证号/公司号查记录,提取当前页的所有id
        :return: int
        """
        form = {
            'pProvince': '0',
            'pCode': pw_code,
            'pName': self.name,
            'pCardNum': self.card_num
        }
        url = 'http://shixin.court.gov.cn/findd'
        self.headers['Referer'] = 'http://shixin.court.gov.cn/'
        options = {'method': 'post', 'url': url, 'form': form,
                   'cookies': self.cookies, 'headers': self.headers}

        response = basicRequest(options)
        if response:
            page_num = 0
            selector = etree.HTML(response.content)
            text = selector.xpath('//div[@id="ResultlistBlock"]/div/text()')
            text = ''.join(text).replace('\n','').replace('\t','').encode('utf-8')
            try:
                tr_num = int(re.search('共(\d+)', text).group(1)) #　记录总数
            except AttributeError:
                re_num -= 1
                pw_code = self.getCode()
                return self.searchByCardNumAndName(pw_code, re_num) if re_num > 0 else False
            else:
                if tr_num > 0:
                    page_num = int(ceil((tr_num)/10.0)) # 总页数
                    sys_ids = self.findIDs(selector)
                    self.id_seq.extend(sys_ids)
                return dict(page_num=page_num, pw_code=pw_code)
    # end

    def findIDs(self, selector):
        """ :param selector:
        :return: list
        """
        trs = selector.xpath('//table[@id="Resultlist"]/tbody/tr')[1:]
        return [tr.xpath('td[5]/a/@id')[0] for tr in trs]
    # end findIDs

    def changePage(self, pw_code, page_i):
        """ 转换page,提取当前页的所有id
        :param pw_code: 验证码
        :param page_i: 第i页
        :return:None
        """
        form = {
            'pProvince': '0',
            'pCode':  pw_code,
            'currentPage':page_i,
            'pName':  self.name,
            'pCardNum': self.card_num,
        }
        url = 'http://shixin.court.gov.cn/findd'
        self.headers['Referer'] = 'http://shixin.court.gov.cn/findd'
        options = {'method':'post', 'url':url, 'form':form,
                   'cookies':self.cookies, 'headers':self.headers}

        response = basicRequest(options)
        if response:
            selector = etree.HTML(response.content)
            sys_ids = self.findIDs(selector)
            self.id_seq.extend(sys_ids)
    # end

    def saveErrID(self, sys_id, err_type):
        """:param sys_id: 单个id或者list,tuple
        :param err_type:
        :return:None
        """
        if err_type not in (1, 2, 3):
            raise ValueError(u'错误类型范围不在定义范围')

        if isinstance(sys_id, (list, tuple)):
            for i in sys_id:
                error = dict(sys_id = i, err_type = err_type)
                self.invalid_items.append(error)
        else:
            error = dict(sys_id = sys_id, err_type = err_type)
            self.invalid_items.append(error)
    # end

    def getJson(self, sys_id, pw_code, re_num=2):
        """  获得sys_id对应的信息
        :param pw_code: 验证码
        :return: None
        """
        params = {'id':sys_id, 'pCode':pw_code}
        url = 'http://shixin.court.gov.cn/findDetai'
        self.headers['Referer'] = 'http://shixin.court.gov.cn/'

        options = {'method': 'get', 'params':params, 'url': url,
                   'cookies': self.cookies, 'headers': self.headers, 'timeout':1 }
        response = basicRequest(options)
        if response and response.status_code not in (520, 500) and len(response.text):
            try:
                item = json.loads(response.text, encoding='utf-8')
            except (ValueError, Exception):
                self.saveErrID(sys_id, 3)
            else:
                result = dict()
                for k, v in item.items():
                    if k in config.KEY_CONVERT_VALID.keys():
                        key = config.KEY_CONVERT_VALID[k]
                        result[key] = v
                result['flag']  = 1 if 'businessEntity' in item.keys() else 0
                self.valid_items.append(result)
        else:
            re_num -= 1
            return self.getJson(sys_id, pw_code, re_num) if re_num > 0 else False
    # end

    def saveItems(self):
        """  保存数据到mysql
        :return: None
        """
        valid_num  = len(self.valid_items)
        invalid_num = len(self.invalid_items)

        if valid_num:
            DB.insertDictList(config.TABEL_NAME_1, config.COLUMN_VALID, self.valid_items)
        if invalid_num:
            DB.insertDictList(config.TABLE_NAME_2, config.KEY_CONVERT_INVALID, self.invalid_items)

        return u'完成入库：有效信息{0}，错误信息{1}'.format(valid_num, invalid_num)
    # end


def shixinSearchAPI(name, card_num='', api_type=1):
    """ 查询接口,名称必须,证件号可缺省
    :param name: 名称
    :card_num: 证件号
    :api_type: 1为调用协程版本，其他为流程版
    :return: dict(t_shixin_valid=[], t_shixin_invalid=[]) / {}
    """
    # makeDirs()

    spider = ShiXinSpider(name, card_num)
    cookie = spider.getCookies()
    if not cookie: # 获取cookies识别
        return returnResult(4000, data={})

    pw_code = spider.getCode()
    if not pw_code: # 获取验证码识别
        return returnResult(4200, data={})

    result = spider.searchByCardNumAndName(pw_code)
    if not result:
        return returnResult(4800, data={})

    if result['page_num'] > 1:
        if api_type == 1:
            objs = list()
            for page_i in range(2, result['page_num']+1):
                objs.append(gevent.spawn(spider.changePage, result['pw_code'], page_i))
            gevent.joinall(objs)
        else:
            for page_i in range(2, result['page_num']+1):
                spider.changePage(result['pw_code'], page_i)

    if spider.id_seq:
        if api_type == 1:
            objs = list()
            for sys_id in spider.id_seq:
                objs.append(gevent.spawn(spider.getJson, sys_id , result['pw_code']))
            gevent.joinall(objs)
        else:
            for sys_id in spider.id_seq:
                spider.getJson(sys_id , result['pw_code'])

    # log = spider.saveItems()
    # clawLog(spider.id_seq, log)

    data = dict(
        t_shixin_valid=spider.valid_items,
        t_shixin_invalid=spider.invalid_items
    )
    return returnResult(2000, data=data) # 流程成功
# end


if __name__ == '__main__':
    # demo
    t_begin = time.time()
    print time.ctime() + ':\t' + 'Test start, running'

    card_num = '72217220X'
    name = '遵义侨丰房地产开发有限责任公司'
    # card_num = ''
    # name = u'毛泽东'

    results = shixinSearchAPI(name, card_num)
    print time.ctime() + ':\t' + 'Test over, cost: {0} seconds\n\n'.format(time.time()-t_begin)
    print results









