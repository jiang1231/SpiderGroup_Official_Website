#coding=utf-8
import sys
reload(sys)
sys.path.append('../')
sys.setdefaultencoding("utf-8")

import time,json,random,re

from lxml import etree
from selenium import webdriver
from selenium.common.exceptions import *


def searchPhoneInfoBySelenium(phone_num):  # 通过百度查询手机的归属地
    '''
    :param phone_num: phone number
    :return:dict(phone=XX, province=XX, city=XX, company=XX)/raise ValueError

    example:
        >>searchPhoneInfoBySelenium('15802028888')
        {'phone':'15802028888', 'province':'广东', 'city':'广州', 'company':'中国移动'}
    '''

    import re
    from selenium import webdriver
    from selenium.common.exceptions import NoSuchElementException

    time_wait_usual = 2

    browser = webdriver.Chrome()
    browser.get('https://www.baidu.com')
    browser.implicitly_wait(time_wait_usual)

    browser.find_element_by_id("kw" ).send_keys(phone_num)      # 定位输入框并输入内容
    browser.find_element_by_xpath('//input[@id="su"]').click()  # 定位百度一下按钮进行查询
    browser.implicitly_wait(time_wait_usual)

    try:
        text = browser.find_element_by_xpath('//div[@class="op_mobilephone_r"]').text
        browser.close()
    except (NoSuchElementException,AttributeError):
        return dict(result=False, error='phone number is invalid')
    else:
        phone = re.search('\d.*\d', text).group()

        if phone == phone_num:
            phone_info = dict()
            record = text.split()
            phone_info['phone'] = phone
            phone_info['province'] = record[1]
            phone_info['city'] = record[2]
            phone_info['company'] = record[3]
            return dict(result=True, info=phone_info)
        else:
            raise ValueError('demoSearchPhoneHome has error')
# end




def testGetCookies():

    import re
    from selenium import webdriver
    from selenium.common.exceptions import NoSuchElementException

    time_wait_usual = 2
    browser = webdriver.Chrome()
    browser.get('http://www.ahcredit.gov.cn/search.jspx')
    browser.implicitly_wait(time_wait_usual)

    print browser.get_cookies()
#



def test_searchPhoneInfoBySelenium():
# 测试"searchPhoneInfoBySelenium"函数

    s1 =time.time()
    result = searchPhoneInfoBySelenium('15802028888')
    print time.time() - s1
    if result['result']:
        for k,v in result['info'].items():
            print k,v
    else:
        print result
# end

# if __name__ == '__main__':
#     testGetCookies()

# a = '社保A岗曹青青1123454+56'
# ss = re.search('(\W+\w{0,2}\W+\w{0,2}\W+)(\d+[/+-]*\d+)',a)
# if ss:
#     print ss.group(1)
#     print ss.group(2)
a = '\xe8\xb4\xb5\xe5\xb7\x9e\xe7\x9c\x81'
print a