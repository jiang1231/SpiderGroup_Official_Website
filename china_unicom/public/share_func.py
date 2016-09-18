#coding=utf-8
import os
import time
import json
import random

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from io import BytesIO
from time import strftime,localtime

# from PIL import Image
from lxml import etree
from requests import request
from requests.exceptions import *
from pytesseract import image_to_string
from requests.packages.urllib3 import disable_warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
disable_warnings(InsecureRequestWarning)


def getIp():
    """ 为X-Forwarded-For构造ip地址
    :return:ipv4字符串 """
    a = random.randint(128, 223)
    b = random.randint(128, 223)
    c = random.randint(128, 223)
    d = random.randint(128, 223)
    return '{0}.{1}.{2}.{3}'.format(a,b,c,d)
# end


def getTimestamp(length=13):
    """ 获得指定长度的时间戳
    :param length: 时间戳长度
    :return: 时间戳字符串 """
    temp = str(time.time()).split('.')
    temp = ''.join(temp)
    str_time_stamp = temp[0:length] if len(temp) > length else  temp + '0'*(length-len(temp))
    return str_time_stamp
# end


def getUniqueFileName(num=2):
    """ 时间戳+随机数构造唯一文件名
    :param num: 随机次数
    :return: 数字字符串 """
    result = ''
    for i in range(num):
        result += str(random.randint(1, 200000))
    return getTimestamp() + result
# end

def recogImage(content):
    """ 识别只有数字的简单验证码
    :param content: response.content
    :return: 识别结果/False """
    file = BytesIO(content)
    img = Image.open(file)
    result = image_to_string(img)
    result = result if result.isdigit() else False
    img.close()
    file.close()
    return result


# def recogImage(image_path, temp_dire, threadID=''):
#     """ 简单验证码的识别
#     :param image_path: 图片绝对路径
#     :param temp_dire: ocr临时文件存放目录
#     :param threadID: 线程ID
#     :return: 识别结果/False """
#     temp_txt_name = getUniqueFileName() + str(threadID)
#     temp_img_name = getUniqueFileName() + str(threadID) + '.bmp'
#     scratch_image_name = os.path.join(temp_dire, temp_img_name)
#     scratch_text_name_root = os.path.join(temp_dire, temp_txt_name)
#     try:
#         img = Image.open(image_path).convert('L')
#         result = alter_image_to_string(img, scratch_image_name, scratch_text_name_root).strip()
#         result = result if result.isdigit() else False
#         return result
#     except (IOError,Exception):
#         return False
# # end



def userAgent():
    """ Generate a "user_agent"
    :return: "user_agent"  """
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.154 Safari/537.36 LBBROWSER',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.69 Safari/537.36 QQBrowser/9.1.3876.400'
    ]
    return random.choice(user_agent_list)
# end


def basicRequest(options, resend_times=1):
    """ 根据参数完成request请求，成功则返回response,失败返回False
    :param options: 请求参数
    :param resend_times: 重发次数
    :return: response对象或False
    example:
    options = {
        'method':'get',
        'url':'http://www.eprc.com.hk/EprcWeb/multi/transaction/login.do',
        'form':None,
        'params':None,
        'cookies':None,
        'headers':headers,
    }
    response = basicRequest(options)
    """
    keys = options.keys()
    options['timeout'] = options['timeout'] if 'timeout' in keys else 3
    # proxies = {'http':'http://127.0.0.1:8888','https':'http://127.0.0.1:8888'}

    try:
        response = request(
            options['method'],
            options['url'],
            timeout = options['timeout'],
            # proxies = proxies if 'proxies' not in keys else None,
            verify = options['verify'] if 'verify' in keys else False,
            data = options['form'] if 'form' in keys else None,
            params = options['params'] if 'params' in keys else None,
            cookies = options['cookies'] if 'cookies' in keys else None,
            headers = options['headers'] if 'headers' in keys else None,
            stream =  options['stream'] if  'stream' in keys else False,
        )
    except (ConnectTimeout, ReadTimeout, Timeout):
        if resend_times > 0:
            time.sleep(random.uniform(0,1))
            options['timeout'] += 1
            return basicRequest(options, resend_times-1)
        else:
            return False

    except ProxyError:
        if resend_times > 0:
            options['proxies'] = None
            return basicRequest(options, resend_times-1)
        else:
            return False

    except SSLError:
        if resend_times > 0:
            options['verify'] = False
            return basicRequest(options, resend_times-1)
        else:
            return False

    except (RequestException, Exception) as ex:
        if resend_times > 0:
            time.sleep(random.uniform(1, 3))
            return basicRequest(options, resend_times-1)
        else:
            print u'危险:请求参数为{options}存在未分类异常,错误为{ex}'.format(options=options, ex=ex)
            return False
    else:
        return response
# end


def xpathText(resonse_text, path_dict):
    """Extract text by the path dictionary"""

    if isinstance(path_dict,dict):

        keys = path_dict.keys()
        result_dict = dict(zip(keys, [False]*len(keys)))
        selector = etree.HTML(resonse_text)

        for key,value in path_dict.iteritems():
            try:
                result_dict[key] = selector.xpath(value)[0].strip()
            except IndexError:
                pass
        return result_dict
    else:
        raise TypeError('Inappropriate argument type')
# end


def binaryzationImage(img_path):
    """ 图片二值化
    :param img_path: 图片的绝对路径
    :return: 二值化的图片流"""
    img = Image.open(img_path)
    # img = img.convert('L')
    pixdata = img.load()

    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            if pixdata[x, y][0] < 90:
                pixdata[x, y] = (0, 0, 0, 255)
        # for
    # for
    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            if pixdata[x, y][1] < 136:
                pixdata[x, y] = (0, 0, 0, 255)
        # for
    # for
    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            if pixdata[x, y][2] > 0:
                pixdata[x, y] = (255, 255, 255, 255)
        # for
    # for
    return img
# end


def saveImage(response, img_dire='code', img_name='', img_type='.jpg'):
    """ 保存图片
    :param response: request返回对象
    :param img_dire:  当前目录下的文件夹
    :param img_name:  图片文件名
    :param img_type: 图片格式
    :return: 图片的绝对路径 """
    path = os.path.join(os.getcwd(), img_dire)
    if not os.path.exists(path):
        os.mkdir(path)

    image_path = os.path.join(path, getUniqueFileName() + str(img_name) + img_type)
    with open(image_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):   #chunk_size=1024
            if chunk:
                f.write(chunk)
                f.flush()
    return image_path
# end


def removeAllFiles(dires):
    """ 删除指定目录的所有文件，异常则跳过
    :param dires: 目录列表
    :return: None """
    if not isinstance(dires, list):
        raise ValueError
    for dire in dires:
        for file in os.listdir(dire):
            try:
                os.remove(os.path.join(dire, file))
            except Exception:
                pass
# end


def clawLog(group, result, other=''):
    """ 在当前目录下的clawed_log目录下打log
    :param group: id列表
    :param result: 字符串统计结果
    :return: None"""
    dire = './clawed_log'
    if not os.path.exists(dire):
        os.mkdir(dire)

    log_name = strftime('%Y-%m-%d.%Hh',localtime()) + '.log' # 格式为：年-月-日.时h.log
    log_path = os.path.join(dire, log_name)
    with open(log_path, 'a') as f:
        f.write(time.ctime() + ':\t' + result + '\n' +  json.dumps(dict(sys_id=group)) + '\n'*2)
# end clawLog


def makeDirs(dirs=None):
    """ 在当前目录下创建目录
    :param dirs: list
    :return: None
    """
    if not dirs:
        dirs = ['clawed_log']
    current_dire = os.getcwd()
    for dir in dirs:
        abs_path = os.path.join(current_dire, dir)
        if not os.path.isdir(abs_path):
            os.mkdir(abs_path)
# end


if __name__ == '__main__':
    makeDirs()
    # print getUniqueFileName(2)
    # clawLog([1,2,3],'完成入库：有效信息1，错误信息49')