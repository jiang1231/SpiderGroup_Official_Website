#coding=utf-8

"""
+++++++++++++++++++++Intro+++++++++++++++++++++

时间：2016/9/9
版本：协程版
流程: 1.拿到cookies 2.请求验证码 3.在1/2下并发多个id
注意: 步骤3下并发的大小问题
接口:
    A: shixinSpiderAPI() 遍历id 1-4825018
    B: errRequestFailAPI() 遍历A中timeout或者被block的id
    C: errUnknownAPI() 遍历A可能不存在相应信息的id
    D: errLostIDs() 遍历由于系统等异常导致丢失的id

+++++++++++++++++++++Over++++++++++++++++++++++++
"""

import sys
reload(sys)
sys.path.append('../')
sys.setdefaultencoding('utf-8')

import gevent
from gevent import monkey; monkey.patch_all()
from requests.utils import dict_from_cookiejar

import public.db_config as DB
import configuration.columns as config
from public.share_func import *
from necessary.shixin_python_sql import *


class ShiXinSpider(object):
    """失信被执行人信息"""
    def __init__(self):
        self.headers = {
            'Referer': '',
            'User-Agent': userAgent(),
            'X-Forwarded-For': getIp(),
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'shixin.court.gov.cn',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        self.cookies = dict()           # “全局”cookies
        self.block_flag = False         # 标记是否被block
        self.valid_items = list()       # 有效id
        self.invalid_items = list()     # 无效/出错id
    # end


    def updateCookies(self):
        """ 获取验证码流程（嵌套函数）
        :return:cookies obj/False
        """
        def visitSys():
            """ 填充cookies
            :return: getSessionID()/False
            """
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
            """填充cookies
            :return: getONEAPM_AI()/False
            """
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
            """ 填充cookies
            :return: getONEAPM_AI()/False
            """
            params = {'functionId':'1'}
            url = 'http://shixin.court.gov.cn/visit.do'
            self.headers['Referer'] = 'http://shixin.court.gov.cn/'
            options = {'method': 'get', 'url': url, 'params': params, 'cookies': self.cookies, 'headers': self.headers}

            response = basicRequest(options)
            if response:
                self.cookies.update(dict_from_cookiejar(response.cookies))
                return self.cookies
            else:
                return False
        # def
        return visitSys()
    # end updateCookies


    def getCode(self, re_num=3):
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
    # end getCode


    def saveErrID(self, sys_id, err_type):
        """:param sys_id: 单个id或者list,tuple
        :param err_type: 错误类型
        :return: None
        """
        if err_type not in (1, 2, 3):
            raise ValueError(u'错误类型范围不在定义范围')

        if isinstance(sys_id, (list, tuple)):
            for i in sys_id:
                self.invalid_items.append(dict(sys_id = i, err_type = err_type))
        else:
            self.invalid_items.append(dict(sys_id = sys_id, err_type = err_type))
    # end


    def getJson(self, sys_id, pw_code, re_num=2):
        """ 获得sys_id对应的信息
        :param pw_code: 验证码
        :return: None
        """
        params = {'id':sys_id, 'pCode':pw_code}
        url = 'http://shixin.court.gov.cn/findDetai'
        self.headers['Referer'] = 'http://shixin.court.gov.cn/'

        options = {'method': 'get', 'params':params, 'url': url,
                   'cookies': self.cookies, 'headers': self.headers, 'timeout':1 }
        response = basicRequest(options, resend_times=1)
        if response and response.status_code not in (520, 500) and len(response.text):
            try:
                item = json.loads(response.text, encoding='utf-8')
            except (ValueError, Exception):
                self.saveErrID(sys_id, 3)
            else:
                result = dict()
                for k, v in item.items():
                    if k in config.KEY_COLUMN.keys():
                        key = config.KEY_COLUMN[k]
                        result[key] = v
                result['flag']  = 1 if 'businessEntity' in item.keys() else 0
                self.valid_items.append(result)
        else:
            re_num -= 1
            if re_num > 0:
                return self.getJson(sys_id, pw_code, re_num)
            else:
                self.saveErrID(sys_id, 3)
    # end


    def startSpider(self, group):
        """ 完成组队列请求json结果
        同个cookies请求多个验证码，每个验证码并发一组
        :param group:[(),(),(),...]; []指组，()指小组
        :return: None
        """
        cookies = self.updateCookies()

        if not cookies:
            print u'{0}: 危险:请切换ip'.format(time.ctime())
            for sub_group in  group:
                self.saveErrID(sub_group, 1)
            self.block_flag = True # 标志为被block
            return 404

        for sub_group in group:
            code = self.getCode()
            if not code:
                self.saveErrID(sub_group, 1)
                time.sleep(random.uniform(1, 3))
                continue

            objs = list()
            for sys_id in sub_group:
                objs.append(gevent.spawn(self.getJson, sys_id, code))
            gevent.joinall(objs)
    # end startSpider


    def saveItems(self):
        """ 保存数据到mysql
        :return: 统计log
        """
        valid_num  = len(self.valid_items)
        invalid_num = len(self.invalid_items)

        if valid_num:
            DB.insertDictList('t_shixin_valid', config.COLUMN_VALID, self.valid_items)
        if invalid_num:
            DB.insertDictList('t_shixin_invalid', config.COLUMN_INVALID, self.invalid_items)

        return u'完成入库: 有效记录数{0}，错误记录数{1}'.format(valid_num, invalid_num)
    # end


    def errUnknownSaveItems(self):
        """ 对错误类型为3(即可能不存在的对应信息的id)
        :return :None
        """
        valid_num  = len(self.valid_items)
        invalid_num = len(self.invalid_items)

        if valid_num:
            DB.insertDictList('t_shixin_valid', config.COLUMN_VALID, self.valid_items)
            deleteErrItems([item['sys_id'] for item in self.valid_items])
        if invalid_num:
            updateIDstatus([item['sys_id'] for item in self.invalid_items if item['err_type'] == 3])

        return u'完成入库：有效记录数{0}，错误记录数{1}'.format(valid_num, invalid_num)
    # end


    @staticmethod
    def getGroups(start_id=None, goal=None, step=50, sub_group_num=10):
        """ 初始化连续的id
        :param start_id: 开始id
        :param goal: 爬取的id总数(start_id开始)
        :param step: 每个小组的大小
        :param sub_group_num: 组中的小组个数
        :return:[(),(),(),...]; []指组，()指小组
        """
        end_id = start_id + goal
        while start_id < end_id:
            group = list()
            for i in range(sub_group_num):
                if start_id+step < end_id:
                    group.append(tuple(range(start_id, start_id+step)))
                    start_id += step
                else:
                    group.append(tuple(range(start_id, end_id)))
                    start_id += step
                    break
            # for
            yield group


    @staticmethod
    def splitGroups(seq, step=50, sub_group_num=8):
        """ 初始化不联系的id
        :param seq：list
        :param step: int
        :return: [(),(),(),...]; []指组，()指小组
        """
        index = 0
        seq_len =  len(seq)
        while index < seq_len:
            group = list()
            for i in range(sub_group_num):
                if index+step < seq_len:
                    group.append(tuple(seq[index:index+step]))
                    index += step
                else:
                    group.append(tuple(seq[index:seq_len]))
                    index += step
                    break
            yield  group
    # end splitGroups


    @staticmethod
    def getStartID():
        """从json文件读取启动id"""
        with open('./configuration/shixin_start_id.json', 'r') as f:
                return json.loads(f.read())['sys_id']
    # end


    @staticmethod
    def saveClawedID(sys_id):
        """将启动id保存到json文件"""
        with open('./configuration/shixin_start_id.json', 'w') as f:
            f.write(json.dumps(dict(sys_id=sys_id)))
    # end

# end class


def shixinSpiderAPI(goal, step=50, sub_group_num=8):
    """ 遍历所有ID
    :param goal: 将要爬取数目
    :param num: 同一cookie下的小组数
    :step: 小组中的id总数(拿到验证码后"并发"的ID数)
    :return: None """
    makeDirs()
    spider = ShiXinSpider()
    start_id = spider.getStartID()

    t_begin = time.time()
    print u'Bingo：启动id:{0}, 目标数量:{1}'.format(start_id, goal)

    for group in spider.getGroups(start_id, goal, step, sub_group_num):

        spider.__init__()
        spider.startSpider(group)
        result = spider.saveItems()
        clawLog(group, result)
        spider.saveClawedID(start_id+goal)

        if spider.block_flag:  #判定ip被block
            break

    print u'进程结束：总用时为{0}'.format(time.time() - t_begin)
# end


def errRequestFailAPI(num=400):
    """ 从t_shixin_invalid读出并删除num个err_type
    为1/2的sys_id,然后对这num个id进行爬取，并保存最终结果
    :param num: 每次读取的id数,建议num >> 400
    :return: None
    """
    makeDirs()
    spider = ShiXinSpider()
    ids = queryRequestFailID(num)

    t_begin = time.time()
    print u'Bingo：时间:{0}'.format(time.ctime())

    while ids:
        for group in spider.splitGroups(ids):
            spider.__init__()
            spider.startSpider(group)
            result = spider.saveItems()
            clawLog(group, result)
        # for
        if spider.block_flag: #判定ip被block
            break
        ids = queryRequestFailID(num)  # 继续读库
    # while
    print u'进程结束：总用时为{0}'.format(time.time() - t_begin)
# end


def errUnknownAPI(num):
    """从DB批量读取unknwon表的sys_id,并进行请求
    :param num: 每次读取的id最大数
    :return: None
    :有效id:1741386
    """
    makeDirs()
    spider = ShiXinSpider()
    ids = queryErrUnknownID(num)

    t_begin = time.time()
    print u'Bingo：时间:{0}'.format(time.ctime())

    while ids:
        for group in spider.splitGroups(ids):
            spider.__init__()
            spider.startSpider(group)
            result = spider.errUnknownSaveItems()
            clawLog(group, result)
        # for
        if spider.block_flag: #判定ip被block
            break
        ids = queryErrUnknownID(num)
    # while
    print u'进程结束：总用时为{0}'.format(time.time() - t_begin)
# end


def errLostAPI():
    """ 根据已经遍历的id求出有哪些id是丢失的，并进行请求
    :return: None
    :有效id: 1741386
    """
    makeDirs()
    spider = ShiXinSpider()
    ids = queryLostID(3307986, 4825018)

    t_begin = time.time()
    print u'Bingo：时间:{0}'.format(time.ctime())

    for group in spider.splitGroups(ids):
        spider.__init__()
        spider.startSpider(group)
        result = spider.saveItems()
        clawLog(group, result)

        if spider.block_flag: #判定ip被block
            break
    # for
    print u'进程结束：总用时为{0}'.format(time.time() - t_begin)
# end

if __name__ == '__main__':
    print u'失信遍历爬虫，请指定遍历类型'
    # demo = ShiXinSpider()





