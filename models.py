# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Institution(db.Model):
    __tablename__ = 't_phone_book'

    id = db.Column(db.Integer, primary_key=True)
    alter_time = db.Column(db.DateTime)
    province = db.Column(db.String(64))
    city = db.Column(db.String(64))
    sub_city = db.Column(db.String(64))
    town_street = db.Column(db.String(64))
    department = db.Column(db.String(124))
    tel_num = db.Column(db.String(32))

    def show(self):
        return u'{} {} {} {} {} {} {}'.format(self.alter_time, self.province, self.city, self.sub_city,
                                              self.town_street, self.department, self.tel_num)
    def __repr__(self):
        return '<Institution {}>'.format(self.department)


class DishonestExecutor(db.Model):
    __tablename__ = 't_shixin_valid'

    id = db.Column(db.Integer, primary_key=True)
    alter_time = db.Column(db.DateTime)
    sys_id = db.Column(db.INT)
    name = db.Column(db.String(128))
    age = db.Column(db.String(8), nullable=True)
    sex = db.Column(db.String(8), nullable=True)
    card_num = db.Column(db.String(64))
    business_entity = db.Column(db.String(64), nullable=True)
    area_name = db.Column(db.String(64))
    case_code = db.Column(db.String(128))
    reg_date = db.Column(db.String(128))
    publish_date = db.Column(db.String(128))
    gist_id = db.Column(db.String(128))
    court_name = db.Column(db.String(128))
    gist_unit = db.Column(db.String(128))
    duty = db.Column(db.Text)
    performance = db.Column(db.String(128), nullable=True)
    disrupt_type_name = db.Column(db.String(128), nullable=True)
    party_type_name = db.Column(db.String(128), nullable=True)
    flag = db.Column(db.SmallInteger)

    def __repr__(self):
        return '<DishonestExecutor {}>'.format(self.id)


class ExecutedPerson(db.Model):
    __tablename__ = 't_zhixing_valid'

    id = db.Column(db.Integer, primary_key=True)
    alter_time = db.Column(db.DateTime)
    sys_id = db.Column(db.Integer)
    name = db.Column(db.String(128))
    card_num = db.Column(db.String(64))
    case_code = db.Column(db.String(128))
    reg_date = db.Column(db.String(128))
    court_name = db.Column(db.String(128))
    execute_money = db.Column(db.String(64))

    def __repr__(self):
        return '<DishonestExecutor {}>'.format(self.name)


