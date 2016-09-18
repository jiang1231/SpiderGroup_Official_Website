# -*- coding: utf-8 -*-
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Institution(db.Model):
    __tablename__ = 't_phone_book'

    id = db.Column(db.INT, primary_key=True, nullable=True)
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

