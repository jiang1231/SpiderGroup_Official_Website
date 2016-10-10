#coding=utf-8
import json
from spider.public import basicRequest,returnResult


def checkParamFormat(phone_num, password):
    """ 手机号、密码格式的检查
    :param phone_num: 手机号
    :param password: 密码
    :return:
    """
    if isinstance(phone_num, str) and isinstance(password, str):
        if len(phone_num) < 11 or len(password) < 6:
            return dict(result=1001, error="parameter's length error")
        else:
            return True
    else:
        return dict(result=1000, error="parameter's type error")
# end


_company_convert = {
    u'中国联通': 1,
    u'中国移动': 2,
    u'中国电信': 3
}

def getPhoneAttr(phone_num):
    """ 调用百度api获得手机的归属地
    :param phone_num: 手机号
    :return:统一接口返回
    example:
        >>searchPhoneInfo('15802028888')
        正常返回key data对应的元素例子
        {'phone':'13267175437', 'province':'广东', 'city':'深圳', 'company':1}
        company值:中国联通1; 中国移动2; 中国电信3, 其他4
    """
    phone_status = 6855 if str(phone_num)[0] == '0' else 6004
    url = 'https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php'
    params = {'query':phone_num, 'resource_id': phone_status}
    options = {'method': 'get', 'url': url, 'params': params}

    response = basicRequest(options)
    if response:
        try:
            company_type = 4
            item = json.loads(response.text)['data'][0]
            if item['type'] in _company_convert.keys():
                company_type =  _company_convert[item['type']]
            data = {
                'phone': phone_num,
                'province': item['prov'],
                'city': item['city'],
                'company': company_type
            }
            return returnResult(code=2000, data=data, desc=u'查询成功')
        except (KeyError, IndexError):
            return returnResult(code=4500, data={})
        except (ValueError, Exception):
            return returnResult(code=4100, data={})
    else:
        return returnResult(code=4000, data={})
# end


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

if __name__ == '__main__':
    getPhoneAttr_Test()