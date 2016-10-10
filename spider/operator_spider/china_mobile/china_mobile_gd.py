#coding=utf-8
"""
Goal：
    广东中国移动用户基本和通话记录的爬取和存储
Problem：
    1、通过selenium进行登录
Date:
    2016/7/28
Author:
    moyh
"""
import sys
reload(sys)
sys.path.append('../')
sys.setdefaultencoding("utf-8")
from copy import copy
import time,json,random,re
from lxml import etree
import spider.public.db_config as DB
from selenium import webdriver
from selenium.common.exceptions import *
from spider.public import userAgent, basicRequest
from necessary.mobile_month import getMonthSeq
import configuration.columns as config

_time_wait = 2
_time_usual = 100
_time_special = 200

class ChinaMobile_GD(int):
    """中国移动-广东爬虫"""
    def __init__(self, phone_attr):
        self.__headers = {
            'Accept': '*/*',
            'User-Agent': userAgent(),
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN',
            'Connection': 'keep-alive',
        }
        self.browser = None
        self.cookies = dict()   # cookies
        self.phone_attr = phone_attr # 手机属性
        self.user_items = list()   # 用户信息
        self.call_items = list()   # 通话信息
        self.refresh_num = 3       # 更新峰值
    # end

    @staticmethod
    def getCookies(cookies_seq):
        # 转换cookies
        cookie_dict = dict()
        if cookies_seq:
            for cookie in cookies_seq:
                cookie_dict[cookie['name']] = cookie['value']
        return cookie_dict
    # end

    @staticmethod
    def timeSleep(min=1, max=3):
        # 设置中断
        if min <= max:
            return time.sleep(random.uniform(min, max))
        else:
            raise ValueError('param value error')
    # end

    @staticmethod
    def judgeByMatch(pattern, string):
         # 通过match内容来判断相关类型
        try:
            re.match(pattern, string).group(1)
        except (IndexError, AttributeError):
            return False
        else:
            return True
    # end

    def getCode(self):

        def openBrowser():
            url = 'http://gd.10086.cn/my/REALTIME_LIST_SEARCH.shtml'
            # browser = webdriver.PhantomJS(r'C:\driver\phantomjs-2.1.1-windows\bin\phantomjs.exe')
            self.browser = webdriver.Chrome(r'C:\driver\chromedriver.exe')
            self.browser.get(url)
            self.browser.implicitly_wait(_time_usual)  # open the login page
            return True

        def acquireCode():

            try:
                self.browser.switch_to.frame('iframe_login_pop')
            except NoSuchFrameException as frame_ex:
                print frame_ex
                sys.exit(0)

            user_name_element = self.browser.find_element_by_id('mobile')  # 手机号框
            user_name_element.clear()
            user_name_element.send_keys(self.phone_attr['phone'])
            try:
                self.browser.find_element_by_id('btn_get_dpw').click()
            except ElementNotVisibleException as ex:
                if self.refresh_num > 0:
                    self.refresh_num -= 1
                    self.browser.refresh()
                    return acquireCode()  # 调用自身
                else:
                    raise Exception(u'对不起,获取手机动态码失败')
            else:
                self.browser.implicitly_wait(_time_usual)  # open the login page
                #　动态密码已发送，10分钟内有效。
                time.sleep(_time_wait)
                try:
                    tips = self.browser.find_element_by_xpath('//span[@class="text"]').text.strip().encode('utf-8')
                    print [tips]
                except (NoSuchElementException, WebDriverException):
                    sys.exit(0)
                else:
                    print tips
                    if self.judgeByMatch('(动态密码已发送)', tips):
                        print u'hi,动态验证码已经发送到手机:' + self.phone_attr['phone']
                        return 2000

                    elif self.judgeByMatch('(动态密码发送失败)', tips):
                        print  u'hi,动态验证码无法发送到手机:' + self.phone_attr['phone']
                        return 4000
                    else:
                        print tips
        # 逻辑
        if openBrowser():
            return acquireCode()
        else:
            raise WebDriverException(u'无法调用驱动')
    # def

    def login(self):

        user_name_element = self.browser.find_element_by_id('mobile')  # 用户名框
        password_element = self.browser.find_element_by_name('password')  # 密码框
        dynamic_pw_element = self.browser.find_element_by_name('dynamicCaptcha')  # 动态密码框
        login_element = self.browser.find_element_by_id('loginSubmit')  # 登录按钮

        user_name_element.clear()
        user_name_element.send_keys(self.phone_attr['phone'])

        password_element.clear()
        password_element.send_keys(self.phone_attr['password'])

        dynamic_pw_element.send_keys(self.phone_attr['phone_pwd'])
        login_element.click()  # login after click
        t_begin = time.time()
        self.browser.implicitly_wait(_time_special)
        print u'这里究竟花费了多长时间呀:{0}'.format(time.time()-t_begin)
        return self.judgeLogin()  # 登陆态判断
    # def

    def judgeLogin(self):
        """ 进行登录判断
        :return:
        """
        try:
            tips = self.browser.find_element_by_xpath('//span[@class="text"]').text.strip().encode('utf-8')
        except (NoSuchElementException, WebDriverException):
            return 2000
        else:
            print type(tips),len(tips)
            if self.judgeByMatch('(密码)', tips):
                print 'pw error'
                return 4401  # 密码错误
            elif self.judgeByMatch('(动态密码错误)', tips):
                return 4402  # 动态码错误
            elif tips == '':
                return 2000
            else:
                raise Exception(u'未知错误')
    # def

    def clawAllInfo(self):
        try:
            self.browser.find_element_by_xpath('//div[@id="mathBox"]/div/a[1]').click()  # 点击查询
            self.browser.implicitly_wait(_time_usual)
        except NoSuchElementException as ex:
            return 4000
        self.cookies = self.getCookies(self.browser.get_cookies())     # cookies更新
        if len(self.cookies) > 0:
            self.clawUserInfo()  # 爬取用户信息
            self.clawCallInfo()  # 爬去通话记录
            return 2000
        else:
            return 4000
    # end

    def clawUserInfo(self):
        """Get the basic information of the user
        :return:False/list
        """
        def queryInfo():
            form = {'servCode': 'MY_BASICINFO'}
            url = 'http://gd.10086.cn/commodity/servicio/track/servicioDcstrack/query.jsps'
            self.__headers['Referer'] = 'http://gd.10086.cn/my/myService/myBasicInfo.shtml'
            options = {'method':'post', 'url':url, 'form':form, 'cookies':self.cookies, 'headers':self.__headers}

            response = basicRequest(options)
            if response:
                return getInfo()
            else:
                return False
        # def

        def getInfo():
            form = {'servCode':'MY_BASICINFO', 'operaType':'QUERY'}
            url = 'http://gd.10086.cn/commodity/servicio/servicioForwarding/queryData.jsps'
            self.__headers['Referer'] = 'http://gd.10086.cn/my/myService/myBasicInfo.shtml'
            options = {'method':'post', 'url':url, 'form':form, 'cookies':self.cookies, 'timeout':30, 'headers':self.__headers}

            response = basicRequest(options)
            if response:
                return clawInfo(response.text)
            else:
                return False
        # def

        def clawInfo(text):
            try:
                selector = etree.HTML(text)
                table = selector.xpath('//table[@class="tb02"]')[0]
                values =  table.xpath('tbody/tr[2]/td/text()')
                if len(values) == 0:
                    values =  table.xpath('tr[2]/td/text()')
                item = dict(
                    phone = values[0],
                    name = values[1],
                    cert_num = values[2],
                    open_date = values[4],
                    company = self.phone_attr['company'],
                    province = self.phone_attr['province'],
                    city = self.phone_attr['city'],
                    user_valid = 1
                )
                # 填充字段
                [item.setdefault(i, '') for i in config.COLUMN_USER]
                self.user_items.append(item) # 保存记录
            except (IndexError,Exception) as ex:
                return 4000
        # def
        return queryInfo()
    # end

    def clawCallInfo(self):
        """ Save all call records
        :return: null
        """
        item = {
            'cert_num': self.user_items[0]['cert_num'],
            'phone': self.user_items[0]['phone']
        }
        text_seq = self.getFiveMonthCall()
        if len(text_seq) > 0:
            for text in text_seq:
                results = json.loads(text)['content']['realtimeListSearchRspBean']['calldetail']['calldetaillist']
                for record in results:
                    temp = copy(item)
                    # 'place', 'time', 'time', 'chargefee','period', 'contnum', 'becall', 'conttype'
                    for k, v in record.items():
                        if k in config.KEY_CONVERT_CALL.keys():
                                column_name = config.KEY_CONVERT_CALL[k]
                                temp[column_name] = v
                    try:
                        self.convertValues(temp)  # 入库修正
                    except Exception as ex:
                        print ex
                        for k,v in temp.items():
                            print k, v
                    self.call_items.append(temp)
        else:
            print 'call records not found'
    # end


    def convertValues(self,temp):
        key = temp.keys()
        if 'call_type' in key:
            call_type = {u'主叫': 1, u'被叫': 2 }
            if temp['call_type'] in call_type.keys():
                temp['call_type'] = call_type[temp['call_type']]
            else:
                temp['call_type'] = 3

        if 'land_type'in key:
            land_type = {u'本地': 1, u'国内长途': 2}
            if temp['land_type'] in land_type.keys():
                temp['land_type'] = land_type[temp['land_type']]
            else:
                temp['land_type'] = 3

        if 'call_date' in key:
             # '04-01 11:18:50' 对时间进行分割
            date_time =  temp['call_date'].split(' ')
            temp['call_date'] = '2016-' + date_time[0]
            temp['call_time'] = date_time[1]
    # end

    def getFiveMonthCall(self):
        """Get the call records of the past five months
        :return: list (maybe empty)
        """
        text_seq = list()
        month_seq = getMonthSeq()[1:2]

        for month in month_seq:
            print '请耐心等待,正在查询{0}:'.format(month)
            result = self.getMonthCall(month)
            if result:
                text_seq.append(result)
            else:
                print '抱歉,查询{0}月通话数据失败'.format(month)
        # for
        return text_seq
    # end

    def getMonthCall(self,month):
        """Get the call records according to month
        :param month: year+month, example:'201602'
        :return: False/response.text
        """
        def getUniqueTag():
            form = {'month': '201602'}
            form['month'] = month
            url = 'http://gd.10086.cn/commodity/servicio/nostandardserv/realtimeListSearch/query.jsps'
            self.__headers['Referer'] = 'http://gd.10086.cn/my/REALTIME_LIST_SEARCH.shtml?dt=1469030400000'
            options = {'method':'post', 'url':url, 'form':form, 'cookies':self.cookies, 'headers':self.__headers}

            response = basicRequest(options)
            if response:
                try:
                    unique_tag = json.loads(response.text)['attachment'][0]['value']
                    return getMonthRecords(unique_tag)
                except (KeyError,IndexError,Exception) as ex :
                    print 'unique_tag not found, error:',ex
                    return False
            else:
                return False
        # def

        def getMonthRecords(unique_tag):

            form = dict(uniqueTag=unique_tag, monthListType='0')
            url = 'http://gd.10086.cn/commodity/servicio/nostandardserv/realtimeListSearch/ajaxRealQuery.jsps'
            options = {'method':'post', 'url':url, 'form':form, 'cookies':self.cookies, 'timeout':20, 'headers':self.__headers}   # pay attention to "timeout"
            response = basicRequest(options)
            if response:
                return response.text
            else:
                return False
        # def
        return getUniqueTag()
    # end

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


# 获取手机动态码
def getNoteCode(phone_attr):
    """
    :param phone_attr: {'phone':'15802027662', 'province':'广东', 'city':'广州', 'company':2, 'password' = '20168888'}
    :return:
    """
    if not isinstance(phone_attr, dict):
        raise ValueError(u'参数错误')

    spider = ChinaMobile_GD(phone_attr)
    result = spider.getCode()
    spider.browser.close()
    if result == 2000:
        return dict(code=2000, temp=spider) # 成功
    else:
        return dict(code=4444, temp=None) # 失败


# 更新手机动态码
def updateNoteCode():
    pass


# 登陆系统
def loginSys(spider):
    print
    if not isinstance(spider, ChinaMobile_GD):
        raise 'obj error', ValueError(u'参数错误')

    login = spider.login()
    if login == 2000: # 登录成功
        print u'登录成功'
        search = spider.clawAllInfo() # 爬取内容
        if search == 2000:
            print '爬取内容成功'
            # print spider.saveItems()
            result=dict(
                t_operator_user = spider.user_items,
                t_operator_call = spider.call_items,
                t_operator_note = []
            )
            spider.browser.close()
            return dict(code=2000, result=result)
    else:
        print u'登录失败,失败码:{0}'.format(login)
        spider.browser.close()
        return dict(code=login, temp=None) # 密码错误4401,动态码错误4402



if __name__ == '__main__':

    from spider.operator_spider.necessary.get_phone_attr import getPhoneAttr
    attr = getPhoneAttr('15802027662')
    if attr['code'] == 2000:
        phone_attr = attr['data']
        phone_attr['password'] = '20168888'  # 添加密码
        code_result = getNoteCode(phone_attr) # 获得手机动态码

        if code_result['code'] == 2000:
            print u'获得手机动态码成功'
            # 获得手机动态码，并调用登陆
            code_result['temp'].phone_attr['phone_pwd'] = raw_input(u'请输入手机动态码:')

            login_result = loginSys(code_result['temp'])
            if login_result['code'] == 2000:
                result = login_result['result']
                print result
            else:
                print login_result
        else:
            print code_result


