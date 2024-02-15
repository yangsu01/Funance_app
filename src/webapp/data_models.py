from flask_login import UserMixin
from sqlalchemy.sql import func

from . import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    creation_date = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    # one to one
    portfolio = db.relationship('Portfolio', backref='user', lazy=True)


class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    available_cash = db.Column(db.Float, nullable=False)
    creation_date = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    # one to many
    holdings = db.relationship('Holdings', backref='portfolio', lazy=True)
    transactions = db.relationship('Transactions', backref='portfolio', lazy=True)


class Holdings(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    shares = db.Column(db.Integer, nullable=False)
    average_price = db.Column(db.Float, nullable=False)
    updated_price = db.Column(db.Float, nullable=False)
    updated_time = db.Column(db.DateTime(timezone=True), nullable=False)


class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    currency = db.Column(db.String(5), nullable=False)
    shares = db.Column(db.Integer, nullable=False)
    share_price = db.Column(db.Float, nullable=False)
    total_value = db.Column(db.Float, nullable=False)

