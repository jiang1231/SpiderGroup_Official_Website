#coding=utf-8
import sys
import re,os
reload(sys)
from lxml import etree
sys.setdefaultencoding("utf-8")

def queryRecord(selector):
    '''机构/个人查询记录明细'''

    query_results = list()
    item_query_keys = ('query_id', 'query_time', 'query_operator', 'query_reason')

    agency_query_table = '//div[@align="center"]/div/table/tr[2]/td/table[7]'
    # agency_query_table = '//table[@width="980" and @border="0" and @align="center"' \
    #                     ' and @cellspacing="0" and @style="margin-top: 12px"]'
    try:
        table = selector.xpath(agency_query_table)[0]
        trs = table.xpath('tbody/tr')[3:-1]
        for tr in trs:
            result = list()
            row =  tr.xpath('td/text()')
            for attr in row:
                result.append(attr.strip())

            item_query = dict(zip(item_query_keys,result))
            item_query['type'] = 1  # 1 means agency's query

            query_results.append(item_query)

    except IndexError:
        pass
    except UnicodeEncodeError:
        pass


    person_query_table = '//div[@align="center"]/div/table/tr[2]/td/table[8]'

    try:
        table = selector.xpath(person_query_table)[0]
        trs = table.xpath('tbody/tr')[3:-1]
        for tr in trs:
            result = list()
            row =  tr.xpath('td/text()')
            for attr in row:
                result.append(attr.strip())

            item_query = dict(zip(item_query_keys,result))
            item_query['type'] = 0  # 0 means personal query

            query_results.append(item_query)

    except IndexError:
        pass
    except UnicodeEncodeError:
        pass

    return query_results
# end


def creditCardRecode(selector):
    '''信用卡账户明细'''

    card_results = list()
    item_card = dict()

    path = '//ol[@class="p olstyle"]/li/text()'
    try:
        results = selector.xpath(path)

        for text in results:
            text = str(text).strip()
            item_card['release_date'] = re.search(r'(^2.*日)', text).group(1)     # 2016年3月29日
            item_card['bank'] = re.search(r'日(.*)发',text).group(1)              # 广州银行
            item_card['card_type'] = re.search(r'的(.*卡)',text).group(1)         # 贷记卡
            item_card['account_type'] = re.search(r'\（(.*)\）',text).group(1)    # 人民币账户
            item_card['due_date'] = re.search(r'截至(.*月)',text).group(1)        # 2016年5月
            item_card['credit_amount'] = re.search(r'信用额度(.*)，',text).group(1)   # 17,000
            item_card['used_amount'] = re.search(r'已使用额度(.*)。',text).group(1)    # 2,214

            card_results.append(item_card)

    except (IndexError,AttributeError):
        pass
    except UnicodeEncodeError:
        pass

    return card_results
# end


def personBasicRecord(selector):
    '''时间/个人基本信息'''

    report_date = dict()
    item_date_keys = ('report_id', 'query_time', 'report_time')
    report_date_path = '//div[@align="center"]/div/table/tr[2]/td/table[1]/tbody/tr[2]/td/strong/text()'

    try:
        results = selector.xpath(report_date_path)
        for index,value in enumerate(results):
            report_date[item_date_keys[index]] = re.search(r'\d.*\d', str(value).strip()).group()
    except IndexError:
        pass

    person_info = dict()
    person_info_path = '//div[@align="center"]/div/table/tr[2]/td/table[2]/tbody/tr/td/strong/text()'
    try:
        results = selector.xpath(person_info_path)
        if len(results) == 4:
            person_info['name'] = str(results[0]).strip().lstrip('姓名： ')
            person_info['id_type'] = str(results[1]).strip().lstrip('证件类型：')
            person_info['id_card'] = str(results[2]).strip().lstrip('证件号码：')
            person_info['marriage'] = str(results[3]).strip()
        else:
            pass
    except IndexError:
        pass

    return dict(report_date, **person_info)
# end


def clawCreditReport(selector=None, html=None):
    '''调用入口'''

    if isinstance(selector, etree._Element):
        person_results = personBasicRecord(selector)
        card_results = creditCardRecode(selector)
        query_results = queryRecord(selector)
        return dict(person_results = person_results, card_results=card_results, query_results=query_results)

    elif os.path.exists(html):
        with open(html, 'r') as f:
            text = f.read()
        return clawCreditReport(selector=etree.HTML(text))

    else:
        raise TypeError('Parameter type error')
# end


def demoTest1():
    html = 'E:\html\person_credit\wu.html'
    result = clawCreditReport(html=html)
    print 'wait'

if __name__ == '__main__':
    demoTest1()