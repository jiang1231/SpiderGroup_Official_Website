#coding=utf-8
"""
Author: moyh
Date:   2016/9/7
alter:  变更为流程[没有线程/协程]
"""
import re
import sys
import json
import time
import random
from math import ceil
import gevent
from lxml import etree
import spider.public.db_config as DB
import configuration.columns as config
from requests.utils import dict_from_cookiejar
from spider.public import basicRequest, userAgent,\
    getIp, recogImage, clawLog, makeDirs, returnResult


_timeout = 10

class ZhiXingSpider(object):
    """根据身份证号/企业号查询执行信息,流程版"""
    def __init__(self, name, card_num):
        self.headers = {
            'Referer': '',
            'User-Agent': userAgent(),
            'Connection': 'keep-alive',
            'Host': 'zhixing.court.gov.cn',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'X-Forwarded-For': getIp(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        self.cookies = dict()           # "全局"cookies
        self.name = name                # 个人姓名/公司名
        self.card_num = card_num        # 身份证号/企业号
        self.id_seq = list()            # 查询结果id序列
        self.valid_items = list()       # 有效id
        self.invalid_items = list()     # 无效/出错id
    # end


    def getCookies(self):
        """ 获取cookies流程（嵌套函数）
        :return: dict/False
        """
        def visitSys():
            url = 'http://zhixing.court.gov.cn/search/'
            options = {'method':'get', 'url':url, 'headers':self.headers}

            response = basicRequest(options)
            if response:
                self.cookies.update(dict_from_cookiejar(response.cookies))
                # invoke next process
                return getSessionID()
            else:
                return False
        # def

        def getSessionID():
            url_one = 'http://zhixing.court.gov.cn/search/security/jcaptcha.jpg?87'
            self.headers['Referer'] = 'http://zhixing.court.gov.cn/'
            options_one = {'method':'get', 'url':url_one, 'cookies':self.cookies, 'headers':self.headers}

            response =  basicRequest(options_one)
            if response:
                self.cookies.update(dict_from_cookiejar(response.cookies))
                #invoke next process
                return self.cookies
            else:
                return False
        # def

        return visitSys()
    # getCookies

    def getCode(self, re_num=2):
        """ 获得验证码
        :return: int/False
        """
        self.headers['Referer'] = 'http://zhixing.court.gov.cn/search/'
        url =  'http://zhixing.court.gov.cn/search/security/jcaptcha.jpg?' + str(random.randint(0,99))
        options = {'method':'get', 'url':url, 'cookies':self.cookies, 'headers':self.headers}

        response = basicRequest(options)
        if response and len(response.text):
            self.cookies.update(dict_from_cookiejar(response.cookies))
            pw_code = recogImage(response.content)
            if pw_code:
                return pw_code
            else:
                re_num -= 1
                return self.getCode(re_num) if re_num > 0 else False
        else:
            re_num -= 1
            return self.getCode(re_num) if re_num > 0 else False
    # end getNoteCode

    def searchByCardNum(self, re_num=2):
        """ 通过身份证号/公司号查记录
        :return: 页总数
        """
        pw_code = self.getCode()
        if not pw_code:
            re_num -= 1
            return self.searchByCardNum(re_num) if re_num > 0 else False

        form = {
            'searchCourtName': '全国法院（包含地方各级法院）',
            'selectCourtId': '1',
            'selectCourtArrange': '1',
            'pname': self.name,
            'cardNum': self.card_num,
            'j_captcha': pw_code
        }
        url = 'http://zhixing.court.gov.cn/search/newsearch'
        self.headers['Referer'] = 'http://zhixing.court.gov.cn/search/'
        options = {'method':'post', 'url':url, 'form':form, 'timeout':_timeout,
                   'cookies':self.cookies, 'headers':self.headers}

        response = basicRequest(options, resend_times=0)
        if response:
            checkout = self.checkOut(response.text)
            if not checkout:
                re_num -= 1
                return self.searchByCardNum(re_num)if re_num > 0 else False
            else:
                page_num = 0
                selector = etree.HTML(response.text)
                text = selector.xpath('//div[@id="ResultlistBlock"]/div/text()')
                text = ''.join(text).replace('\n','').replace('\t','').encode('utf-8')
                tr_num = int(re.search('共(\d+)', text).group(1))
                if tr_num > 0:
                    page_num = int(ceil((tr_num)/10.0))
                    sys_ids = self.findIDs(selector)
                    self.id_seq.extend(sys_ids)
                return page_num
    # end

    def findIDs(self, selector):

        trs = selector.xpath('//table[@id="Resultlist"]/tbody/tr')[1:]
        return [tr.xpath('td[5]/a/@id')[0] for tr in trs]
    # end


    def changePage(self, page_i, re_num=2):

        pw_code = self.getCode()
        if not pw_code:
            re_num -= 1
            return self.changePage(page_i, re_num) if re_num > 0 else False

        form = {
            'currentPage': page_i,
            'selectCourtId': '1',
            'selectCourtArrange': '1',
            'pname': self.name,
            'cardNum': self.card_num
        }
        url = 'http://zhixing.court.gov.cn/search/newsearch?j_captcha=' + pw_code
        self.headers['Referer'] = 'http://zhixing.court.gov.cn/search/'
        options = {'method':'post', 'url':url, 'form':form, 'timeout':_timeout,
                   'cookies': self.cookies, 'headers':self.headers}

        response = basicRequest(options, resend_times=0)
        if response:
            checkout = self.checkOut(response.text)
            if not checkout:
                re_num -= 1
                return self.changePage(page_i, re_num) if re_num > 0 else False
            else:
                selector = etree.HTML(response.text)
                sys_ids = self.findIDs(selector)
                self.id_seq.extend(sys_ids)
        else:
            re_num -= 1
            return self.changePage(page_i, re_num) if re_num > 0 else False
    # end

    def checkOut(self, text):
        """ 通过页面返回内容检查验证码是否出错,
        正确返回True,否则返回False
        :param text:response.text
        :return:True/False
        """
        selector = etree.HTML(text)
        title = selector.xpath('//title/text()')[0]
        checkout = re.match('验证码出现错误', title.encode('utf-8'))
        # if checkout:
        #     print checkout.group()
        return False if checkout else True
    # end

    def saveErrID(self, sys_id, err_type):
        """ 保存出错的id,和对应的错误类型
        1位请求错误/2为超时/3为未知错误
        :param sys_id: id
        :param err_type: 1/2/3
        :return: None
        """
        if err_type not in (1,2,3):
            raise ValueError
        err_item = dict(sys_id=sys_id,err_type=err_type)
        self.invalid_items.append(err_item)
        return False
    # end

    def getJson(self, sys_id, re_num=2):
        """  获得id对应的被执行信息（json格式）
        :param sys_id: id
        :return: None
        """
        pw_code = self.getCode()
        if not pw_code:
            re_num -= 1
            return self.getJson(sys_id, re_num) if re_num > 0 else self.saveErrID(sys_id, 1)

        params = {'id':sys_id, 'j_captcha':pw_code}
        url = 'http://zhixing.court.gov.cn/search/newdetail'
        self.headers['Referer'] = 'http://zhixing.court.gov.cn/search/'
        options = {'method': 'get', 'params':params, 'url': url, 'timeout':_timeout,
                   'cookies': self.cookies, 'headers': self.headers}

        response = basicRequest(options, resend_times=0)
        if response and len(response.text) > 10:
            try:
                item = json.loads(response.text, encoding='utf-8')
            except (ValueError,Exception):
                self.saveErrID(sys_id, 3)
            else:
                result = dict()
                for k, v in item.items():
                    if k in config.KEY_COLUMN.keys():
                        key = config.KEY_COLUMN[k]
                        result[key] = v
                self.valid_items.append(result)
        else:
            re_num -= 1
            return self.getJson(sys_id, re_num) if re_num > 0 else self.saveErrID(sys_id, 3)
    # end

    def saveItems(self):
        """ 保存数据到mysql
        :return: None
        """
        valid_num  = len(self.valid_items)
        invalid_num = len(self.invalid_items)

        if valid_num:
            DB.insertDictList(config.TABEL_NAME_1, config.COLUMN_VALID, self.valid_items)
        if invalid_num:
            DB.insertDictList(config.TABLE_NAME_2, config.COLUMN_INVALID, self.invalid_items)

        return u'完成入库：有效信息{0}，错误信息{1}'.format(valid_num, invalid_num)
    # end saveItems

# class


def zhixingSearchAPI(name='', card_num='', api_type=0):
    """ 根据身份证号/企业号查询接口
    :param card_num:身份证号/企业号
    :return: dict(t_zhixing_valid=[], t_zhixing_invalid=[])
    """
    # makeDirs()
    if not name and not name:
        return returnResult(4400, data={})

    spider = ZhiXingSpider(name, card_num)
    page_num = spider.searchByCardNum()

    if page_num > 1:
        for page in  range(2, page_num+1):
            spider.changePage(page)

    if spider.id_seq:
        if api_type == 1:
            print u'并发版本暂停使用,返回数据为空'
        else:
            for sys_id in spider.id_seq:
                spider.getJson(sys_id)

    # result = spider.saveItems()
    # clawLog(spider.id_seq, result)

    data =  dict(
        t_zhixing_valid = spider.valid_items,
        t_zhixing_invalid = spider.invalid_items
    )
    return returnResult(2000, data=data) # 流程成功
# end


if __name__ == '__main__':
    # demo
    t_begin = time.time()
    print time.ctime() + ':\t' + 'Test start'

    card_num = '77535404-X'
    name = '漳州伟翔精密机械有限公司'

    # card_num = ''
    # name = '何计通'
    results = zhixingSearchAPI(name, card_num)

    print time.ctime() + ':\t' + 'Test over, cost: {0} seconds\n'.format(time.time()-t_begin)

    print results

