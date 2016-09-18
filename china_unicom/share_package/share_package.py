#coding=utf-8
import json
from china_unicom.public.share_func import basicRequest


def checkParamFormat(phone_num, password):
    '''
    :param phone_num: 手机号
    :param password: 密码
    :return:
    '''
    if isinstance(phone_num, str) and isinstance(password, str):
        if len(phone_num) < 11 or len(password) < 6:
            return dict(result=1001, error="parameter's length error")
        else:
            return True
    else:
        return dict(result=1000, error="parameter's type error")
# end


def searchPhoneInfo(phone_num):
    ''' 调用百度api获得手机的归属地
    :param phone_num: 手机号
    :return:dict(phone=XX, province=XX, city=XX, company=XX)/raise ValueError

    example:
        >>searchPhoneInfo('15802028888')
        {'phone':'15802028888', 'province':'广东', 'city':'广州', 'company':'中国移动'}
    '''
    phone_status = 6855 if str(phone_num)[0] == '0' else 6004
    url = 'https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php'
    params = {'query':phone_num, 'resource_id':phone_status}
    options = {'method':'get','url':url,'params':params}

    response = basicRequest(options)
    if response:
        try:
            item = json.loads(response.text, encoding='utf-8')['data'][0]

            return dict(
                phone = phone_num,
                province = item['prov'],
                city = item['city'],
                company = item['type'],
            )
        except (ValueError,KeyError,IndexError,Exception):
            return False
    else:
        return False
# end


def test_searchPhoneInfo():
    import time
    start = time.time()
    result = searchPhoneInfo('13267175437')
    print 'api耗费时间为{0}秒'.format(time.time() - start )
    if result:
        for k,v in result.items():
            print k,v
    else:
        print 'api failed'
# end

if __name__ == '__main__':
    test_searchPhoneInfo()