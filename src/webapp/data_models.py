from flask_login import UserMixin
from sqlalchemy.sql import func

from . import db


# registered users
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    creation_date = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    # one to one
    portfolio = db.relationship('Portfolio', back_populates='user', uselist=False, cascade='all, delete-orphan')


# user's investment portfolio
class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    available_cash = db.Column(db.Float, nullable=False)
    creation_date = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    updated_value = db.Column(db.Float, nullable=False)
    updated_time = db.Column(db.DateTime(timezone=True), nullable=False)

    # one to one
    user = db.relationship('User', back_populates='portfolio')

    # one to many
    holdings = db.relationship('Holdings', backref='portfolio', lazy=True)
    transactions = db.relationship('Transactions', backref='portfolio', lazy=True)
    history = db.relationship('History', backref='portfolio', lazy=True)


# individual stock holdings in portfolios
class Holdings(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    shares = db.Column(db.Integer, nullable=False)
    average_price = db.Column(db.Float, nullable=False)
    updated_price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(5), nullable=False)
    open_price = db.Column(db.Float, nullable=False)
    open_price_date = db.Column(db.Date, nullable=False) #new column


# transactions history
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


# history of portfolio values
class History(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    portfolio_value = db.Column(db.Float, nullable=False)


