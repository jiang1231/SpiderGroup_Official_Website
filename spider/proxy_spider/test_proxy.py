from requests.utils import dict_from_cookiejar
from proxy_spider import  getVaildProxiesAPI


url = 'http://shixin.court.gov.cn/'

from requests import get, ReadTimeout,ConnectTimeout,Timeout, ConnectionError


def testProxy(proxy):

    proxies = {'http':proxy, 'https':proxy}
    try:
        response = get(url, proxies=proxies, timeout=3)
    except (ReadTimeout, ConnectTimeout, Timeout):
        pass
    except ConnectionError:
        pass
    else:
        if response:
            print dict_from_cookiejar(response.cookies)
# end

proxies = getVaildProxiesAPI(2)
for proxy in proxies:
    for i in range(100):
        testProxy(proxy)