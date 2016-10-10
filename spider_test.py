#coding=utf-8
import time
from spider import getPhoneAttr
from spider import chinaUnicomAPI
# from spider import phonebookSpiderAPI
from spider import shixinSearchAPI, zhixingSearchAPI
from spider import getNoteCode, loginSys


def countTime(t_begin):
    pass


def descStatus():
    pass


# 测试-查询手机属性
def getPhoneAttr_Test():
    import time
    start = time.time()
    result = getPhoneAttr('15802027662')
    print 'api耗费时间为{0}秒'.format(time.time() - start )
    if result:
        for k,v in result.items():
            print k,v
    else:
        print 'api failed'
# end


# 测试-失信被执行人
def shixinSearchAPI_Test():
    t_begin = time.time()
    print time.ctime() + ':\t' + 'Test start, running'
    card_num = '72217220X'
    name = '遵义侨丰房地产开发有限责任公司'
    # card_num = ''
    # name = u'毛泽东'
    results = shixinSearchAPI(name, card_num)
    print time.ctime() + ':\t' + 'Test over, cost: {0} seconds\n\n'.format(time.time()-t_begin)
    print results
# end


# 测试-被执行人接口
def zhixingSearchAPI_Test():
    t_begin = time.time()
    print time.ctime() + ':\t' + 'Test start'
    card_num = '77535404-X'
    name = '漳州伟翔精密机械有限公司'
    # card_num = ''
    # name = '何计通'
    results = zhixingSearchAPI(name, card_num)
    print time.ctime() + ':\t' + 'Test over, cost: {0} seconds\n'.format(time.time()-t_begin)
    print results
# end


# 测试-政府联络方式
def phonebookSpiderAPI_Test():
    pass
    # phonebookSpiderAPI()
# end


# 测试-联通接口
def chinaUnicomAPI_Test():
    t_begin = time.time()
    attr = getPhoneAttr('13267175437')
    if attr['code'] == 2000:
        phone_attr = attr['data']
        phone_attr['password'] = 'moyihua251314'
        result = chinaUnicomAPI(phone_attr)
        for item in result.items():
            print item
    else:
        print '无法查询号码的归属信息,bye!'
    print u'整个流程耗费用时:{0}'.format(time.time()-t_begin)
# end


# 测试-移动接口
def chinaMobileAPI_Test():
    attr = getPhoneAttr('15802027662')
    if attr['code'] == 2000:
        phone_attr = attr['data']
        phone_attr['password'] = 'xxxxx'  # 添加密码
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


if __name__ == '__main__':
    # pass
    # getPhoneAttr_Test() #查询手机属性
    chinaUnicomAPI_Test()  #中国联通
    # shixinSearchAPI_Test() #失信被执行人
    # zhixingSearchAPI_Test() #被执行人

