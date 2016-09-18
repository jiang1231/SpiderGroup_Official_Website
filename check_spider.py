# coding=utf-8
from flask import Flask, render_template, request
# from flask.ext.moment import Moment
from china_unicom.china_unicom_search import chinaUnicomAPI
from models import db, Institution
from sqlalchemy import distinct
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost:3306/spider'
db.init_app(app)

# moment = Moment(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check')
def check():
    return render_template('check.html')


@app.route('/get_data/<number>/<password>')
def get_data(number, password):
    r = chinaUnicomAPI(number, password)
    try:
        r['t_china_unicom_uesr']
    except KeyError:
        return 'error'

    return render_template('output.html', user=r['t_china_unicom_uesr'][0])


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
    print content
    if content:
        content = content.strip()
        print content
        i = Institution.query.filter(Institution.province==province,
                                     Institution.city==city, Institution.sub_city==sub_city,
                                     Institution.town_street==town_street, Institution.department.like('%{}%'.format(content))).all()
    else:
        i = Institution.query.filter_by(province=province, city=city, sub_city=sub_city, town_street=town_street).all()
    # print i
    return render_template('government_output.html', institutions=i)

if __name__ == '__main__':
    app.run(debug=True)
