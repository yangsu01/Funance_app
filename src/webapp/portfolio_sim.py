from flask import Blueprint, render_template, request
from flask_login import current_user

from . import db
from .data_models import User, Portfolio, Holdings, Transactions

# constants
STARTING_FUNDS = 10000

sim = Blueprint('sim', __name__)

@sim.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        create_portfolio(current_user.id)
        print('hello this works')

    portfolio_exists = Portfolio.query.filter_by(user_id=current_user.id).first()

    return render_template("portfolio_sim/dashboard.html", user=current_user, username=current_user.username, portfolio_exists=portfolio_exists)

@sim.route('/rules', methods=['GET'])
def rules():

    return render_template("portfolio_sim/rules.html", user=current_user, starting_funds=STARTING_FUNDS)


def create_portfolio(user_id: int) -> None:
    '''Create a portfolio for a user
        args:
            user_id: int - database id of the user
    '''
    portfolio = Portfolio(user_id=user_id, available_cash=STARTING_FUNDS)

    db.session.add(portfolio)
    db.session.commit()

    return portfolio
