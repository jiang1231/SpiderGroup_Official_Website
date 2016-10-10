# coding=utf-8
import json
import sys
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for
from models import db, Institution, DishonestExecutor, ExecutedPerson
from sqlalchemy import distinct
from spider import zhixingSearchAPI
from spider import shixinSearchAPI
from operator_result_temp import result
from spider import  getPhoneAttr
from flask_script import Manager
from get_month import getMonthSeq
from spider import chinaUnicomAPI # 联通
from spider import getNoteCode, loginSys  # 移动

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost:3306/spider'
app.secret_key = 'spider'
# 工作MySql路径
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://pbb:pbb@123___@rm-wz9z97an1up0y6h7b.mysql.rds.aliyuncs.com:3306/spider'

app.config['DEBUG'] = True
db.init_app(app)
manager = Manager(app)

# 省份跟传过来的数字相匹配
MAPPED = {"660": u"北京", "661": u"天津", "662": u"河北", "663": u"山西", "664": u"内蒙古", "665": u"辽宁",
          "666": u"吉林", "667": u"黑龙江", "668": u"上海", "669": u"江苏", "670": u"浙江", "671": u"安徽",
          "672": u"福建", "673": u"江西", "674": u"山东", "675": u"河南", "676": u"湖北", "677": u"湖南",
          "678": u"广东", "679": u"广西", "680": u"海南", "681": u"重庆", "682": u"四川", "683": u"贵州",
          "684": u"云南", "685": u"西藏", "686": u"陕西", "687": u"甘肃", "688": u"青海", "689": u"宁夏",
          "690": u"新疆", "691": u"香港", "692": u"澳门", "693": u"台湾"}


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/check')
def check():
    """运营商查询页面"""
    return render_template('operators.html')


@app.route('/get_data_by_month/<date>')
def get_phone_data_by_month(date):
    '''
    获取最近6个月的记录 其中所有数据在登录的时候已经获取并存进了g变量
    :param month: 月份
    :return: 渲染后的结果
    '''
    phone_result = session["phone_result"]
    month_list = getMonthSeq()
    operator_call = filter(lambda a: a["call_date"].startswith(date), phone_result["t_operator_call"])
    operator_note = filter(lambda a: a["note_date"].startswith(date), phone_result["t_operator_note"])
    return render_template('operator_output.html', user=phone_result['t_operator_user'][0], month_list=month_list,
                           this_month=date,  operator_call=operator_call, operator_note=operator_note)


@app.route('/get_data_union/<number>/<password>')
def get_data_union(number, password):
    """暂时返回默认结果 operator_output.html result是外部导入 益华编的字典 """
    print 'in'
    session["phone_attr"]["password"] = password
    result = chinaUnicomAPI(session["phone_attr"])
    if result["code"] == 2000:
        session["phone_result"] = result["data"]
        date = datetime.now().strftime("%Y-%m")
        return redirect(url_for("get_phone_data_by_month", date=date))
    else:
        return '&' + result["desc"]


@app.route('/get_vcode')
def get_vcode():
    result = getNoteCode(session["phone_attr"])
    print result["code"]
    if result["code"] == 2000:
        session['result'] = result["temp"]
        print result["temp"]
        return u"验证码已经在路上"
    else:
        return result["desc"]


@app.route('/get_data_mobile/<number>/<password>/<vcode>')
def get_data_mobile(number, password, vcode):
    """暂时不用"""
    session["phone_obj"].phone_attr["password"] = password
    session["phone_obj"].phone_attr['phone_pwd'] = vcode
    login_result = loginSys(session["phone_obj"])
    if login_result['code'] == 2000:
        session['result'] = login_result['result']
        date = datetime.now().strftime("%Y-%m")
        return redirect(url_for("get_phone_data_by_month", date=date))
    else:

        return '&' + result["desc"]


@app.route('/check_phone_number/<number>')
def check_phone_number(number):
    """查询号码归属及类型api 其中getPhoneAttr是调用的查询脚本"""
    ret = getPhoneAttr(number)
    if ret['code'] == 2000:
        session["phone_attr"] = ret["data"]
        return json.dumps(ret['data'])
    else:
        return '&' + ret['desc']


@app.route('/institution')
def institution():
    """政府机构查询页面"""
    return render_template('government.html')


@app.route('/api/get_area', methods=['POST'])
def get_area():
    """根据前端传过来的参数查询相对应子地区并返回的api"""
    tp = request.form.get('type')
    name = request.form.get('name')
    if tp == 'province':
        i = db.session.query(distinct(Institution.province)).all()
    elif tp == 'city':
        i = db.session.query(distinct(Institution.city)).filter(Institution.province == name).all()
    elif tp == 'sub_city':
        i = db.session.query(distinct(Institution.sub_city)).filter(Institution.city == name).all()
    else:
        i = db.session.query(distinct(Institution.town_street)).filter(Institution.sub_city == name).all()
    return json.dumps(i)


@app.route('/get_mess', methods=['POST'])
def get_mess():
    """在数据库里查询政府机构的api"""
    province = request.form.get('province')
    city = request.form.get('city')
    sub_city = request.form.get('sub_city')
    if sub_city == None:
        sub_city = ''
    town_street = request.form.get('town_city')
    if town_street == None:
        town_street = ''
    content = request.form.get('content')
    if content:
        content = content.strip()
        i = Institution.query.filter(Institution.province == province, Institution.city == city,
                                     Institution.sub_city == sub_city, Institution.town_street == town_street,
                                     Institution.department.like('%{}%'.format(content))).all()
    else:
        i = Institution.query.filter_by(province=province, city=city, sub_city=sub_city, town_street=town_street).all()
    return render_template('government_output.html', institutions=i)


@app.route('/dishonest_check', methods=['GET', 'POST'])
def dishonest_check():
    """被执行人视图 GET直接返回查询页面 POST则分析并返回解析结果"""
    if request.method == 'POST':
        company_name = request.form.get('name')
        card_num = request.form.get('card_num') if request.form.get('card_num') else ''
        flag = int(request.form.get('flag'))
        province = '' if request.form.get('province') == '0' else MAPPED[request.form.get('province')]
        # 等待判断num是否为空，待处理
        if flag:
            if province:
                d = DishonestExecutor.query.filter(DishonestExecutor.name.like(
                    "{}%".format(company_name)), DishonestExecutor.card_num == card_num,
                    DishonestExecutor.area_name == province).all()
            else:
                d = DishonestExecutor.query.filter(DishonestExecutor.name.like(
                    "{}%".format(company_name)), DishonestExecutor.card_num == card_num).all()
        else:
            if len(card_num) == 18:
                card_num = card_num[:10] + "****" + card_num[14:]
            if province:
                d = DishonestExecutor.query.filter(DishonestExecutor.name.like(
                    "{}%".format(company_name)), DishonestExecutor.card_num == card_num,
                    DishonestExecutor.area_name == province).all()
            else:
                d = DishonestExecutor.query.filter(DishonestExecutor.name.like(
                    "{}%".format(company_name)), DishonestExecutor.card_num == card_num).all()
        if d:
            return render_template('dishonest_executor_output.html', DishonestExecutors=d)
        else:
            d = shixinSearchAPI(company_name, card_num)['data']
            print d
            if d and d['t_shixin_valid']:
                d = d['t_shixin_valid']
                return render_template('dishonest_executor_output.html', DishonestExecutors=d)
            else:
                return render_template('not_found_message.html')
    return render_template('dishonest_check.html')


@app.route('/dishonest_person', methods=['GET', 'POST'])
def dishonest_person():
    """执行人视图 GET直接返回查询页面 POST则分析并返回解析结果"""
    if request.method == 'POST':
        company_name = request.form.get('name')
        card_num = request.form.get('card_num') if request.form.get('card_num') else ''
        # 法院名称等待操作
        court = request.form.get('court')
        print court
        if len(card_num) >= 10:
            card_num = card_num[:10]
        d = ExecutedPerson.query.filter(ExecutedPerson.name.like(
            "{}%".format(company_name)), ExecutedPerson.card_num.ilike("%{}%".format(card_num))).all()
        if d:
            return render_template('dishonest_person_output.html', DishonestPeople=d)
        else:
            d = zhixingSearchAPI(company_name, card_num)['data']
            if d['t_zhixing_valid']:
                print d
                d = d['t_zhixing_valid']
                return render_template('dishonest_person_output.html', DishonestPeople=d)
            else:
                return render_template('not_found_message.html')
    return render_template('dishonest_person.html')

if __name__ == '__main__':
    manager.run()
