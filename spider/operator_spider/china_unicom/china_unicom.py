#coding=utf-8
"""
++++++++++++++++描述+++++++++++++++++
联通通话记录爬取
时间：2016/9/9
版本：协程版
++++++++++++++++Over+++++++++++++++++
"""
import json
import re
import time
from math import ceil
from copy import copy

import gevent
import spider.public.db_config as DB
import configuration.columns as config
from gevent import monkey; monkey.patch_all()
from requests.utils import dict_from_cookiejar
from threadpool import ThreadPool, makeRequests

from necessary.param_date import getDateSeq
from configuration.columns import KEY_CONVERT_USER
from spider.public import userAgent, basicRequest, \
    getTimestamp, returnResult, clawLog, makeDirs

_thread_num = 3

class ChinaUnicom(object):
    """中国联通爬虫"""
    def __init__(self, phone_attr):
        self.headers = {
            'Accept': '*/*',
            'User-Agent': userAgent(),
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.cookies  = dict()
        self.user_items = list()   # 用户信息
        self.call_items = list()   # 通话信息
        self.phone_attr = phone_attr    # 手机基本信息
    # end

    def loginSys(self):
        """ 登录流程(函数嵌套的方式)
        :return: sysCheckLogin()
        """
        def sysCheckLogin():
            """ 登录检查,更新cookies
            :return: loginByJS()/dict
            """
            url = 'http://iservice.10010.com/e3/static/check/checklogin/?_=' + getTimestamp()
            self.headers['Referer'] = 'http://iservice.10010.com/e3/query/call_dan.html?menuId=000100030001'
            options = {'method':'post', 'url':url, 'cookies':None, 'headers':self.headers}

            response = basicRequest(options)
            if response:
                self.cookies.update(dict_from_cookiejar(response.cookies))
                return loginByJS()
            else:
                return dict(code=4000, func='sysCheckLogin')
        # end

        def loginByJS():
            """ 通过get登录,更新cookies
            :return: judgeLogin(response)/dict()
            """
            params = {
                '_': '1468474921490',   # req_time + 1
                'callback': 'jQuery172000024585669494775475_1468770450339',
                'password': '662670',
                'productType': '01',
                'pwdType': '01',
                'redirectType':	'03',
                'redirectURL': 'http://www.10010.com',
                'rememberMe': '1',
                'req_time': '1468474921489',
                'userName':	'18617112670'
            }
            params['req_time'] = getTimestamp()
            params['_'] = str(int(params['req_time'])+1)
            params['userName'] = self.phone_attr['phone']
            params['password'] = self.phone_attr['password']

            url = 'https://uac.10010.com/portal/Service/MallLogin'
            self.headers['Referer'] = 'http://uac.10010.com/portal/hallLogin'
            options = {'method':'get', 'url':url, 'params':params, 'cookies':None, 'headers':self.headers}

            response = basicRequest(options)
            if response:
                return judgeLogin(response)
            else:
                return dict(code=4000, func='loginByJS')
        # def

        def judgeLogin(response):
            """ 对登录response进行分析
            :param response: response obj
            :return: 登录状态码dict()/raise
            """
            try:
                code = re.search(r'resultCode:"(.*?)"', response.text).group(1)
            except (AttributeError,IndexError) as ex:
                return dict(code=4000, func='judgeLogin')
            else:
                code_hash = {
                    '0000': 2000, # 流程成功
                    '7007': 4600, # 密码错误
                    '7999': 5500, # 对方服务器繁忙
                    '7072': 4500, # 账号错误
                    '7009': 4500  # 账号错误
                }
                if code in code_hash.keys():
                    self.cookies.update(dict_from_cookiejar(response.cookies))
                    return dict(code=code_hash[code])
                else:
                    raise Exception('未知错误')
        # def
        return sysCheckLogin()
    # end

    def getUserInfo(self):
        """ 爬取用户信息
        :return: sysCheckLoginAgain()
        """
        def sysCheckLoginAgain():
            """ 检查是否登录
            :return: getHeaderView()
            """
            url = 'http://iservice.10010.com/e3/static/check/checklogin/?_=' + getTimestamp()
            self.headers['Referer'] = 'http://iservice.10010.com/e3/query/call_dan.html?menuId=000100030001'
            options = {'method':'post', 'url':url, 'cookies':self.cookies, 'headers':self.headers}

            response = basicRequest(options)
            if response:
                return getHeaderView()
            else:
                return dict(code=4000, func='sysCheckLoginAgain')
        # def

        def getHeaderView():
            """ 获得账户balance(余额)
            :return: saveUserInfos(part_info)/dict()
            """
            url = 'http://iservice.10010.com/e3/static/query/headerView'
            self.headers['Referer'] = 'http://iservice.10010.com/e3/index_server.html'
            options = {'method':'post', 'url':url, 'cookies':self.cookies, 'headers':self.headers}

            response = basicRequest(options)
            if response:
                try:
                    self.phone_attr['balance'] = json.loads(response.text)['result']['account']
                except KeyError:
                    self.phone_attr['balance'] = ''
                return getUserRecord()
            else:
                return dict(code=4000, func='getHeaderView')
        # def

        def getUserRecord():
            """ 获得用户信息
            :return:
            """
            params = { '_':getTimestamp(), 'menuid':'000100030001'}
            url = 'http://iservice.10010.com/e3/static/query/searchPerInfo/'
            self.headers['Referer'] = 'http://iservice.10010.com/e3/query/personal_xx.html'
            options = {'method':'post', 'url':url, 'params':params, 'cookies':self.cookies, 'headers':self.headers}

            response = basicRequest(options)
            if response:
                item = dict()
                result = json.loads(response.text)['result']
                item['user_valid'] = 1 if result['usercirclestatus'] == u'有效期' else 0
                for k, v in result['MyDetail'].items():
                    if k in KEY_CONVERT_USER.keys():
                        columm_name = KEY_CONVERT_USER[k]
                        item[columm_name] = v
                del self.phone_attr['password']
                self.user_items.append(dict(item, **self.phone_attr))
            else:
                return dict(code=4000, func='clawCallRecords')
        # def
        return sysCheckLoginAgain()
    # end


    def getCallInfo(self):

        def clawMonthCall(month):
            text = clawPageCall(month)
            try:
                page_json = json.loads(text)
            except (ValueError,Exception):
                return
            if 'errorMessage' in page_json.keys():  # 存在错误
                return
            else:
                text_seq.append(text)
                total_record = float(page_json['totalRecord'])
                # remain_page = int(ceil((total_record-100)/ 100))
                remain_page = int(ceil((total_record-20)/ 20))
                if remain_page > 0:
                    print '请注意,{0}月份还有{1}页'.format(month[0], remain_page)

                    coroutine_obj = list()
                    for page in range(2, 2+remain_page):
                        coroutine_obj.append(gevent.spawn(coroutineClawPageCall, month, page))
                    gevent.joinall(coroutine_obj)
                else:
                    pass
        # def

        def coroutineClawPageCall(date_tuple, page_no=1, resend = 2):  #完成单次请求[存在网络繁忙则重传]
            """完成单次请求"""
            params = { '_':getTimestamp(), 'menuid':'000100030001'}
            form = {'pageNo': page_no, 'pageSize':'20', 'beginDate':date_tuple[0], 'endDate':date_tuple[1]}
            url = 'http://iservice.10010.com/e3/static/query/callDetail'
            self.headers['Referer'] = 'http://iservice.10010.com/e3/query/call_dan.html?menuId=000100030001'
            options = {'method':'post', 'url':url, 'form':form, 'params':params, 'cookies':self.cookies, 'headers':self.headers}
            response = basicRequest(options)
            if response:
                try:
                    page_json = json.loads(response.text)
                except ValueError:
                    pass
                else:
                    if 'errorMessage' in page_json.keys() and  resend > 0: # 存在系统繁忙
                        try:
                            if page_json['errorMessage']['respCode'] == '4114030193':
                                return clawPageCall(date_tuple, page_no, resend-1)     # 繁忙重传
                        except KeyError:
                            pass
                    else:
                        text_seq.append(response.text)
                        print '注意:协助完成处理{0}日到{1}日记录中的第{2}页'.format(date_tuple[0], date_tuple[1], page_no)

            else:
                pass
        # def

        def clawPageCall(date_tuple, page_no=1, resend = 2):  #完成单次请求[存在网络繁忙则重传]
            """完成单次请求"""
            params = { '_':'1468549625712', 'menuid':'000100030001'}
            form = {'pageNo':'1', 'pageSize':'20', 'beginDate':'2016-07-01', 'endDate':'2016-07-18'}
            form['pageNo'] = page_no
            form['beginDate'] = date_tuple[0]
            form['endDate'] = date_tuple[1]
            params['_'] = getTimestamp()

            url = 'http://iservice.10010.com/e3/static/query/callDetail'
            self.headers['Referer'] = 'http://iservice.10010.com/' \
                                      'e3/query/call_dan.html?menuId=000100030001'

            options = {'method':'post', 'url':url, 'form':form,
                       'params':params, 'cookies':self.cookies, 'headers':self.headers}

            response = basicRequest(options)
            if response:
                try:
                    page_json = json.loads(response.text)
                except ValueError:
                    return False
                else:
                    if 'errorMessage' in page_json.keys() and  resend > 0: # 存在系统繁忙
                        try:
                            if page_json['errorMessage']['respCode'] == '4114030193':
                                return clawPageCall(date_tuple, page_no, resend-1)     # 繁忙重传
                        except KeyError:
                            return False
                    else:
                        return response.text
            else:
                return False
        # def

        t_start = time.time()
        text_seq = list()
        date_seq = getDateSeq()

        pool = ThreadPool(_thread_num)
        requests = makeRequests(clawMonthCall, date_seq)
        [pool.putRequest(req) for req in requests]
        pool.wait()

        print '结束:所有的通话记录数据的总页数为：{0}'.format(len(text_seq))
        print '统计:爬取通话记录耗费{0}秒'.format(time.time() - t_start)
        return self.parseCallInfo(text_seq)
    # end

    def parseCallInfo(self, text_seq):
        item = {
            'cert_num': self.user_items[0]['cert_num'],
            'phone': self.user_items[0]['phone']
        }
        for text in text_seq:
            try:
                results = json.loads(text)['pageMap']['result']
            except (KeyError,ValueError,Exception):
                continue
            else:
                for record in results:
                    temp = copy(item)
                    for k, v in record.items():
                        if k in config.KEY_CONVERT_CALL.keys():
                            column_name = config.KEY_CONVERT_CALL[k]
                            temp[column_name] = v
                    self.convertValues(temp) # 入库修正
                    self.call_items.append(temp)
                # for
        # for
    # end

    def convertValues(self,item):

        key = item.keys()
        if 'call_type' in key:
            call_type = {u'主叫': 1, u'被叫': 2 }
            if item['call_type'] in call_type.keys():
                item['call_type'] = call_type[item['call_type']]
            else:
                item['call_type'] = 3

        if 'land_type'in key:
            land_type = {u'本地通话': 1, u'省内通话': 2}
            if item['land_type'] in land_type.keys():
                item['land_type'] = land_type[item['land_type']]
            else:
                item['land_type'] = 3
    # end


    def getNoteInfo(self):
        # 获得短信信息
        pass

    def saveItems(self):
        """  保存数据到mysql
        :return: None
        """
        valid_num  = len(self.user_items)
        invalid_num = len(self.call_items)

        if valid_num:
            DB.insertDictList(config.TABEL_NAME_1, config.COLUMN_USER, self.user_items)
        if invalid_num:
            DB.insertDictList(config.TABLE_NAME_2, config.COLUMN_CALL, self.call_items)

        return u'完成入库：有效信息{0}，错误信息{1}'.format(valid_num, invalid_num)
    # end
# class

def checkAttr(phone_attr):
    _key = ('phone', 'province', 'city', 'company', 'password')
    if not isinstance(phone_attr, dict) or set(phone_attr.keys()) != set(_key):
        return returnResult(4400, data={})
    else: # 参数正确返回True
        return True


def chinaUnicomAPI(phone_attr):
    """
    :param phone_attr: dict(phone=XX, province=XX, city=XX, company=XX, password=XX)
    :param password: 全为数字的字符串(长度不少于6位)
    :return:
    """
    # makeDirs()
    check_param = checkAttr(phone_attr)
    if check_param != True:
        return check_param  # 返回参数错误

    spider = ChinaUnicom(phone_attr)
    login = spider.loginSys()
    if login['code'] != 2000:
        return returnResult(login['code'], data={}) # 返回登陆错误信息
    else:
        spider.getUserInfo()
        spider.getCallInfo()
        # spider.saveItems()
        # clawLog(phone_attr, log)
        data =  dict(
            t_operator_user = spider.user_items,
            t_operator_call = spider.call_items,
            t_operator_note = list()
        )
        return returnResult(2000, data=data)  # 返回爬去结果
# end


if __name__ == '__main__':
    # demo
    from necessary.get_phone_attr import getAttributes
    t_begin = time.time()
    attr = getAttributes('13267175437')
    if attr['code'] == 2000:
        phone_attr = attr['data']
        phone_attr['password'] = '201688'
        result = chinaUnicomAPI(phone_attr)
        for item in result.items():
            print item
    else:
        print '无法查询号码的归属信息,bye!'

    print u'整个流程耗费用时:{0}'.format(time.time()-t_begin)