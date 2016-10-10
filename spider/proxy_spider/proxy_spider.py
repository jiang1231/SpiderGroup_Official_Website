#coding=utf-8
import re
import gevent
import requests

from lxml import etree
from public import basicRequest
from requests.exceptions import *
from gevent import monkey; monkey.patch_all()

_timeout = 5
_vaild_proxies = list()


def getProxies():
    """ http://www.youdaili.net/
    :return:
    """
    options = {'method':'get', 'url':'http://www.youdaili.net/'}
    response = basicRequest(options)
    if not response:
        return False

    path = '//div[@class="m_box2"][1]/ul/li[1]/a/@href'
    href = etree.HTML(response.content).xpath(path)
    if not href:
        return False

    options = {'method':'get', 'url':href[0]}
    response = basicRequest(options)
    path = '//div[@class="cont_font"]/p/span/text()'

    result = [i.lstrip('\r\n') for i in etree.HTML(response.content).xpath(path)]
    proxies = [re.search('(.*)\@',i).group(1) for i in result[:-1]]
    return proxies
# end


def testProxy(proxy=None):

    proxies = {'http':proxy, 'https':proxy}
    # url = 'https://tcc.taobao.com/cc/json/mobile_tel_segment.htm?tel=15850781443' # 手机归属地API
    url = 'https://www.baifubao.com/callback?cmd=1059&callback=phone&phone=15850781443'
    try:
        requests.get(url, timeout=_timeout, proxies=proxies, verify=False)
        _vaild_proxies.append(proxy)
    except (Timeout,ProxyError,SSLError,Exception):
        pass

# end


def getVaildProxiesAPI(timeout):

    global _timeout
    _timeout = timeout

    results = getProxies()
    if isinstance(results, list) and results:
        objs = []
        for proxy in results:
            objs.append(gevent.spawn(testProxy, proxy))
        gevent.joinall(objs)

    return _vaild_proxies
# end


if __name__ == '__main__':
    import time
    t_begin = time.time()
    print getVaildProxiesAPI(2)
    print time.time()-t_begin
