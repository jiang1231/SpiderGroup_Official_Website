#coding=utf-8
import time

_time_wait_usual = 200

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


    # browser = webdriver.PhantomJS(r'C:\driver\phantomjs-2.1.1-windows\bin\phantomjs.exe')
    browser = webdriver.Chrome(r'C:\driver\chromedriver.exe')
    browser.get('https://www.baidu.com')
    browser.implicitly_wait(_time_wait_usual)

    browser.find_element_by_id("kw" ).send_keys(phone_num)      # 定位输入框并输入内容
    browser.find_element_by_xpath('//input[@id="su"]').click()  # 定位百度一下按钮进行查询
    browser.implicitly_wait(_time_wait_usual)

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

if __name__ == '__main__':
    test_searchPhoneInfoBySelenium()