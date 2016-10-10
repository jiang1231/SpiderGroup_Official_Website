#coding=utf-8
import Image
import requests
import threading
import sys, random
import os, json, time

reload(sys)
sys.setdefaultencoding('utf-8')

from requests.exceptions import *
from pytesser import  image_to_string
from threadpool import makeRequests, ThreadPool
from requests.utils import dict_from_cookiejar
from requests.packages.urllib3 import disable_warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
disable_warnings(InsecureRequestWarning)

from additional.mysql_process import insertDicts
from public.share_func import userAgent, basicRequest, \
    saveImage, getIp, removeAllFiles, clawLog, recogImage, makeDirs


class ZhiXingSpider(object):
    '''被执行人记录'''

    invalid_columns = ('sys_id', 'err_type') # t_zhixing_invalid的字段
    valid_columns = ('sys_id', 'name', 'card_num','case_code','reg_date','court_name','execute_money')  # t_zhixing_valid的字段
    json_keys  = ('id', 'pname', 'partyCardNum', 'caseCode','caseCreateTime', 'execCourtName', 'execMoney') # json的字段

    def __init__(self):
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

        self.err_ids = list()
        self.threads_cookies = dict()

        self.valid_items = list()       # 有效id
        self.invalid_items = list()     # 无效/出错id

        self.dire_temp = os.path.join(os.getcwd(), 'temp')  # 临时图片目录
        self.dire_code = os.path.join(os.getcwd(), 'code')  # 验证码目录
    # end


    def getCookies(self):
        """ 获取cookies流程（嵌套函数）
        :return: dict/False """

        cookies = dict()

        def visitSys():
            url = 'http://zhixing.court.gov.cn/search/'
            options = {'method':'get', 'url':url, 'headers':self.headers}

            response = basicRequest(options)
            if response:
                cookies.update(dict_from_cookiejar(response.cookies))
                # invoke next process
                return getSessionID()
            else:
                return False
        # def

        def getSessionID():
            url_one = 'http://zhixing.court.gov.cn/search/security/jcaptcha.jpg?87'
            url_two = 'http://zhixing.court.gov.cn/search/security/jcaptcha.jpg?3'
            self.headers['Referer'] = 'http://zhixing.court.gov.cn/'
            options_one = {'method':'get', 'url':url_one, 'cookies':cookies, 'headers':self.headers}
            options_two = {'method':'get', 'url':url_two, 'cookies':cookies, 'headers':self.headers}

            response = basicRequest(options_two) if basicRequest(options_one) else False

            if response:
                cookies.update(dict_from_cookiejar(response.cookies))
                #invoke next process
                return cookies
            else:
                return False
        # def

        return visitSys()
    # getCookies


    def getCode(self, re_num=3):
        """ 请求并保存验证码图片然后调用识别函数
        :return: 识别结果/None """

        threadID = threading.current_thread().ident
        cookies = self.threads_cookies[threadID]

        url =  'http://zhixing.court.gov.cn/search/security/jcaptcha.jpg?15'

        self.headers['Referer'] = 'http://zhixing.court.gov.cn/search/'
        options = {'method':'get', 'url':url,
                   'cookies':cookies, 'headers':self.headers}

        response = basicRequest(options)
        if response and len(response.text):
            image_path = saveImage(response, img_name=threadID)
            pw_code = recogImage(image_path, self.dire_temp, threadID)
            if pw_code:
                return pw_code
            else:
                time.sleep(random.uniform(0, 1))    # 识别错误重拉
                return self.getCode( re_num) if re_num > 0 else False
        else:
            re_num -= 1
            time.sleep(random.uniform(0, 1))
            return self.getCode(re_num) if re_num > 0 else False
    # end getNoteCode


    def getJson(self, sys_id):
        """  获得最后的json信息
        :param pw_code: 验证码
        :return: None """

        threadID = threading.current_thread().ident

        if not threadID in self.threads_cookies.keys():
            cookies = self.getCookies()
            if cookies:
                self.threads_cookies[threadID] = cookies
            else:
                self.saveErrID(sys_id, 1); return

        pw_code = self.getCode()
        if not pw_code:
            self.saveErrID(sys_id, 1); return

        params = {'id':sys_id, 'j_captcha':pw_code}
        url = 'http://zhixing.court.gov.cn/search/newdetail'
        self.headers['Referer'] = 'http://zhixing.court.gov.cn/search/'

        try:
            # 注意timeout的设置
            proxies = {'http':'http://127.0.0.1:8888','https':'http://127.0.0.1:8888'}
            response = requests.get(url, params=params, cookies=self.threads_cookies[threadID],
                                    proxies=proxies, headers=self.headers, timeout=5)
        except Timeout:
            self.saveErrID(sys_id, 2)

        except (ConnectionError,HTTPError,RequestException):
            self.saveErrID(sys_id, 3)

        else:
            # 注意判断条件 len(response.text) > 0 表示不为空
            if len(response.text) > 10:
                try:
                    item = json.loads(response.text, encoding='utf-8')
                except (ValueError,Exception):
                    self.saveErrID(sys_id, 3)
                else:
                    result = dict()
                    for i,v in enumerate(ZhiXingSpider.json_keys):
                        result[ZhiXingSpider.valid_columns[i]] = item[v]
                    self.valid_items.append(result)
            else:
                self.saveErrID(sys_id, 3)
    # end getJson


    def saveErrID(self, sys_id, err_type):

        if err_type not in (1,2,3):
            raise ValueError

        err_item = dict(sys_id=sys_id,err_type=err_type)
        self.invalid_items.append(err_item)
    # end


    def saveItems(self):
        '''  保存数据到mysql
        :return: None
        '''
        valid_num  = len(self.valid_items)
        invalid_num = len(self.invalid_items)

        if valid_num:
            table_name = 't_zhixing_valid'
            insertDicts(table_name, self.valid_columns, self.valid_items)
        if invalid_num:
            table_name = 't_zhixing_invalid'
            insertDicts(table_name, self.invalid_columns, self.invalid_items)

        return u'完成入库：有效信息{0}，错误信息{1}'.format(valid_num, invalid_num)

    # end saveItems


    @staticmethod
    def idQueue(start_id, goal, step=2500):
        # 将连续的id切分,避免单次分配过多的任务(id)
        end_id = start_id + goal
        while start_id < end_id:
            if start_id+step < end_id:
                yield range(start_id, start_id+step)
            else:
                yield range(start_id, end_id+1)
            start_id += step
    # end idQueue

    @staticmethod
    def getStartID():
        '''json文件读取启动id'''
        with open('./configuration/zhixing_start.json', 'r') as f:
                return json.loads(f.read())['sys_id']
    # end getStartID

    @staticmethod
    def saveClawedID(sys_id):
        with open('./configuration/zhixing_start.json', 'w') as f:
            f.write(json.dumps(dict(sys_id=sys_id)))

# class


def zhixingSpiderAPI(goal, thread_num):
    '''
    :param goal: 将要爬取id数目
    :param thread_num: 线程数目
    :return: None
    '''
    makeDirs()
    spider = ZhiXingSpider()
    pool = ThreadPool(thread_num)
    start_id = spider.getStartID()

    for group in  spider.idQueue(start_id, goal):
        spider.__init__()
        t_begin = time.time()

        print time.ctime() + u'\tBegin：启动id:{0}, 目标数量:{1}'.format(start_id, goal)

        requests = makeRequests(spider.getJson, group)
        [pool.putRequest(req) for req in requests]
        pool.wait()

        result = spider.saveItems()
        log_id = list()
        log_id.extend((group[0], group[-1]))
        clawLog(log_id, result)

        spider.saveClawedID(start_id+goal)

        print time.ctime() + u'\tOver：finish it,coast:{0} \n'.format(time.time()-t_begin)

        removeAllFiles([spider.dire_code, spider.dire_temp])
# end


if __name__ == '__main__':
    zhixingSpiderAPI(3600, thread_num=60)





