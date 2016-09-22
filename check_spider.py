# coding=utf-8
import json
from flask import Flask, render_template, request
# from flask.ext.moment import Moment
from models import db, Institution, DishonestExecutor, ExecutedPerson
from sqlalchemy import distinct
# from china_unicom.china_unicom_search import chinaUnicomAPI
from zhixing_spider.zhixing_search import zhixingSearchAPI
from shixin_spider.shixin_search import shixinSearchAPI
from operator_result_temp import result
from phone_attr import getAttributes
from flask.ext.script import Manager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost:3306/spider'
db.init_app(app)
manager = Manager(app)

# moment = Moment(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check')
def check():
    return render_template('operators.html')


@app.route('/get_data_union/<number>/<password>')
def get_data_union(number, password):
    # r = chinaUnicomAPI(number, password)
    # try:
    #     r['t_china_unicom_uesr']
    # except KeyError:
    #     return 'error'
    # print result['t_operator_user']
    return render_template('operator_output.html', user=result['t_operator_user'][0],
                           operator_call=result['t_operator_call'], operator_note=result['t_operator_note'])


@app.route('/get_data_mobile/<number>/<password>/<vcode>')
def get_data_mobile(number, password, vcode):
    # r = chinaUnicomAPI(number, password)
    # try:
    #     r['t_china_unicom_uesr']
    # except KeyError:
    #     return 'error'
    #
    # return render_template('output.html', user=r['t_china_unicom_uesr'][0])
    return "{} {} {}".format(number, password, vcode)


@app.route('/check_phone_number/<number>')
def check_phone_number(number):
    ret = getAttributes(number)
    return json.dumps(ret)


@app.route('/institution')
def institution():
    # i = db.session.query(distinct(Institution.city)).filter(Institution.province==u'广东省').all()
    # i = Institution.query.filter_by(province=u'上海市').distinct().all()
    return render_template('government.html')


@app.route('/api/get_area', methods=['POST'])
def get_area():
    # data = json.loads(unicode(request.data))
    # print request.form
    tp = request.form.get('type')
    name = request.form.get('name')
    if tp == 'province':
        i = db.session.query(distinct(Institution.province)).all()
    elif tp == 'city':
        i = db.session.query(distinct(Institution.city)).filter(Institution.province == name).all()
    elif tp == 'sub_city':
        i = db.session.query(distinct(Institution.sub_city)).filter(Institution.city == name).all()
    elif tp == 'town_street':
        i = db.session.query(distinct(Institution.town_street)).filter(Institution.sub_city == name).all()
    return json.dumps(i)


@app.route('/get_mess', methods=['POST'])
def get_mess():
    province = request.form.get('province')
    city = request.form.get('city')
    sub_city = request.form.get('sub_city')
    if sub_city == None:
        sub_city = ''
    town_street = request.form.get('town_city')
    if town_street == None:
        town_street = ''
    content = request.form.get('content')
    # print content
    if content:
        content = content.strip()
        # print content
        i = Institution.query.filter(Institution.province==province,
                                     Institution.city==city, Institution.sub_city==sub_city,
                                     Institution.town_street==town_street, Institution.department.like('%{}%'.format(content))).all()
    else:
        i = Institution.query.filter_by(province=province, city=city, sub_city=sub_city, town_street=town_street).all()
    # print i
    return render_template('government_output.html', institutions=i)


@app.route('/dishonest_check', methods=['GET', 'POST'])
def dishonest_check():
    if request.method == 'POST':
        # return render_template('not_found_message.html')
        company_name = request.form.get('name')
        card_num = request.form.get('card_num') if request.form.get('card_num') else ''
        flag = int(request.form.get('flag'))
        if flag:
            d = DishonestExecutor.query.filter(DishonestExecutor.name.like(
                "{}%".format(company_name)), DishonestExecutor.card_num.ilike("%{}%".format(card_num))).all()
        else:
            if len(card_num) == 18:
                card_num = card_num[:10] + "****" + card_num[14:]
            # print 'in'
            d = DishonestExecutor.query.filter(DishonestExecutor.name.like(
                "{}%".format(company_name)), DishonestExecutor.card_num.ilike("%{}%".format(card_num))).all()
        # print '{} {} {}'.format(d.name, d.card_num, d.flag)
        if d:
            return render_template('dishonest_executor_output.html', DishonestExecutors=d)
        else:
            d = shixinSearchAPI(company_name, card_num)
            print d
            if d['t_shixin_valid']:
                d = d['t_shixin_valid']
                return render_template('dishonest_executor_output.html', DishonestExecutors=d)
            else:
                return render_template('not_found_message.html')
    return render_template('dishonest_check.html')


@app.route('/dishonest_person', methods=['GET', 'POST'])
def dishonest_person():
    if request.method == 'POST':
        company_name = request.form.get('name')
        card_num = request.form.get('card_num') if request.form.get('card_num') else ''
        # print len(card_num), card_num
        if len(card_num) >= 10:
            # card_num = card_num[:10] + "****" + card_num[15:]
            card_num = card_num[:10]
            # print card_num
            # d = ExecutedPerson.query.filter(ExecutedPerson.name.ilike(
            #     "{}%".format(company_name)), ExecutedPerson.card_num == card_num).all()
        # else:
        d = ExecutedPerson.query.filter(ExecutedPerson.name.like(
            "{}%".format(company_name)), ExecutedPerson.card_num.ilike("%{}%".format(card_num))).all()
        # print '{} {} {}'.format(d.name, d.card_num, d.flag)
        if d:
            return render_template('dishonest_person_output.html', DishonestPeople=d)
        else:
            d = zhixingSearchAPI(company_name, card_num)
            # print d
            if d['t_zhixing_valid']:
                print d
                d = d['t_zhixing_valid']
                return render_template('dishonest_person_output.html', DishonestPeople=d)
            else:
                return render_template('not_found_message.html')
    return render_template('dishonest_person.html')

if __name__ == '__main__':
    manager.run()
